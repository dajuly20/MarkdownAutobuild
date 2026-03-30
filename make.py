#!/usr/bin/env python3
"""
Markdown Recursive - Combine linked Markdown files into a single document.

FEATURES:
- Inlines linked .md files at the position of each link (not appended at the end)
- Recursively processes nested links
- Prevents infinite loops (circular references)
- Converts [text](file.md) links to internal PDF anchors
- Auto-opens resulting PDF

USAGE:
  make.py                    # Uses README.md → pdf/README.pdf
  make.py input.md           # Uses input.md → pdf/input.pdf
  make.py -o pdf/custom.pdf CLAUDE.md      # Custom output path
  make.py -n README.md                      # No auto-open
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Set, Dict

# Regex for markdown links: [text](file.md) or [text](path/file.md)
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)')


class MarkdownRecursive:
    def __init__(self, input_file: str = None, output_pdf: str = None,
                 auto_open: bool = True):
        self.base_dir = Path.cwd()
        self.input_file = self._find_input_file(input_file)
        self.output_pdf = output_pdf or f"pdf/{self.input_file.stem}.pdf"
        self.auto_open = auto_open

        self.visited: Set[Path] = set()
        self.anchor_counts: Dict[str, int] = {}

    def _find_input_file(self, input_file: str = None) -> Path:
        if input_file:
            file = Path(input_file)
            if file.exists():
                return file
            raise FileNotFoundError(f"File not found: {input_file}")

        for file in self.base_dir.glob("*.md"):
            if file.name.lower() == "readme.md":
                return file

        raise FileNotFoundError("README.md not found in current directory")

    def _make_anchor(self, filepath: Path) -> str:
        try:
            rel = filepath.relative_to(self.base_dir)
        except ValueError:
            rel = Path(filepath.name)

        anchor = str(rel).replace('.md', '').lower()
        anchor = re.sub(r'[^a-z0-9]+', '-', anchor).strip('-')
        base_anchor = f"sec-{anchor}"

        if base_anchor not in self.anchor_counts:
            self.anchor_counts[base_anchor] = 0
            return base_anchor
        else:
            self.anchor_counts[base_anchor] += 1
            return f"{base_anchor}-{self.anchor_counts[base_anchor]}"

    def _resolve_link_path(self, link_target: str, relative_to: Path) -> Path:
        return (relative_to / link_target).resolve()

    def _inline_content(self, filepath: Path, depth: int = 0) -> str:
        """
        Read a file and recursively replace each [text](file.md) link
        with the content of that file, inlined at that position.
        """
        if filepath in self.visited:
            print(f"Warning: Circular reference, skipping: {filepath.name}",
                  file=sys.stderr)
            return ""

        self.visited.add(filepath)

        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
            return ""

        def replace_link(match):
            link_text = match.group(1)
            link_target = match.group(2)
            target_path = self._resolve_link_path(link_target, filepath.parent)

            if not target_path.exists():
                print(f"Warning: Linked file not found: {link_target}",
                      file=sys.stderr)
                return match.group(0)

            if target_path in self.visited:
                # Already inlined elsewhere — keep as plain text reference
                return f"*{link_text}*"

            anchor = self._make_anchor(target_path)
            filename = target_path.stem.replace('-', ' ').replace('_', ' ')
            inlined = self._inline_content(target_path, depth + 1)
            print(f"  {'  ' * depth}↳ {target_path.name}")
            return f"\n\n# {filename} {{#{anchor}}}\n\n{inlined}\n\n"

        return MD_LINK_PATTERN.sub(replace_link, content)

    def _build_combined_markdown(self) -> str:
        content = self._inline_content(self.input_file)

        if not content.startswith('#'):
            title = self.input_file.stem.replace('-', ' ').replace('_', ' ')
            content = f"# {title}\n\n{content}"

        return content

    def run(self):
        print(f"Input: {self.input_file}")
        print("Building combined markdown (inlining linked files)...")

        combined_md = self._build_combined_markdown()

        output_path = Path(self.output_pdf)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_md = output_path.with_suffix('.md')
        temp_md.write_text(combined_md, encoding='utf-8')

        print(f"Building PDF: {self.output_pdf}")
        try:
            subprocess.run(
                ['pandoc', str(temp_md), '-o', str(self.output_pdf),
                 '--pdf-engine=xelatex', '--toc'],
                check=True,
                capture_output=True
            )
            print(f"PDF created: {self.output_pdf}")
        except subprocess.CalledProcessError as e:
            print(f"Error: PDF build failed:\n{e.stderr.decode()}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: pandoc not found.", file=sys.stderr)
            sys.exit(1)

        if self.auto_open:
            try:
                opener = os.environ.get('OPENER', 'xdg-open')
                subprocess.Popen([opener, str(self.output_pdf)])
            except Exception as e:
                print(f"Warning: Could not open PDF: {e}", file=sys.stderr)

        print("Done!")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Recursively inline linked Markdown files into a single PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('input_file', nargs='?', default=None,
                        help='Input .md file (default: README.md)')
    parser.add_argument('-o', '--output', dest='output_pdf', default=None,
                        help='Output PDF path')
    parser.add_argument('-n', '--no-open', dest='auto_open', action='store_false',
                        help='Do not auto-open PDF')

    args = parser.parse_args()

    try:
        converter = MarkdownRecursive(
            input_file=args.input_file,
            output_pdf=args.output_pdf,
            auto_open=args.auto_open,
        )
        converter.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
