# Third-Party Notices

This repository vendors the third-party skills listed below. Each remains under its upstream licence; nothing in this repo's own MIT `LICENSE` re-licenses them. Vendored copies are as installed from upstream, unmodified.

| Directory | Upstream | Licence | Copyright |
|---|---|---|---|
| `skills/agents-sdk`, `skills/cloudflare`, `skills/cloudflare-email-service`, `skills/cloudflare-one`, `skills/cloudflare-one-migrations`, `skills/durable-objects`, `skills/sandbox-sdk`, `skills/turnstile-spin`, `skills/web-perf`, `skills/workers-best-practices`, `skills/wrangler` | [cloudflare/skills](https://github.com/cloudflare/skills) | Apache-2.0 | Cloudflare, Inc. |
| `skills/archify` | [tt-a1i/archify](https://github.com/tt-a1i/archify), based on Cocoon-AI/architecture-diagram-generator | MIT | 2026 tt-a1i; 2025 Cocoon AI — see `skills/archify/LICENSE` |
| `skills/frontend-slides` | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | MIT | 2025 Zara Zhang — see `skills/frontend-slides/LICENSE` |
| `skills/impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (npm `impeccable`) | Apache-2.0 | 2025 Paul Bakaus — see `skills/impeccable/LICENSE` and `skills/impeccable/NOTICE.md` (carries an MIT attribution to [ehmo/platform-design-skills](https://github.com/ehmo/platform-design-skills) for the iOS/Android references) |
| `skills/markitdown` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) (formerly claude-scientific-skills) | MIT | 2025 K-Dense Inc. — text below |
| `skills/playwright-cli` | [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli) (npm `@playwright/cli`) | Apache-2.0 | Microsoft Corporation |
| `skills/stop-slop` | [Hardik Pandya](https://hvpandya.com) | MIT | 2025 Hardik Pandya — see `skills/stop-slop/LICENSE` |
| `skills/theme-factory` | Anthropic | Apache-2.0 | 2026 Anthropic, PBC — see `skills/theme-factory/LICENSE.txt` |

Notes:

- The full Apache License 2.0 text is included in this repository at `skills/impeccable/LICENSE` and `skills/theme-factory/LICENSE.txt`; it applies equally to the Cloudflare-family and playwright-cli directories above.
- `skills/frontend-slides` downloads additional templates at runtime from [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates); that content is fetched, not vendored here — check its licence before redistributing outputs.
- One previously bundled skill (`guizang-ppt-skill`, AGPL-3.0) is deliberately **not** included in this distribution because its copyleft terms don't mix with a permissively licensed repo. Install it from upstream if you want it: [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill).

## MIT licence text for `skills/markitdown`

MIT License

Copyright (c) 2025 K-Dense Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
