---
name: publish-to-web
description: Publish local HTML (a single file or a folder of static assets) to a live public URL by pushing to a GitHub repo and deploying to Cloudflare (default), Netlify, Vercel, or GitHub Pages. Optional shared-password gate. Use when the user asks to "publish", "deploy", "put this HTML online", "get a live link", "host this page", or "ship this site". Static sites only (HTML/CSS/JS/images) — not server-side apps.
---

# Publish local HTML to the web

Turn a local HTML file or static-site folder into a live public URL. Default host is **Cloudflare (Workers static assets)**, deployed **CLI-first** with a **GitHub repo** as the source of truth so a Git-connected build can auto-deploy on every push.

Publishing is an outward-facing, hard-to-reverse action (content becomes public and may be cached/indexed). **Confirm source, repo name, visibility, host, and whether a password is needed before the first deploy** unless the user has said to go ahead.

> Why Workers, not Pages: Cloudflare's dashboard "Connect to Git" now creates a **Workers Build** (`npx wrangler deploy` + `assets.directory`), not a Pages project. Pages `functions/_middleware.js` does NOT run under Workers. Build around Workers static assets from the start to avoid a mid-job rewrite. Pages still works via `wrangler pages deploy`, but treat it as the fallback.

## 0. Preflight — toolchain

```powershell
git --version
gh --version; gh auth status     # GitHub CLI (optional; not required if repo already exists)
npx wrangler --version           # Cloudflare (via npx, no global install needed)
```
- `git` is required. `gh` is only needed to *create* a repo; if the user already made one, plain `git` + cached credentials is enough (`gh` is often not installed).
- Interactive logins must be run by the user with the `! ` prefix so output lands in the session: `! npx wrangler login` (Cloudflare), `! gh auth login` (GitHub).
- Work in a clone OUTSIDE any OneDrive/Dropbox-synced folder to avoid `.git` sync corruption.

## 1. Stage the source

- Site root must serve **`index.html`**. If the user points at `page.html`, copy it to `index.html` in a staging dir. **Never mutate the user's original** — copy it.
- Rewrite any absolute `C:\...` / `file://` refs to relative paths.
- **Size check (Cloudflare hard limit: 25 MiB per file).** Self-contained dashboards that inline images as base64 routinely exceed this. If `index.html` > ~24 MiB, externalise the inlined images to separate files (see Gotcha A) before deploying.
- `.gitignore`: `node_modules/`, `.env`, `.DS_Store`, **`.wrangler/`** (never commit the wrangler cache — it also gets served if it lands in the assets dir).

## 2. GitHub repo (source of truth)

```powershell
cd <site-root>
git init -b main; git add -A; git commit -m "Initial site"
gh repo create <name> --private --source=. --remote=origin --push   # if gh present
# else: git remote add origin <url>; git push -u origin main
```
Default `--private`. Report the repo URL.

## 3. Deploy — Cloudflare Workers static assets (default)

Put a site subfolder per project (e.g. `p3575/`) so one repo can host several sites. Repo layout:
```
<repo>/
  wrangler.jsonc      # name, main, assets.directory (relative to repo root)
  worker.js           # only if a password gate / custom logic is needed; else omit `main`
  <site>/index.html   # + assets/, etc.
```

`wrangler.jsonc` (no-auth static site):
```jsonc
{
  "name": "<project-name>",
  "compatibility_date": "2026-07-08",
  "assets": { "directory": "<site>" }
}
```
Deploy and capture the printed URL (`https://<name>.<account>.workers.dev`):
```powershell
npx wrangler deploy
```
- The `workers.dev` URL is always `<worker-name>.<account-subdomain>.workers.dev` — the account subdomain cannot be removed; only a custom domain drops it (see step 5).
- **Git-connected auto-deploy:** dashboard → Workers & Pages → Create → Workers → Connect to Git → pick repo. It runs `npx wrangler deploy` on each push. Committing your own `wrangler.jsonc` stops it auto-generating one. This connection is dashboard-only (GitHub OAuth); wrangler cannot wire it.

### Optional: shared-password gate (cookie-based)
Prefer a **cookie login over HTTP Basic Auth** — Basic Auth on image/subresource requests is silently stripped by some browsers and corporate proxies (symptom: page loads but all images fail). Cookies are sent on every request.

`wrangler.jsonc` gains a worker that runs before assets:
```jsonc
{
  "name": "<project-name>",
  "compatibility_date": "2026-07-08",
  "main": "worker.js",
  "assets": { "directory": "<site>", "binding": "ASSETS", "run_worker_first": true }
}
```
`worker.js` — login form sets an HttpOnly cookie; cookie then authorises everything; Basic Auth kept as a curl fallback; HTML served `no-cache` so redeploys show without a hard refresh:
```js
const DEFAULT_PASSWORD = "CHANGE_ME";
const COOKIE = "site_auth";
async function tokenFor(pw){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode("s|"+pw));return[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");}
async function serveAsset(req,env){const r=await env.ASSETS.fetch(req);if((r.headers.get("Content-Type")||"").includes("text/html")){const h=new Headers(r.headers);h.set("Cache-Control","no-cache");return new Response(r.body,{status:r.status,headers:h});}return r;}
function login(msg){return new Response(`<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Sign in</title><body style="margin:0;height:100vh;display:grid;place-items:center;background:#0b0c0e;color:#eee;font-family:sans-serif"><form method=POST action=/__auth style="width:320px;padding:32px;background:#141619;border:1px solid #26292e;border-radius:12px">${msg?`<p style="color:#e5736b">${msg}</p>`:""}<input type=password name=password placeholder=Password autofocus style="width:100%;box-sizing:border-box;padding:12px;margin-bottom:12px;background:#0b0c0e;border:1px solid #33373d;border-radius:8px;color:#fff"><button style="width:100%;padding:12px;border:0;border-radius:8px;background:#c8a34a;font-weight:600;cursor:pointer">Enter</button></form>`,{status:401,headers:{"Content-Type":"text/html;charset=utf-8","Cache-Control":"no-store"}});}
export default { async fetch(request, env) {
  const expected = (env && env.SITE_PASSWORD) || DEFAULT_PASSWORD;
  const token = await tokenFor(expected);
  const url = new URL(request.url);
  if (request.method === "POST" && url.pathname === "/__auth") {
    const f = await request.formData();
    if ((f.get("password")||"") === expected) return new Response(null,{status:303,headers:{"Location":"/","Set-Cookie":`${COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=86400`}});
    return login("Incorrect password.");
  }
  if ((request.headers.get("Cookie")||"").split(/;\s*/).includes(`${COOKIE}=${token}`)) return serveAsset(request, env);
  const a = request.headers.get("Authorization")||"";
  if (a.startsWith("Basic ")) { try { const d=atob(a.slice(6)); if (d.slice(d.indexOf(":")+1)===expected) return serveAsset(request, env); } catch(e){} }
  return login();
}};
```
Set the password via `SITE_PASSWORD` in the dashboard (Settings → Variables) to keep it out of the repo, or the hardcoded default if the repo is private and the gate is only light.

### Fallback: Cloudflare Pages
`npx wrangler pages deploy <site> --project-name=<name>` → `https://<name>.pages.dev`. Pages accepts a `functions/_middleware.js` gate and an external-CNAME custom domain, BUT: **run `wrangler pages deploy` from INSIDE the folder that contains `functions/`** — wrangler resolves `functions/` relative to the cwd, not the deployed dir, and silently skips it otherwise (no "Compiled Worker" line = the gate did not deploy).

### Other hosts
- **Netlify:** `npx netlify-cli deploy --dir=<site> --prod` → `*.netlify.app`. `netlify init` connects GitHub.
- **Vercel:** `npx vercel --cwd <site> --prod --yes` → `*.vercel.app`.
- **GitHub Pages** (no third-party account; repo must be public on free tier): Settings → Pages → Source `main`/root → `https://<user>.github.io/<repo>/`. Higher per-file limit than Cloudflare but no built-in auth.

## 4. Verify (do not claim success without this)
```powershell
$h = @{ Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("u:<password>")) }  # if gated
(Invoke-WebRequest "<url>/" -Headers $h -UseBasicParsing).StatusCode                     # expect 200 (or 401 with no creds)
```
- If gated: confirm no-auth → 401, correct password → 200.
- Fetch `index.html` and confirm byte size / `<title>` match the source.
- Spot-check assets return 200. For an **interactive dashboard, open it in a browser (Playwright) and check images actually render** — server 200 is necessary but not sufficient (see Gotcha B).
- Never fabricate a URL; report only the one the deploy printed.

## 5. Custom domain
- **Workers:** the domain's DNS **zone must be on the user's Cloudflare account** (external CNAME does NOT work, unlike Pages). Once the zone is on Cloudflare, add to `wrangler.jsonc`: `"routes":[{"pattern":"dash.example.com","custom_domain":true}]` then `wrangler deploy`. If the user's main domain lives elsewhere, register a spare domain via Cloudflare Registrar or move a domain's nameservers to Cloudflare first.
- **Pages:** accepts a plain external CNAME to `<name>.pages.dev` — no zone move needed.

## Gotchas (hard-won)

**A. 25 MiB per-file limit / externalising inlined images.** Extract every `data:<mime>;base64,<payload>` to a file and rewrite the reference to a relative path (dedupe identical payloads by hash; pick extension from the mime). This can turn a 30 MB HTML into ~6 MB HTML + separate image files. Keep the extraction script so it can be re-run when the source is regenerated. Regex on the raw text catches data-URIs in HTML attrs, CSS `url()`, and JS strings — but NOT base64 assembled at runtime by JS concatenation (those stay inline and are fine).

**B. `blob:` / dynamically-built iframes.** If the page builds an iframe via `URL.createObjectURL(new Blob([html],{type:'text/html'}))`, **relative URLs inside it do not resolve** (only absolute URLs work); root-relative `/x` also fails. Externalising that iframe's images breaks them all. Fix: inject `<base href="${location.origin}/">` into the iframe HTML before blob creation (domain-independent). `srcdoc` iframes are fine — relative paths resolve against the parent origin.

**C. Auth + subresources.** HTTP Basic Auth can be stripped from subresource requests by browsers/proxies → document loads but images 401. Use the cookie gate above.

**D. Assets dir hygiene.** `wrangler deploy` uploads EVERYTHING under `assets.directory`. Keep `.wrangler/`, source scripts, and stray files out of it or they get served.

**E. Stale HTML.** Cloudflare/browsers heuristically cache HTML with no `Cache-Control`. Serve HTML `no-cache` (worker snippet does this) or the user sees old versions and blames the deploy. When testing yourself, cache-bust with a `?v=<n>` query.

**F. Renaming a worker** referenced by a Workers Build changes its `workers.dev` URL and can orphan the old worker — clean up old workers/Pages projects with `wrangler delete --name <old>` / `wrangler pages project delete <old>`.

$ARGUMENTS
