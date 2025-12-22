#!/usr/bin/env python3
"""
Command Index Generator

Scans all command files in ~/.claude/commands/ and generates
a comprehensive index with descriptions, tool usage, and complexity analysis.

Usage:
    generate_command_index.py [--commands-dir PATH]

Examples:
    # Generate index for default commands directory
    python3 generate_command_index.py

    # Generate index for specific directory
    python3 generate_command_index.py --commands-dir /path/to/commands

    # Save to file
    python3 generate_command_index.py > command-index.md
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse


def parse_frontmatter(content: str) -> Dict[str, any]:
    """
    Parse YAML frontmatter from command file.

    Returns dict with:
    - description: str
    - allowed_tools: List[str]
    """
    frontmatter = {}

    # Match frontmatter between --- markers
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.MULTILINE | re.DOTALL)

    if not match:
        return frontmatter

    yaml_content = match.group(1)

    # Parse description
    desc_match = re.search(r'description:\s*(.+?)(?:\n\w+:|$)', yaml_content, re.DOTALL)
    if desc_match:
        frontmatter['description'] = desc_match.group(1).strip()

    # Parse allowed-tools
    tools_match = re.search(r'allowed-tools:\s*\n((?:  - .+\n)+)', yaml_content)
    if tools_match:
        tools_text = tools_match.group(1)
        tools = re.findall(r'  - (.+)', tools_text)
        frontmatter['allowed_tools'] = [t.strip() for t in tools]
    else:
        frontmatter['allowed_tools'] = []

    return frontmatter


def count_steps(content: str) -> int:
    """Count number of steps in command (## N. headings)."""
    # Find all step headings like "## 1. Step name"
    steps = re.findall(r'^##\s+\d+\.\s+', content, re.MULTILINE)
    return len(steps)


def has_todowrite(content: str) -> bool:
    """Check if command uses TodoWrite."""
    return 'TodoWrite' in content and 'status' in content and 'activeForm' in content


def has_validation(content: str) -> bool:
    """Check if command has validation checks."""
    validation_patterns = [
        r'if \[.*\]; then',
        r'echo "SUCCESS"',
        r'echo "FAILED"',
        r'exit 1',
        r'VERIFY',
        r'CHECK',
    ]
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in validation_patterns)


def estimate_complexity(frontmatter: Dict, content: str) -> str:
    """
    Estimate command complexity based on:
    - Number of tools
    - Number of steps
    - Has TodoWrite
    - Has validation
    - Content length
    """
    tool_count = len(frontmatter.get('allowed_tools', []))
    step_count = count_steps(content)
    has_todo = has_todowrite(content)
    has_valid = has_validation(content)
    lines = len(content.split('\n'))

    # Simple scoring
    score = 0
    score += tool_count * 2
    score += step_count * 3
    score += 5 if has_todo else 0
    score += 3 if has_valid else 0
    score += lines // 20

    if score < 10:
        return "Simple"
    elif score < 30:
        return "Medium"
    else:
        return "Complex"


def categorize_command(name: str, description: str) -> str:
    """Attempt to categorize command based on name and description."""
    name_lower = name.lower()
    desc_lower = description.lower()

    # Project setup
    if any(word in name_lower for word in ['init', 'setup']):
        if 'project' in name_lower or 'git' in name_lower:
            return "Project Initialization"

    # Feature development
    if any(word in name_lower for word in ['feature', 'start', 'new']):
        return "Feature Development"

    # Task management
    if any(word in name_lower for word in ['task', 'plan', 'wave']):
        return "Task Management"

    # Technical planning
    if any(word in name_lower for word in ['context', 'spec', 'tech']):
        return "Technical Planning"

    # Infrastructure
    if any(word in name_lower for word in ['infrastructure', 'deploy', 'docker']):
        return "Infrastructure"

    # Command management
    if any(word in name_lower for word in ['command', 'slash']):
        return "Command Management"

    # Meta/System
    if 'meta' in name_lower or 'old' in name_lower or 'audit' in name_lower:
        return "Meta/System"

    return "Other"


def scan_commands(commands_dir: Path) -> List[Dict]:
    """Scan all command files and extract information."""
    commands = []

    if not commands_dir.exists():
        print(f"Error: Directory not found: {commands_dir}", file=sys.stderr)
        return commands

    # Find all .md files
    for filepath in sorted(commands_dir.glob("*.md")):
        try:
            content = filepath.read_text(encoding='utf-8')
            frontmatter = parse_frontmatter(content)

            command_name = filepath.stem
            description = frontmatter.get('description', 'No description')
            tools = frontmatter.get('allowed_tools', [])
            complexity = estimate_complexity(frontmatter, content)
            category = categorize_command(command_name, description)
            step_count = count_steps(content)

            commands.append({
                'name': command_name,
                'description': description,
                'tools': tools,
                'tool_count': len(tools),
                'complexity': complexity,
                'category': category,
                'step_count': step_count,
                'has_todowrite': has_todowrite(content),
                'has_validation': has_validation(content),
            })
        except Exception as e:
            print(f"Warning: Failed to parse {filepath.name}: {e}", file=sys.stderr)

    return commands


def generate_markdown_table(commands: List[Dict], group_by_category: bool = True) -> str:
    """Generate markdown table from commands list."""
    output = []

    # Header
    output.append("# Claude Code Commands Index")
    output.append("")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("")
    output.append(f"Total commands: {len(commands)}")
    output.append("")

    if group_by_category:
        # Group commands by category
        categories = {}
        for cmd in commands:
            category = cmd['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)

        # Output each category
        for category in sorted(categories.keys()):
            output.append(f"## {category}")
            output.append("")
            output.append("| Command | Description | Tools | Complexity |")
            output.append("|---------|-------------|-------|------------|")

            for cmd in sorted(categories[category], key=lambda x: x['name']):
                name = f"`/{cmd['name']}`"
                desc = cmd['description']
                tools = str(cmd['tool_count'])
                complexity = cmd['complexity']
                output.append(f"| {name} | {desc} | {tools} | {complexity} |")

            output.append("")
    else:
        # Single table
        output.append("| Command | Description | Tools | Complexity | Category |")
        output.append("|---------|-------------|-------|------------|----------|")

        for cmd in sorted(commands, key=lambda x: x['name']):
            name = f"`/{cmd['name']}`"
            desc = cmd['description']
            tools = str(cmd['tool_count'])
            complexity = cmd['complexity']
            category = cmd['category']
            output.append(f"| {name} | {desc} | {tools} | {complexity} | {category} |")

    return '\n'.join(output)


def generate_detailed_report(commands: List[Dict]) -> str:
    """Generate detailed report with statistics."""
    output = []

    # Statistics
    output.append("## Statistics")
    output.append("")

    # Complexity distribution
    complexity_counts = {}
    for cmd in commands:
        comp = cmd['complexity']
        complexity_counts[comp] = complexity_counts.get(comp, 0) + 1

    output.append("**Complexity Distribution:**")
    for comp in ['Simple', 'Medium', 'Complex']:
        count = complexity_counts.get(comp, 0)
        percentage = (count / len(commands) * 100) if commands else 0
        output.append(f"- {comp}: {count} ({percentage:.1f}%)")
    output.append("")

    # TodoWrite usage
    todowrite_count = sum(1 for cmd in commands if cmd['has_todowrite'])
    output.append(f"**TodoWrite Usage:** {todowrite_count}/{len(commands)} commands ({todowrite_count/len(commands)*100:.1f}%)")
    output.append("")

    # Validation checks
    validation_count = sum(1 for cmd in commands if cmd['has_validation'])
    output.append(f"**Validation Checks:** {validation_count}/{len(commands)} commands ({validation_count/len(commands)*100:.1f}%)")
    output.append("")

    # Most used tools
    tool_usage = {}
    for cmd in commands:
        for tool in cmd['tools']:
            # Normalize tool name (remove parameters)
            tool_base = tool.split('(')[0]
            tool_usage[tool_base] = tool_usage.get(tool_base, 0) + 1

    output.append("**Most Used Tools:**")
    for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
        output.append(f"- {tool}: {count} commands")
    output.append("")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Generate command index for Claude Code commands'
    )
    parser.add_argument(
        '--commands-dir',
        type=Path,
        default=Path.home() / '.claude' / 'commands',
        help='Path to commands directory (default: ~/.claude/commands)'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed statistics report'
    )
    parser.add_argument(
        '--no-categories',
        action='store_true',
        help='Do not group by categories'
    )

    args = parser.parse_args()

    # Scan commands
    commands = scan_commands(args.commands_dir)

    if not commands:
        print("No commands found!", file=sys.stderr)
        sys.exit(1)

    # Generate output
    output = generate_markdown_table(commands, group_by_category=not args.no_categories)
    print(output)

    if args.detailed:
        print("\n---\n")
        print(generate_detailed_report(commands))


if __name__ == '__main__':
    main()
