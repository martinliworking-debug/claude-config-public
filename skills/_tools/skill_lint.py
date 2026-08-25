#!/usr/bin/env python
"""skill_lint.py - validate every SKILL.md in a skills directory.

Why this exists
---------------
Two real-world failures traced to the same root: a skill's rule or tool was
correct, and nothing checked that it was reachable.

  1. Skills carried CRLF frontmatter with a bare ": " inside the description
     scalar. The loader fell back to the H1 heading, so the skills advertised
     their heading text instead of their real AUTO-TRIGGER description. Their
     entire trigger surface was invisible for an unknown period.
  2. A SKILL.md named a helper script that lived inside one project's folder.
     A machine-wide skill cannot depend on a single project; the referenced
     path resolved on no other machine.

So: frontmatter must parse, names must match, referenced paths must resolve,
and no skill may point into a project-specific folder.

Usage
-----
    python skill_lint.py                 # lint ~/.claude/skills
    python skill_lint.py --skills-dir D  # lint another tree
    python skill_lint.py --quiet         # findings only, no per-skill OK lines
    python skill_lint.py --selftest      # prove each check fires

Exit codes: 0 = no errors (warnings allowed), 1 = at least one ERROR,
2 = bad invocation. Terminal line is always `SKILL-LINT RESULT: PASS|FAIL`,
because a wrapper that exits 0 on a dead run is the failure mode this whole
family of checks exists to stop.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    sys.stderr.write(
        "PyYAML not available. Install it first:\n"
        "  pip install pyyaml\n"
    )
    raise SystemExit(2)

# --------------------------------------------------------------------------
# check ids, so a SKILL.md imperative can cite the check that enforces it
# --------------------------------------------------------------------------
FM001 = "FM-001 frontmatter parses as a YAML mapping"
FM002 = "FM-002 name and description present and non-empty"
FM003 = "FM-003 name matches the directory name"
FM004 = "FM-004 description is a single line"
FM005 = "FM-005 CRLF frontmatter must not contain a bare ': ' in a plain scalar"
REF001 = "REF-001 skill-relative paths named in SKILL.md resolve"
REF002 = "REF-002 no SKILL.md points into a job folder"

# A job folder: a P-code (P1234, P5678A) under a Desktop, or any absolute path
# carrying a P-code directory. Deliberately narrow to avoid false positives on
# prose that merely mentions a job.
JOB_PATH = re.compile(r"(?:[A-Za-z]:[\\/]|Desktop[\\/])[^\s`'\"]*[\\/]?P\d{4}[A-Za-z]?[\s\\/][^\s`\"]*")

# Skill-relative paths worth resolving: `scripts/x.py`, `references/y.md`,
# `signal/z.py`, `lib/w.py`, `engine/v.py`, `assets/u.css`. Only these prefixes,
# so we never try to resolve prose or shell fragments.
REL_PATH = re.compile(
    r"`((?:scripts|references|reference|signal|signals|lib|engine|assets|helpers|"
    r"config_template|templates)/[A-Za-z0-9_.\-/]+)`"
)

CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)


class Finding:
    __slots__ = ("skill", "level", "check", "detail")

    def __init__(self, skill: str, level: str, check: str, detail: str) -> None:
        self.skill, self.level, self.check, self.detail = skill, level, check, detail

    def __str__(self) -> str:
        return f"  {self.level:<5} [{self.check.split()[0]}] {self.detail}"


def split_frontmatter(text: str) -> str | None:
    """Return the raw frontmatter block, or None if the file has no fence."""
    if not text.lstrip("\ufeff").startswith("---"):
        return None
    body = text.lstrip("\ufeff")
    # find the closing fence at the start of a line
    m = re.search(r"^---\s*$", body[3:], re.MULTILINE)
    if not m:
        return None
    return body[3 : 3 + m.start()]


def lint_skill(skill_dir: Path) -> list[Finding]:
    name = skill_dir.name
    out: list[Finding] = []
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return [Finding(name, "ERROR", FM001, "no SKILL.md")]

    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    is_crlf = b"\r\n" in raw.split(b"---", 2)[0] + raw[:400]

    fm = split_frontmatter(text)
    if fm is None:
        out.append(Finding(name, "ERROR", FM001, "no --- frontmatter fence"))
        return out

    try:
        data = yaml.safe_load(fm)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 2} col {mark.column + 1}" if mark else ""
        out.append(Finding(name, "ERROR", FM001, f"YAML parse failed{where}: {getattr(exc, 'problem', exc)}"))
        data = None

    if data is not None and not isinstance(data, dict):
        out.append(Finding(name, "ERROR", FM001, f"frontmatter is {type(data).__name__}, not a mapping"))
        data = None

    if isinstance(data, dict):
        got_name = data.get("name")
        desc = data.get("description")
        if not got_name or not str(got_name).strip():
            out.append(Finding(name, "ERROR", FM002, "missing or empty `name`"))
        elif str(got_name).strip() != name:
            out.append(Finding(name, "ERROR", FM003, f"name '{got_name}' != directory '{name}'"))
        if not desc or not str(desc).strip():
            out.append(Finding(name, "ERROR", FM002, "missing or empty `description`"))
        elif "\n" in str(desc):
            out.append(Finding(name, "WARN", FM004, "description spans multiple lines; a line-oriented loader may truncate it"))

    # FM-005: the exact trap described in the module docstring. A bare ": " inside an
    # unquoted description is legal-ish on LF and fatal on CRLF, so gate on CRLF.
    raw_desc_line = ""
    for line in fm.splitlines():
        if line.lstrip().startswith("description:"):
            raw_desc_line = line
            break
    if raw_desc_line:
        value = raw_desc_line.split("description:", 1)[1].strip()
        quoted = (value[:1], value[-1:]) in ((('"', '"')), (("'", "'")))
        if not quoted and ": " in value:
            level = "ERROR" if is_crlf else "WARN"
            out.append(
                Finding(name, level, FM005,
                        f"bare ': ' in an unquoted description{' (file is CRLF)' if is_crlf else ''}; "
                        "replace with ' - ' or quote the scalar")
            )

    prose = CODE_FENCE.sub("", text)

    for m in REL_PATH.finditer(prose):
        rel = m.group(1)
        if not (skill_dir / rel).exists():
            out.append(Finding(name, "ERROR", REF001, f"names `{rel}` which does not exist in the skill"))

    for m in JOB_PATH.finditer(prose):
        frag = m.group(0).strip().rstrip(".,;)")
        out.append(Finding(name, "ERROR", REF002, f"points into a job folder: {frag[:110]}"))

    return out


def run(skills_dir: Path, quiet: bool = False) -> int:
    skills = sorted(d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith("_"))
    all_findings: list[Finding] = []
    for d in skills:
        if not (d / "SKILL.md").is_file():
            continue  # not a skill dir (assets, vendored trees)
        f = lint_skill(d)
        all_findings.extend(f)
        if f:
            print(f"{d.name}:")
            for x in f:
                print(x)
        elif not quiet:
            print(f"{d.name}: ok")

    errors = [f for f in all_findings if f.level == "ERROR"]
    warns = [f for f in all_findings if f.level == "WARN"]
    print()
    print(f"{len(skills)} skills scanned, {len(errors)} error(s), {len(warns)} warning(s)")
    print(f"SKILL-LINT RESULT: {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


# --------------------------------------------------------------------------
# selftest: every check must be shown to fire, or it is not known to work
# --------------------------------------------------------------------------
SAMPLES = {
    FM003: ("---\nname: wrong-name\ndescription: fine.\n---\n# t\n", "ok-name"),
    FM002: ("---\nname: s\n---\n# t\n", "s"),
    FM005: ("---\r\nname: s\r\ndescription: a thing: with a colon.\r\n---\r\n# t\r\n", "s"),
    REF001: ("---\nname: s\ndescription: fine.\n---\n# t\nSee `scripts/nope.py`.\n", "s"),
    REF002: ("---\nname: s\ndescription: fine.\n---\n# t\nSee C:/Users/x/Desktop/P1234 Job/a.py\n", "s"),
    FM001: ("---\nname: [unclosed\n---\n# t\n", "s"),
}


def selftest() -> int:
    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for check, (content, dirname) in SAMPLES.items():
            d = root / dirname
            d.mkdir(exist_ok=True)
            (d / "SKILL.md").write_bytes(content.encode("utf-8"))
            fired = {f.check for f in lint_skill(d)}
            hit = check in fired
            print(f"{'PASS' if hit else 'FAIL'}  {check}")
            if not hit:
                print(f"      fired instead: {sorted(c.split()[0] for c in fired) or 'nothing'}")
                ok = False
            (d / "SKILL.md").unlink()
        # a clean skill must produce nothing
        d = root / "clean"
        d.mkdir(exist_ok=True)
        (d / "SKILL.md").write_bytes(b"---\nname: clean\ndescription: A fine description.\n---\n# t\n")
        f = lint_skill(d)
        print(f"{'PASS' if not f else 'FAIL'}  clean skill produces no findings")
        if f:
            for x in f:
                print(x)
            ok = False
    print(f"SELFTEST RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills-dir", default=str(Path.home() / ".claude" / "skills"))
    ap.add_argument("--quiet", action="store_true", help="print findings only")
    ap.add_argument("--selftest", action="store_true", help="prove each check fires")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    d = Path(a.skills_dir)
    if not d.is_dir():
        sys.stderr.write(f"not a directory: {d}\n")
        return 2
    return run(d, quiet=a.quiet)


if __name__ == "__main__":
    raise SystemExit(main())
