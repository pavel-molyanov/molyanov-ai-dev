"""Integration coverage for public-layout generation and Git hook staging."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent


class PublicSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ("scripts", ".githooks", "skills/code-reviewing/scripts", "agents", "commands"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / "scripts/sync-to-codex.py", self.root / "scripts/sync-to-codex.py")
        for name in ("sync-runtime.py", "pre-commit", "pre-push"):
            shutil.copy2(SOURCE / ".githooks" / name, self.root / ".githooks" / name)
        self.write("CLAUDE.md", "# Instructions\nRead CLAUDE.md.\n")
        self.write("skills/code-reviewing/SKILL.md", "---\nname: code-reviewing\ndescription: Review code.\n---\n# Review\nRead CLAUDE.md.\n")
        self.write("skills/code-reviewing/scripts/run.sh", "#!/bin/sh\nexit 0\n")
        (self.root / "skills/code-reviewing/scripts/run.sh").chmod(0o755)
        self.write("agents/code-reviewer.md", "---\nname: code-reviewer\ndescription: Review code.\nskills:\n  - code-reviewing\nallowed-tools:\n  - Read\n---\nRead the code-reviewing skill.\n")
        self.write("commands/review.md", "Review the code.\n")
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.hooksPath", ".githooks")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def run_command(self, *args):
        environment = os.environ.copy()
        for name in tuple(environment):
            if name.startswith("GIT_"):
                environment.pop(name)
        return subprocess.run(args, cwd=self.root, env=environment, capture_output=True, text=True)

    def git(self, *args):
        result = self.run_command("git", *args)
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout

    def sync(self, mode, expected=0):
        result = self.run_command("python3", ".githooks/sync-runtime.py", mode)
        self.assertEqual(expected, result.returncode, result.stderr + result.stdout)
        return result

    def tree_state(self):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file() and ".git" not in path.relative_to(self.root).parts
        }

    def initial_commit(self):
        self.sync("--apply")
        self.git("add", "-A")
        self.git("commit", "-qm", "Fixture baseline")

    def test_generation_uses_project_paths_and_global_agent_pointers(self):
        self.sync("--apply")
        self.assertTrue((self.root / ".agents/skills/code-reviewing/SKILL.md").is_file())
        self.assertTrue((self.root / ".agents/skills/source-command-review/SKILL.md").is_file())
        self.assertFalse((self.root / ".codex/skills").exists())
        self.assertIn("AGENTS.md", (self.root / "AGENTS.md").read_text())
        self.assertIn("~/.codex/skills/code-reviewing/SKILL.md", (self.root / ".codex/agents/code-reviewer.toml").read_text())
        self.assertTrue((self.root / ".agents/skills/code-reviewing/scripts/run.sh").stat().st_mode & 0o111)
        before = self.tree_state()
        self.sync("--check")
        self.assertEqual(before, self.tree_state())
        self.assertFalse((self.root / ".codex/.sync").exists())

    def test_approved_project_templates_keep_converter_exceptions(self):
        self.write("skills/project-initialization/SKILL.md", "---\nname: project-initialization\ndescription: Initialize projects.\n---\n# Initialize\n")
        templates = {
            ".claude/settings.json": '{"permissions": {}}\n',
            ".mcp.json": '{"mcpServers": {}}\n',
            ".mcp.bot.json": '{"mcpServers": {}}\n',
        }
        for relative, content in templates.items():
            self.write("skills/project-initialization/assets/new-project/" + relative, content)
        self.sync("--apply")
        for relative, content in templates.items():
            target = self.root / ".agents/skills/project-initialization/assets/new-project" / relative
            self.assertEqual(content, target.read_text())
        before = self.tree_state()
        self.sync("--check")
        self.assertEqual(before, self.tree_state())
        for relative in ("settings.json", ".mcp.json"):
            with self.subTest(relative=relative):
                target = self.root / ".agents/skills/code-reviewing/scripts" / relative
                target.write_text("{}\n")
                before = self.tree_state()
                self.sync("--apply", 4)
                self.assertEqual(before, self.tree_state())
                target.unlink()
        self.write("skills/code-reviewing/scripts/settings.json", "{}\n")
        before = self.tree_state()
        self.sync("--apply", 4)
        self.assertEqual(before, self.tree_state())

    def test_drift_check_does_not_write_and_apply_refuses_foreign_file(self):
        self.sync("--apply")
        with (self.root / "skills/code-reviewing/SKILL.md").open("a") as handle:
            handle.write("New source instruction.\n")
        before = self.tree_state()
        self.sync("--check", 1)
        self.assertEqual(before, self.tree_state())
        self.sync("--apply")
        self.write(".codex/agents/code-reviewer.toml", "# Handwritten agent\n")
        before = self.tree_state()
        self.sync("--apply", 3)
        self.assertEqual(before, self.tree_state())

    def test_precommit_rejects_partial_sources_then_stages_generated_outputs(self):
        self.initial_commit()
        self.write("CLAUDE.md", "# Instructions\nNew instruction.\n")
        self.git("add", "CLAUDE.md")
        self.write("skills/code-reviewing/SKILL.md", "---\nname: code-reviewing\ndescription: Review code.\n---\nNew review instruction.\n")
        result = self.run_command(".githooks/pre-commit")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("partially staged", result.stderr)
        self.git("add", "skills")
        result = self.run_command(".githooks/pre-commit")
        self.assertEqual(0, result.returncode, result.stderr)
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        self.assertIn("AGENTS.md", staged)
        self.assertIn(".agents/skills/code-reviewing/SKILL.md", staged)
        self.assertFalse((self.root / ".codex/skills").exists())
        self.sync("--check")

    def test_precommit_stages_deleted_legacy_paths(self):
        self.initial_commit()
        self.write(".codex/skills/old/SKILL.md", "Legacy fixture snapshot\n")
        self.git("add", ".codex/skills")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Legacy fixture")
        before = self.tree_state()
        self.sync("--apply", 2)
        self.assertEqual(before, self.tree_state())
        shutil.rmtree(self.root / ".codex/skills")
        self.write("CLAUDE.md", "# Changed source\n")
        self.git("add", "CLAUDE.md")
        result = self.run_command(".githooks/pre-commit")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("D\t.codex/skills/old/SKILL.md", self.git("diff", "--cached", "--name-status"))

    def test_source_deletion_prunes_generated_skill_and_preserves_foreign_files(self):
        self.initial_commit()
        shutil.rmtree(self.root / "skills/code-reviewing")
        self.sync("--apply")
        self.assertFalse((self.root / ".agents/skills/code-reviewing").exists())
        self.write(".agents/skills/custom/SKILL.md", "# Handwritten skill\n")
        before = self.tree_state()
        self.sync("--apply", 3)
        self.assertEqual(before, self.tree_state())

    def test_untracked_asset_in_generated_skill_blocks_without_partial_writes(self):
        self.initial_commit()
        self.write(".agents/skills/code-reviewing/scripts/local-only.sh", "#!/bin/sh\necho local\n")
        self.write("CLAUDE.md", "# Pending generated instruction update\n")
        before = self.tree_state()
        index = (self.root / ".git/index").read_bytes()
        for mode in ("--check", "--apply"):
            with self.subTest(mode=mode):
                result = self.sync(mode, 3)
                self.assertIn("local-only.sh", result.stderr)
                self.assertEqual(before, self.tree_state())
                self.assertEqual(index, (self.root / ".git/index").read_bytes())

    def test_orphan_generated_definition_is_pruned_without_git_baseline(self):
        self.sync("--apply")
        self.write(".agents/skills/obsolete/SKILL.md", "<!-- Generated by sync-to-codex v1. Do not edit directly. -->\n# Obsolete\n")
        self.sync("--apply")
        self.assertFalse((self.root / ".agents/skills/obsolete").exists())

    def test_source_removed_asset_preserves_local_edits(self):
        self.initial_commit()
        (self.root / "skills/code-reviewing/scripts/run.sh").unlink()
        self.write(".agents/skills/code-reviewing/scripts/run.sh", "#!/bin/sh\necho local change\n")
        before = self.tree_state()
        for mode in ("--check", "--apply"):
            with self.subTest(mode=mode):
                result = self.sync(mode, 3)
                self.assertIn("scripts/run.sh", result.stderr)
                self.assertEqual(before, self.tree_state())

    def test_source_removed_clean_tracked_asset_is_pruned(self):
        self.initial_commit()
        (self.root / "skills/code-reviewing/scripts/run.sh").unlink()
        self.sync("--apply")
        self.assertFalse((self.root / ".agents/skills/code-reviewing/scripts/run.sh").exists())
        self.assertTrue((self.root / ".agents/skills/code-reviewing/SKILL.md").exists())
        self.sync("--check")

    def test_orphan_symlink_does_not_borrow_referent_generation_marker(self):
        self.initial_commit()
        link = self.root / ".agents/skills/code-reviewing/scripts/local-link"
        link.symlink_to("../SKILL.md")
        before = self.tree_state()
        self.sync("--apply", 4)
        self.assertTrue(link.is_symlink())
        self.assertEqual(before, self.tree_state())

    def test_ignored_initialization_archive_is_unchanged_by_project_guard(self):
        self.write("AGENTS.md", "# Manual existing instructions\nKeep these exact bytes.\n")
        self.write(".claude/skills/previous/SKILL.md", "---\nname: previous\ndescription: Previous skill.\n---\n# Previous\n")
        self.write("old/previous.txt", "Earlier local archive\n")
        self.git("add", "-A")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Existing project fixture")
        original = self.tree_state()
        skill = SOURCE / "skills/project-initialization"
        # Execute the actual published preservation/template step in the fixture.
        snippet = (skill / "SKILL.md").read_text().split("```bash\n", 1)[1].split("```", 1)[0]
        snippet = 'INIT_SKILL_DIR="$1"\n' + snippet + '\nprintf "\n/%s/\n" "$OLD_DIR" >> .gitignore\n'
        result = self.run_command("bash", "-c", snippet, "init-fixture", str(skill))
        self.assertEqual(0, result.returncode, result.stderr)
        archive = self.root / "old2"
        self.assertTrue(archive.is_dir())
        archived = {
            str(path.relative_to(archive)): (path.read_bytes(), path.stat().st_mode)
            for path in archive.rglob("*") if path.is_file()
        }
        self.assertEqual({path: value[:2] for path, value in original.items()}, archived)
        self.git("add", "-A")
        self.assertEqual("", self.git("ls-files", "--", "old2"))
        result = self.run_command(
            "python3", str(SOURCE / "scripts/codex-sync-git-guard.py"), "pre-commit",
            "--scope", "project", "--repo", str(self.root),
            "--sync-script", str(SOURCE / "scripts/sync-to-codex.sh"),
        )
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        after = {
            str(path.relative_to(archive)): (path.read_bytes(), path.stat().st_mode)
            for path in archive.rglob("*") if path.is_file()
        }
        self.assertEqual(archived, after)
        self.assertFalse((archive / ".agents").exists())
        self.assertFalse((archive / ".codex").exists())
        self.assertEqual("", self.git("ls-files", "--", "old2"))
        self.assertNotEqual("# Manual existing instructions\nKeep these exact bytes.\n", (self.root / "AGENTS.md").read_text())
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        self.assertIn("AGENTS.md", staged)
        self.assertIn(".agents/skills/project-knowledge/SKILL.md", staged)
        self.assertFalse(any(path.startswith("old2/") for path in staged))
        self.assertIn("D\t.claude/skills/previous/SKILL.md", self.git("diff", "--cached", "--name-status"))

    def test_prepush_requires_clean_files_and_checks_committed_drift(self):
        self.initial_commit()
        result = self.run_command(".githooks/pre-push")
        self.assertEqual(0, result.returncode, result.stderr)
        self.write("CLAUDE.md", "# Changed source\n")
        result = self.run_command(".githooks/pre-push")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("uncommitted changes", result.stderr)
        self.git("add", "CLAUDE.md")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Committed drift fixture")
        result = self.run_command(".githooks/pre-push")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("AGENTS.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
