#!/usr/bin/env python3
"""
Command Analyzer

Validates command files against the command creation checklist and provides
detailed feedback on quality, structure, and potential improvements.

Usage:
    analyze_command.py <command-file> [--detailed]

Examples:
    # Basic analysis
    python3 analyze_command.py ~/.claude/commands/my-command.md

    # Detailed analysis with suggestions
    python3 analyze_command.py ~/.claude/commands/my-command.md --detailed
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


class Issue:
    """Represents a validation issue."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

    def __init__(self, severity: str, category: str, message: str, suggestion: str = ""):
        self.severity = severity
        self.category = category
        self.message = message
        self.suggestion = suggestion


class CommandAnalyzer:
    """Analyzes command files for quality and compliance."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text(encoding='utf-8')
        self.issues: List[Issue] = []
        self.frontmatter = {}

    def analyze(self) -> List[Issue]:
        """Run all validation checks."""
        self.check_frontmatter()
        self.check_todowrite_usage()
        self.check_instruction_clarity()
        self.check_shell_compatibility()
        self.check_validation_checks()
        self.check_step_numbering()
        self.check_placeholders()
        return self.issues

    def check_frontmatter(self):
        """Check frontmatter completeness and validity."""
        # Check frontmatter exists
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', self.content, re.MULTILINE | re.DOTALL)

        if not match:
            self.issues.append(Issue(
                Issue.CRITICAL,
                "Frontmatter",
                "Missing frontmatter (---...---)",
                "Add YAML frontmatter at the start of the file with description and allowed-tools"
            ))
            return

        yaml_content = match.group(1)

        # Check description
        desc_match = re.search(r'description:\s*(.+?)(?:\n\w+:|$)', yaml_content, re.DOTALL)
        if not desc_match:
            self.issues.append(Issue(
                Issue.CRITICAL,
                "Frontmatter",
                "Missing 'description' field",
                "Add description: Brief description of what command does"
            ))
        else:
            description = desc_match.group(1).strip()
            if '[TODO]' in description or 'TBD' in description:
                self.issues.append(Issue(
                    Issue.WARNING,
                    "Frontmatter",
                    "Description contains placeholder",
                    "Replace [TODO] or TBD with actual description"
                ))

        # Check allowed-tools
        tools_match = re.search(r'allowed-tools:\s*\n((?:  - .+\n)+)', yaml_content)
        if not tools_match:
            self.issues.append(Issue(
                Issue.CRITICAL,
                "Frontmatter",
                "Missing 'allowed-tools' field",
                "Add allowed-tools list with specific tools this command uses"
            ))
        else:
            tools_text = tools_match.group(1)
            tools = re.findall(r'  - (.+)', tools_text)

            # Check for overly permissive wildcards
            if '- *' in tools_text and 'Bash(*)' not in tools_text:
                self.issues.append(Issue(
                    Issue.CRITICAL,
                    "Frontmatter",
                    "Overly permissive wildcard '*' in allowed-tools",
                    "List specific tools instead of '*'. Only Bash(*) is allowed as wildcard."
                ))

            # Store for later checks
            self.frontmatter['allowed_tools'] = tools

    def check_todowrite_usage(self):
        """Check TodoWrite usage for multi-step commands."""
        # Count steps
        steps = re.findall(r'^##\s+\d+\.\s+', self.content, re.MULTILINE)
        step_count = len(steps)

        # Check if TodoWrite is used
        has_todowrite = 'TodoWrite' in self.content and 'status' in self.content and 'activeForm' in self.content

        if step_count > 1 and not has_todowrite:
            self.issues.append(Issue(
                Issue.CRITICAL,
                "TodoWrite",
                f"Command has {step_count} steps but no TodoWrite",
                "Add TodoWrite section at step 0 with all steps listed in Russian"
            ))

        if has_todowrite:
            # Check if TodoWrite is in Russian
            todo_section = re.search(
                r'TodoWrite.*?\[.*?\]',
                self.content,
                re.DOTALL | re.IGNORECASE
            )
            if todo_section:
                todo_text = todo_section.group(0)

                # Simple heuristic: check for Cyrillic characters
                if not re.search(r'[а-яА-ЯёЁ]', todo_text):
                    self.issues.append(Issue(
                        Issue.WARNING,
                        "TodoWrite",
                        "TodoWrite appears to be in English, not Russian",
                        "TodoWrite is user-facing, so content and activeForm must be in Russian"
                    ))

                # Check if all steps are represented
                todo_items = re.findall(r'"content":\s*"([^"]+)"', todo_text)
                if len(todo_items) < step_count - 1:  # -1 for step 0
                    self.issues.append(Issue(
                        Issue.WARNING,
                        "TodoWrite",
                        f"TodoWrite has {len(todo_items)} items but command has {step_count} steps",
                        "Ensure all major steps are represented in TodoWrite"
                    ))

    def check_instruction_clarity(self):
        """Check for clear, imperative instructions."""
        # Look for vague example language
        vague_patterns = [
            (r'\bexample\b', "Uses 'example' - be explicit instead"),
            (r'\byou can\b', "Uses 'you can' - use imperative form instead"),
            (r'\bconsider\b', "Uses 'consider' - be explicit instead"),
            (r'\bmight want to\b', "Uses 'might want to' - be explicit instead"),
            (r'\bsimilar to\b', "Uses 'similar to' - provide exact command instead"),
            (r'\bsomething like\b', "Uses 'something like' - be specific instead"),
        ]

        for pattern, message in vague_patterns:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            for match in matches:
                # Get line number
                line_num = self.content[:match.start()].count('\n') + 1
                self.issues.append(Issue(
                    Issue.WARNING,
                    "Instruction Clarity",
                    f"Line {line_num}: {message}",
                    "Use imperative verbs: EXECUTE, RUN, CREATE, VERIFY"
                ))

        # Check for imperative verbs (good!)
        has_imperatives = any(
            word in self.content.upper()
            for word in ['EXECUTE', 'RUN', 'CREATE', 'VERIFY', 'CHECK', 'ASK']
        )

        if not has_imperatives:
            self.issues.append(Issue(
                Issue.INFO,
                "Instruction Clarity",
                "No imperative verbs found (EXECUTE, RUN, CREATE, etc.)",
                "Consider using imperative language for clarity"
            ))

    def check_shell_compatibility(self):
        """Check for zsh compatibility issues."""
        # Problematic patterns
        problems = [
            (
                r'\$\(.*\|.*while\s+read',
                "Complex pipe in command substitution may not work in zsh",
                "Use temp files instead: cmd > /tmp/file.txt; while read line; done < /tmp/file.txt"
            ),
            (
                r'<\([^)]+\)',
                "Process substitution may not work consistently",
                "Use temp files instead of process substitution"
            ),
            (
                r'\$\{.*\[@\].*\}',
                "Bash array syntax may not work in zsh",
                "Use simple loops or temp files instead"
            ),
        ]

        for pattern, message, suggestion in problems:
            matches = re.finditer(pattern, self.content)
            for match in matches:
                line_num = self.content[:match.start()].count('\n') + 1
                self.issues.append(Issue(
                    Issue.WARNING,
                    "Shell Compatibility",
                    f"Line {line_num}: {message}",
                    suggestion
                ))

    def check_validation_checks(self):
        """Check for validation after critical operations."""
        # Look for operations that should have validation
        operations = [
            (r'\bmkdir\s+', "mkdir", "Verify directory created with: if [ ! -d dir ]; then echo ERROR; fi"),
            (r'\bcp\s+', "cp", "Verify file copied with: if [ ! -f dest ]; then echo ERROR; fi"),
            (r'\bmv\s+', "mv", "Verify file moved with: if [ ! -f dest ]; then echo ERROR; fi"),
            (r'\bgit commit\s+', "git commit", "Verify commit with: git log -1 --oneline"),
            (r'\bgit push\s+', "git push", "Check exit code: if [ $? -ne 0 ]; then echo ERROR; fi"),
            (r'\bnpm run build', "npm run build", "Verify build output exists: if [ ! -d dist ]; then echo ERROR; fi"),
        ]

        # Check if validation patterns exist
        validation_patterns = [
            r'if \[',
            r'&& echo "SUCCESS"',
            r'\|\| echo "FAILED"',
            r'exit 1',
            r'VERIFY',
            r'CHECK',
        ]

        has_validation = any(
            re.search(pattern, self.content, re.IGNORECASE)
            for pattern in validation_patterns
        )

        if not has_validation:
            # Check if command has critical operations
            has_critical_ops = any(
                re.search(pattern, self.content)
                for pattern, _, _ in operations
            )

            if has_critical_ops:
                self.issues.append(Issue(
                    Issue.WARNING,
                    "Validation",
                    "Command performs operations but has no validation checks",
                    "Add validation after critical operations to ensure they succeeded"
                ))

    def check_step_numbering(self):
        """Check for whole number step numbering."""
        # Find all step headings
        steps = re.findall(r'^##\s+(\d+(?:\.\d+)?)\.\s+', self.content, re.MULTILINE)

        for step in steps:
            if '.' in step and step != '0':  # Allow ## 0. but not ## 1.5
                self.issues.append(Issue(
                    Issue.WARNING,
                    "Step Numbering",
                    f"Step {step} uses decimal numbering",
                    "Use whole numbers only: 1, 2, 3 (not 1.5, 2.5)"
                ))

        # Check for letter sub-steps
        letter_steps = re.findall(r'^##\s+\d+[a-zA-Z]\.\s+', self.content, re.MULTILINE)
        if letter_steps:
            self.issues.append(Issue(
                Issue.WARNING,
                "Step Numbering",
                "Found letter sub-steps (e.g., 1a, 1b)",
                "Use whole numbers only: 1, 2, 3"
            ))

    def check_placeholders(self):
        """Check for placeholders indicating incomplete command."""
        placeholders = [
            (r'\[TODO\]', "[TODO]"),
            (r'\[TBD\]', "[TBD]"),
            (r'\[FIXME\]', "[FIXME]"),
            (r'\{[a-z-]+\}', "{placeholder}"),
            (r'<[a-z-]+>', "<placeholder>"),
            (r'your-.*-here', "your-*-here"),
        ]

        for pattern, placeholder_type in placeholders:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            for match in matches:
                line_num = self.content[:match.start()].count('\n') + 1
                self.issues.append(Issue(
                    Issue.WARNING,
                    "Placeholders",
                    f"Line {line_num}: Found placeholder '{placeholder_type}'",
                    "Replace placeholders with actual values before using command"
                ))

    def generate_report(self, detailed: bool = False) -> str:
        """Generate validation report."""
        output = []

        # Header
        output.append("=" * 60)
        output.append(f"Command Analysis: {self.filepath.name}")
        output.append("=" * 60)
        output.append("")

        if not self.issues:
            output.append("✅ All checks passed! Command looks good.")
            return '\n'.join(output)

        # Group issues by severity
        critical = [i for i in self.issues if i.severity == Issue.CRITICAL]
        warnings = [i for i in self.issues if i.severity == Issue.WARNING]
        info = [i for i in self.issues if i.severity == Issue.INFO]

        # Summary
        output.append("Summary:")
        output.append(f"  ❌ Critical: {len(critical)}")
        output.append(f"  ⚠️  Warnings: {len(warnings)}")
        output.append(f"  ℹ️  Info: {len(info)}")
        output.append("")

        # Critical issues
        if critical:
            output.append("=" * 60)
            output.append("❌ CRITICAL ISSUES (must fix)")
            output.append("=" * 60)
            output.append("")
            for issue in critical:
                output.append(f"[{issue.category}] {issue.message}")
                if detailed and issue.suggestion:
                    output.append(f"  → Suggestion: {issue.suggestion}")
                output.append("")

        # Warnings
        if warnings:
            output.append("=" * 60)
            output.append("⚠️  WARNINGS (should fix)")
            output.append("=" * 60)
            output.append("")
            for issue in warnings:
                output.append(f"[{issue.category}] {issue.message}")
                if detailed and issue.suggestion:
                    output.append(f"  → Suggestion: {issue.suggestion}")
                output.append("")

        # Info
        if info and detailed:
            output.append("=" * 60)
            output.append("ℹ️  INFO (nice to have)")
            output.append("=" * 60)
            output.append("")
            for issue in info:
                output.append(f"[{issue.category}] {issue.message}")
                if issue.suggestion:
                    output.append(f"  → Suggestion: {issue.suggestion}")
                output.append("")

        # Recommendations
        if detailed:
            output.append("=" * 60)
            output.append("Recommendations")
            output.append("=" * 60)
            output.append("")

            if critical:
                output.append("1. Fix all CRITICAL issues before using this command")
            if warnings:
                output.append("2. Address WARNINGS to improve command quality")
            if not critical and not warnings:
                output.append("Command is in good shape! Consider INFO suggestions for further improvement.")

        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze command file against validation checklist'
    )
    parser.add_argument(
        'command_file',
        type=Path,
        help='Path to command file to analyze'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed suggestions and recommendations'
    )

    args = parser.parse_args()

    if not args.command_file.exists():
        print(f"Error: File not found: {args.command_file}", file=sys.stderr)
        sys.exit(1)

    try:
        analyzer = CommandAnalyzer(args.command_file)
        analyzer.analyze()
        report = analyzer.generate_report(detailed=args.detailed)
        print(report)

        # Exit with error code if critical issues found
        critical_count = sum(1 for i in analyzer.issues if i.severity == Issue.CRITICAL)
        sys.exit(1 if critical_count > 0 else 0)

    except Exception as e:
        print(f"Error analyzing command: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
