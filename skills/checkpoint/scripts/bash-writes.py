#!/usr/bin/env python3
"""List files a session wrote outside the Write/Edit tools, for checkpoint attribution.

write-manifest only records Write/Edit/MultiEdit from the main thread. This scans the
session transcript (which survives compaction) for:
  - Bash redirections / tee / cp / mv / sed -i / heredoc targets (main + subagents)
  - Write/Edit/MultiEdit/NotebookEdit calls made by subagents
and prints only paths that exist now and sit inside a git repo (scratchpad / tmp dropped).

usage: bash-writes.py <session-id | transcript.jsonl> [--after ISO_TIMESTAMP] [--all]
  --after  only calls at/after this timestamp (e.g. the previous checkpoint)
  --all    keep paths outside git repos too
"""
import glob, json, os, re, shlex, subprocess, sys

REDIR = re.compile(r"(?<![0-9&<>])>{1,2}\|?\s*(\"[^\"]+\"|'[^']+'|[^\s;&|()<>]+)")


def transcripts(arg):
    if arg.endswith(".jsonl"):
        main = os.path.expanduser(arg)
    else:
        hits = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{arg}.jsonl"))
        if not hits:
            sys.exit(f"transcript not found for {arg}")
        main = hits[0]
    subs = sorted(glob.glob(main[:-6] + "/subagents/*.jsonl"))
    return [("main", main)] + [(os.path.basename(s)[:-6], s) for s in subs]


def bash_targets(cmd, cwd):
    """Return absolute write targets, following `cd` between command segments."""
    out = []
    for seg in re.split(r"&&|\|\||;|\n", cmd):
        for m in REDIR.finditer(seg):
            out.append(resolve(m.group(1).strip("\"'"), cwd))
        for part in seg.split("|"):
            try:
                tok = shlex.split(part, comments=True)
            except ValueError:
                continue
            if not tok:
                continue
            head = os.path.basename(tok[0])
            args = [t for t in tok[1:] if t and not t.startswith("-")]
            if head == "cd" and args:
                cwd = resolve(args[0], cwd)
            elif head == "tee":
                out += [resolve(a, cwd) for a in args]
            elif head in ("cp", "mv", "rsync", "install") and len(args) >= 2:
                out.append(resolve(args[-1], cwd))
            elif head == "sed" and any(t.startswith("-i") for t in tok[1:]) and len(args) >= 2:
                out += [resolve(a, cwd) for a in args[1:]]
    return [p for p in out if not p.startswith("/dev/") and "&" not in os.path.basename(p)]


def resolve(p, cwd):
    p = os.path.expanduser(os.path.expandvars(p))
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd or "/", p))


def in_repo(p):
    d = p if os.path.isdir(p) else os.path.dirname(p)
    while d and not os.path.isdir(d):
        d = os.path.dirname(d)
    r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    argv = sys.argv[1:]
    if not argv:
        sys.exit(__doc__)
    after = argv[argv.index("--after") + 1] if "--after" in argv else ""
    keep_all = "--all" in argv
    found = {}
    for who, path in transcripts(argv[0]):
        for line in open(path, errors="ignore"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ts, cwd = d.get("timestamp", ""), d.get("cwd")
            if after and ts < after:
                continue
            content = (d.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if b.get("type") != "tool_use":
                    continue
                name, inp = b.get("name"), b.get("input") or {}
                if name == "Bash":
                    cmd = inp.get("command", "")
                    for t in bash_targets(cmd, cwd):
                        found.setdefault(t, (who, ts, "Bash: " + cmd.splitlines()[0][:80]))
                elif who != "main" and name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp:
                        found.setdefault(resolve(fp, cwd), (who, ts, name))
    for p, (who, ts, how) in sorted(found.items(), key=lambda x: x[1][1]):
        if not os.path.isfile(p) or "/scratchpad/" in p or p.startswith(("/tmp/", "/private/tmp/")):
            continue
        repo = in_repo(p)
        if repo or keep_all:
            print(f"{p}\t{who}\t{ts}\t{how}")


if __name__ == "__main__":
    main()
