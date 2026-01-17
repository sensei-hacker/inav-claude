#!/usr/bin/env python3
"""
Convert slide mockup text files to HTML with terminal-like styling.
Resembles Claude Code session appearance.
"""

import os
import glob
from html import escape

# Claude Code dark theme colors
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{filename}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .timestamp {{
            color: #888;
        }}
        .header {{
            color: #4fc3f7;
            font-weight: bold;
        }}
        .success {{
            color: #81c784;
        }}
        .error {{
            color: #ff5252;
        }}
        .filename {{
            color: #ffb74d;
        }}
        .comment {{
            color: #888;
            font-style: italic;
        }}
    </style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>
"""

def add_syntax_highlighting(text):
    """Add basic syntax highlighting by wrapping certain patterns."""
    lines = text.split('\n')
    result = []

    for line in lines:
        line_html = escape(line)

        # Highlight timestamps
        if line.strip().startswith('[') and ']:' in line:
            parts = line_html.split(']:', 1)
            line_html = f'<span class="timestamp">{parts[0]}]:</span>{parts[1] if len(parts) > 1 else ""}'

        # Highlight headers with ###
        elif line.strip().startswith('###'):
            line_html = f'<span class="header">{line_html}</span>'

        # Highlight success markers
        elif '✓' in line or '✅' in line:
            line_html = f'<span class="success">{line_html}</span>'

        # Highlight error markers
        elif '✗' in line or '❌' in line:
            line_html = f'<span class="error">{line_html}</span>'

        # Highlight file paths
        elif '.md' in line or '.js' in line or '.ts' in line:
            line_html = f'<span class="filename">{line_html}</span>'

        # Highlight comments
        elif line.strip().startswith('//') or line.strip().startswith('#'):
            line_html = f'<span class="comment">{line_html}</span>'

        result.append(line_html)

    return '\n'.join(result)

def convert_file(input_path):
    """Convert a single markdown mockup to HTML."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add basic syntax highlighting
    highlighted = add_syntax_highlighting(content)

    # Get filename for title
    filename = os.path.basename(input_path)

    # Generate HTML
    html = HTML_TEMPLATE.format(
        filename=filename,
        content=highlighted
    )

    # Output path
    output_path = input_path.replace('.md', '.html')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Created: {output_path}")
    return output_path

def main():
    """Convert all slide-09-*.md files to HTML."""
    pattern = 'slide-09-*.md'
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No files matching {pattern} found in current directory")
        return

    print(f"Converting {len(files)} files...\n")

    for file in files:
        convert_file(file)

    print(f"\n✅ Done! Created {len(files)} HTML files.")
    print("\nTo create screenshots:")
    print("1. Open each .html file in browser (Firefox or Chrome)")
    print("2. Press F11 for fullscreen")
    print("3. Use browser screenshot tool or:")
    print("   - Firefox: Right-click → Take Screenshot → Save Full Page")
    print("   - Chrome: Ctrl+Shift+P → 'Capture full size screenshot'")

if __name__ == '__main__':
    main()
