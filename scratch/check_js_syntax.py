import re
import js2py # or simple python AST / node check

with open(r"c:\jarvis AI\jarvis\public\hud\index.html", "r", encoding="utf-8") as f:
    content = f.read()

script_blocks = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
print(f"Found {len(script_blocks)} script blocks.")
for idx, sb in enumerate(script_blocks):
    print(f"Block {idx} length: {len(sb)} chars")
