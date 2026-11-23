"""
Utility script to export DESIGN_DOCUMENT.md to a publication-ready styled HTML report.
Can be opened in any web browser and saved as PDF (Print -> Save as PDF).
"""

import os
import re

def markdown_to_html(md_text: str) -> str:
    html = md_text

    # Headers
    html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # Bold and italics
    html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)

    # Code blocks
    html = re.sub(r"```mermaid(.*?)```", r'<div class="mermaid">\1</div>', html, flags=re.DOTALL)
    html = re.sub(r"```[a-z]*(.*?)```", r"<pre><code>\1</code></pre>", html, flags=re.DOTALL)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

    # Tables (simple conversion)
    lines = html.split("\n")
    in_table = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                new_lines.append('<table class="report-table">')
                in_table = True
            cells = [c.strip() for c in line.strip()[1:-1].split("|")]
            if all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue  # Divider line
            row_html = "".join(f"<td>{c}</td>" for c in cells)
            new_lines.append(f"<tr>{row_html}</tr>")
        else:
            if in_table:
                new_lines.append("</table>")
                in_table = False
            new_lines.append(line)
    if in_table:
        new_lines.append("</table>")
    html = "\n".join(new_lines)

    # Lists
    html = re.sub(r"^\* (.*)$", r"<li>\1</li>", html, flags=re.MULTILINE)

    # Horizontal rules
    html = re.sub(r"^---$", r"<hr/>", html, flags=re.MULTILINE)

    # Paragraphs (line breaks)
    paragraphs = html.split("\n\n")
    wrapped = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith("<h") and not p.startswith("<table") and not p.startswith("<pre") and not p.startswith("<div"):
            wrapped.append(f"<p>{p}</p>")
        else:
            wrapped.append(p)

    body = "\n\n".join(wrapped)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>eSim Automated Tool Manager - Design Document</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({{startOnLoad:true, theme: 'neutral'}});</script>
  <style>
    body {{
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #24292f;
      max-width: 900px;
      margin: 40px auto;
      padding: 0 20px;
      background: #ffffff;
    }}
    h1 {{ color: #0969da; border-bottom: 2px solid #eaecef; padding-bottom: 10px; font-size: 26px; }}
    h2 {{ color: #1f2328; border-bottom: 1px solid #eaecef; padding-bottom: 6px; margin-top: 30px; font-size: 20px; }}
    h3 {{ color: #31373d; margin-top: 20px; font-size: 16px; }}
    code {{ background-color: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-size: 90%; font-family: Consolas, monospace; }}
    pre {{ background-color: #f6f8fa; padding: 14px; border-radius: 6px; overflow-x: auto; font-family: Consolas, monospace; }}
    .report-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
    .report-table td, .report-table th {{ border: 1px solid #d0d7de; padding: 8px 12px; font-size: 14px; }}
    .report-table tr:nth-child(even) {{ background-color: #f6f8fa; }}
    .mermaid {{ text-align: center; margin: 25px 0; background: #fafafa; padding: 15px; border-radius: 6px; }}
    hr {{ border: 0; height: 1px; background: #e1e4e8; margin: 30px 0; }}
    li {{ margin-bottom: 4px; }}
    @media print {{
      body {{ max-width: 100%; margin: 0; }}
      .mermaid {{ page-break-inside: avoid; }}
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_path = os.path.join(root, "DESIGN_DOCUMENT.md")
    out_path = os.path.join(root, "eSim_Task5_Design_Document.html")

    if not os.path.exists(doc_path):
        print(f"Error: {doc_path} not found.")
        return

    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    html = markdown_to_html(content)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Successfully generated HTML report: {out_path}")
    print("Open this file in your browser to view or print as PDF!")

if __name__ == "__main__":
    main()
