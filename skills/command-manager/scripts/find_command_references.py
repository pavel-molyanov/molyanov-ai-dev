#!/usr/bin/env python3
"""
Command Reference Finder

Searches for references to a command before deletion to identify dependencies.
Searches in:
- Other commands (SlashCommand calls)
- Documentation files (guides, README)
- Configuration files (CLAUDE.md)

Usage:
    find_command_references.py <command-name> [--claude-dir PATH]

Examples:
    # Find references to a command
    python3 find_command_references.py deploy-app

    # Use custom .claude directory
    python3 find_command_references.py deploy-app --claude-dir /path/to/.claude
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class Reference:
    """Represents a reference to a command."""

    def __init__(self, filepath: Path, line_num: int, line_content: str, context: str = ""):
        self.filepath = filepath
        self.line_num = line_num
        self.line_content = line_content.strip()
        self.context = context

    def __str__(self):
        return f"{self.filepath}:{self.line_num} - {self.line_content}"


class ReferenceFinder:
    """Finds references to a command in various files."""

    def __init__(self, command_name: str, claude_dir: Path):
        self.command_name = command_name
        self.claude_dir = claude_dir
        self.references: Dict[str, List[Reference]] = {
            'commands': [],
            'documentation': [],
            'config': [],
        }

    def find_all_references(self):
        """Search all locations for references."""
        # Normalize command name (with or without /)
        patterns = [
            f'/{self.command_name}',  # /command-name
            f'SlashCommand.*{self.command_name}',  # SlashCommand tool usage
            self.command_name,  # Just the name
        ]

        # Search commands
        commands_dir = self.claude_dir / 'commands'
        if commands_dir.exists():
            self._search_directory(commands_dir, patterns, 'commands', exclude_files=[f'{self.command_name}.md'])

        # Search documentation in skills/*/guides/
        skills_dir = self.claude_dir / 'skills'
        if skills_dir.exists():
            for skill_path in skills_dir.iterdir():
                if skill_path.is_dir():
                    guides_dir = skill_path / 'guides'
                    if guides_dir.exists():
                        self._search_directory(guides_dir, patterns, 'documentation')

        readme = self.claude_dir / 'README.md'
        if readme.exists():
            self._search_file(readme, patterns, 'documentation')

        # Search CLAUDE.md
        claude_md = self.claude_dir / 'CLAUDE.md'
        if claude_md.exists():
            self._search_file(claude_md, patterns, 'config')

    def _search_directory(self, directory: Path, patterns: List[str], category: str, exclude_files: List[str] = None):
        """Search all files in directory."""
        exclude_files = exclude_files or []

        for filepath in directory.rglob('*.md'):
            if filepath.name in exclude_files:
                continue
            self._search_file(filepath, patterns, category)

    def _search_file(self, filepath: Path, patterns: List[str], category: str):
        """Search single file for patterns."""
        try:
            content = filepath.read_text(encoding='utf-8')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, start=1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Get context (surrounding lines)
                        context_start = max(0, line_num - 2)
                        context_end = min(len(lines), line_num + 1)
                        context = '\n'.join(lines[context_start:context_end])

                        ref = Reference(filepath, line_num, line, context)
                        self.references[category].append(ref)
                        break  # Only add once per line

        except Exception as e:
            print(f"Warning: Failed to read {filepath}: {e}", file=sys.stderr)

    def generate_report(self, language: str = 'ru') -> str:
        """Generate dependency report."""
        output = []

        if language == 'ru':
            output.append(f"Поиск упоминаний команды /{self.command_name}:")
            output.append("")

            # Commands
            if self.references['commands']:
                output.append(f"Найдено в командах ({len(self.references['commands'])}):")
                for ref in self.references['commands']:
                    rel_path = ref.filepath.relative_to(self.claude_dir)
                    output.append(f"  - {rel_path}:{ref.line_num}")
                    output.append(f"    {ref.line_content}")
                output.append("")
            else:
                output.append("✓ Не найдено в других командах")
                output.append("")

            # Documentation
            if self.references['documentation']:
                output.append(f"Найдено в документации ({len(self.references['documentation'])}):")
                for ref in self.references['documentation']:
                    rel_path = ref.filepath.relative_to(self.claude_dir)
                    output.append(f"  - {rel_path}:{ref.line_num}")
                    output.append(f"    {ref.line_content}")
                output.append("")
            else:
                output.append("✓ Не найдено в документации")
                output.append("")

            # Config
            if self.references['config']:
                output.append(f"Найдено в конфиге ({len(self.references['config'])}):")
                for ref in self.references['config']:
                    rel_path = ref.filepath.relative_to(self.claude_dir)
                    output.append(f"  - {rel_path}:{ref.line_num}")
                    output.append(f"    {ref.line_content}")
                output.append("")
            else:
                output.append("✓ Не найдено в конфиге")
                output.append("")

            # Summary
            total = sum(len(refs) for refs in self.references.values())
            if total > 0:
                output.append("=" * 60)
                output.append(f"⚠️  ВНИМАНИЕ: Найдено {total} упоминаний команды!")
                output.append("=" * 60)
                output.append("")
                output.append("Удаление этой команды может сломать:")
                if self.references['commands']:
                    output.append(f"  - {len(self.references['commands'])} других команд")
                if self.references['documentation']:
                    output.append(f"  - {len(self.references['documentation'])} документов")
                if self.references['config']:
                    output.append(f"  - {len(self.references['config'])} конфигов")
                output.append("")
                output.append("Убедись, что обновил все зависимости перед удалением!")
            else:
                output.append("=" * 60)
                output.append("✅ Команда не используется в других местах")
                output.append("=" * 60)
                output.append("")
                output.append("Безопасно удалять.")

        else:  # English
            output.append(f"Searching for references to /{self.command_name}:")
            output.append("")

            if self.references['commands']:
                output.append(f"Found in commands ({len(self.references['commands'])}):")
                for ref in self.references['commands']:
                    rel_path = ref.filepath.relative_to(self.claude_dir)
                    output.append(f"  - {rel_path}:{ref.line_num}")
                    output.append(f"    {ref.line_content}")
                output.append("")
            else:
                output.append("✓ Not found in other commands")
                output.append("")

            if self.references['documentation']:
                output.append(f"Found in documentation ({len(self.references['documentation'])}):")
                for ref in self.references['documentation']:
                    rel_path = ref.filepath.relative_to(self.claude_dir)
                    output.append(f"  - {rel_path}:{ref.line_num}")
                    output.append(f"    {ref.line_content}")
                output.append("")
            else:
                output.append("✓ Not found in documentation")
                output.append("")

            total = sum(len(refs) for refs in self.references.values())
            if total > 0:
                output.append("=" * 60)
                output.append(f"⚠️  WARNING: Found {total} references!")
                output.append("=" * 60)
                output.append("")
                output.append("Deleting this command may break other parts of the system.")
            else:
                output.append("=" * 60)
                output.append("✅ Command not used elsewhere")
                output.append("=" * 60)
                output.append("")
                output.append("Safe to delete.")

        return '\n'.join(output)

    def has_dependencies(self) -> bool:
        """Check if command has any dependencies."""
        return any(len(refs) > 0 for refs in self.references.values())


def main():
    parser = argparse.ArgumentParser(
        description='Find references to a command before deletion'
    )
    parser.add_argument(
        'command_name',
        help='Name of command to search for (without / prefix)'
    )
    parser.add_argument(
        '--claude-dir',
        type=Path,
        default=Path.home() / '.claude',
        help='Path to .claude directory (default: ~/.claude)'
    )
    parser.add_argument(
        '--language',
        choices=['ru', 'en'],
        default='ru',
        help='Report language (default: ru)'
    )

    args = parser.parse_args()

    # Remove leading / if present
    command_name = args.command_name.lstrip('/')

    if not args.claude_dir.exists():
        print(f"Error: Directory not found: {args.claude_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        finder = ReferenceFinder(command_name, args.claude_dir)
        finder.find_all_references()
        report = finder.generate_report(language=args.language)
        print(report)

        # Exit with code 1 if dependencies found (to signal caution)
        sys.exit(1 if finder.has_dependencies() else 0)

    except Exception as e:
        print(f"Error searching for references: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
