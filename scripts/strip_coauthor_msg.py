"""Remove Cursor co-author trailers from commit messages (git filter-branch helper)."""
import sys

msg = sys.stdin.read()
lines = [
    line
    for line in msg.splitlines(keepends=True)
    if not line.startswith("Co-authored-by: Cursor <cursoragent@cursor.com>")
]
while lines and lines[-1].strip() == "":
    lines.pop()
if lines and not lines[-1].endswith("\n"):
    lines.append("\n")
sys.stdout.write("".join(lines))
