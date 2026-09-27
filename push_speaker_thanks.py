#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "DistributedApps.AI",
    "GIT_AUTHOR_EMAIL": "kenhuangus@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "DistributedApps.AI",
    "GIT_COMMITTER_EMAIL": "kenhuangus@users.noreply.github.com",
}
MSG = (
    "Add speaker intro and recent two-book closing slides from graph-engineer deck.\n"
    "\n"
    "Slide 2 introduces Ken Huang with the book gallery; final slide features "
    "Graph Engineering and Harness Engineering (EN/ZH).\n"
)


def run(args, input_text=None, check=True):
    r = subprocess.run(args, cwd=ROOT, input=input_text, text=True, capture_output=True, env=ENV)
    if check and r.returncode:
        sys.stderr.write(r.stdout or "")
        sys.stderr.write(r.stderr or "")
        raise SystemExit(r.returncode)
    return r


def main():
    shutil.copy2(ROOT / "index.html", ROOT / "docs" / "index.html")
    shutil.copy2(ROOT / "slides.html", ROOT / "docs" / "slides.html")
    shutil.copy2(ROOT / "slides-zh.js", ROOT / "docs" / "slides-zh.js")
    run(["git", "add", "-A"])
    st = run(["git", "status", "--porcelain"]).stdout.strip()
    if not st:
        print("nothing to commit")
    else:
        tree = run(["git", "write-tree"]).stdout.strip()
        head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
        new = run(["git", "commit-tree", tree, "-p", head], input_text=MSG).stdout.strip()
        run(["git", "reset", "--soft", new])
        body = run(["git", "log", "-1", "--format=%B"]).stdout
        if "Co-authored-by" in body:
            raise SystemExit("trailer present")
        print("COMMIT", new)
    run(["git", "push", "origin", "HEAD:main"])
    print("Pushed")
    print("Local speaker: file:///C:/Users/kenhu/agentic-ai-2026-predictions/slides.html?lang=en#2")
    print("Local books:   file:///C:/Users/kenhu/agentic-ai-2026-predictions/slides.html?lang=en#20")
    print("Public speaker: https://kenhuangus.github.io/agentic-ai-2026-predictions/slides.html?lang=en#2")
    print("Public books:   https://kenhuangus.github.io/agentic-ai-2026-predictions/slides.html?lang=en#20")


if __name__ == "__main__":
    main()
