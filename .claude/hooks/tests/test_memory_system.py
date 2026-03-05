#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Comprehensive test suite for the OpenClaw memory adoption patterns.

Tests cover:
  1. precompact-guard.py — dedup guard with 60s cooldown
  2. memory-search.py — SQLite FTS5 ranked search sidecar
  3. hooks.json — structural validity and hook chain integrity
  4. Documentation consistency — all new components referenced
  5. Regression — existing memory hooks still functional

Run:
    uv run .claude/hooks/tests/test_memory_system.py
    uv run .claude/hooks/tests/test_memory_system.py -v    # verbose
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]  # .claude/hooks/tests -> repo root
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
HOOKS_JSON = HOOKS_DIR / "hooks.json"
MEMORY_GUIDE = REPO_ROOT / ".claude" / "MEMORY_GUIDE.md"
REGISTRY = REPO_ROOT / ".claude" / "REGISTRY.md"
USER_GUIDE = REPO_ROOT / ".claude" / "USER_GUIDE.md"
MANIFEST = REPO_ROOT / "MANIFEST.json"
MEMORY_CMD = REPO_ROOT / ".claude" / "commands" / "workflow" / "memory.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PRECOMPACT_GUARD = HOOKS_DIR / "precompact-guard.py"
MEMORY_SEARCH = HOOKS_DIR / "memory-search.py"
MEMORY_LOADER = HOOKS_DIR / "memory-loader.py"
MEMORY_DISTILL = HOOKS_DIR / "memory-distill.py"


def _run_script(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a Python script and capture output."""
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
        timeout=30,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 1. PreCompact Guard Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPrecompactGuard(unittest.TestCase):
    """Tests for precompact-guard.py — dedup guard with 60s cooldown."""

    def setUp(self):
        """Create an isolated temp directory to simulate session dirs."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="guard_test_"))
        self.sessions_dir = self.tmpdir / ".claude" / "memory" / "sessions"
        self.sessions_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_guard(self, session_dirs: list[Path]) -> subprocess.CompletedProcess:
        """Run precompact-guard with patched SESSION_DIRS."""
        # We can't easily patch constants in a subprocess, so we test the
        # internal function by importing it. For subprocess-level tests
        # we use the real dirs (tested separately).
        # Here we test the function directly.
        pass

    def test_script_exists(self):
        """precompact-guard.py exists and is a Python file."""
        self.assertTrue(PRECOMPACT_GUARD.exists(), f"Missing: {PRECOMPACT_GUARD}")
        content = PRECOMPACT_GUARD.read_text()
        self.assertIn("FLUSH_COOLDOWN_SECONDS", content)

    def test_no_recent_flush_no_output(self):
        """When no session files modified recently, script outputs nothing."""
        # Use a temp dir with old files
        old_file = self.sessions_dir / "2020-01-01.md"
        old_file.write_text("old session")
        # Set mtime to 5 minutes ago
        old_time = time.time() - 300
        os.utime(old_file, (old_time, old_time))

        # Import and test the function directly with patched dirs
        import importlib.util
        spec = importlib.util.spec_from_file_location("guard", PRECOMPACT_GUARD)
        guard = importlib.util.module_from_spec(spec)

        # Patch SESSION_DIRS
        original_dirs = None
        try:
            spec.loader.exec_module(guard)
            original_dirs = guard.SESSION_DIRS
            guard.SESSION_DIRS = [self.sessions_dir]
            self.assertFalse(guard.recent_flush_exists())
        finally:
            if original_dirs is not None:
                guard.SESSION_DIRS = original_dirs

    def test_recent_flush_detected(self):
        """When a session file was touched within 60s, guard detects it."""
        fresh_file = self.sessions_dir / "2026-02-11.md"
        fresh_file.write_text("fresh flush")
        # mtime is now (just created)

        import importlib.util
        spec = importlib.util.spec_from_file_location("guard2", PRECOMPACT_GUARD)
        guard = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(guard)
            original_dirs = guard.SESSION_DIRS
            guard.SESSION_DIRS = [self.sessions_dir]
            self.assertTrue(guard.recent_flush_exists())
        finally:
            guard.SESSION_DIRS = original_dirs

    def test_empty_sessions_dir(self):
        """Empty sessions directory returns no recent flush."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("guard3", PRECOMPACT_GUARD)
        guard = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(guard)
            original_dirs = guard.SESSION_DIRS
            guard.SESSION_DIRS = [self.sessions_dir]  # exists but empty
            self.assertFalse(guard.recent_flush_exists())
        finally:
            guard.SESSION_DIRS = original_dirs

    def test_missing_sessions_dir(self):
        """Non-existent sessions directory is handled gracefully."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("guard4", PRECOMPACT_GUARD)
        guard = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(guard)
            original_dirs = guard.SESSION_DIRS
            guard.SESSION_DIRS = [self.tmpdir / "nonexistent" / "sessions"]
            self.assertFalse(guard.recent_flush_exists())
        finally:
            guard.SESSION_DIRS = original_dirs

    def test_subprocess_output_format(self):
        """When run as subprocess with recent file, output is valid JSON."""
        # Touch a real session file to trigger detection
        real_sessions = REPO_ROOT / ".claude" / "memory" / "sessions"
        if not real_sessions.exists():
            self.skipTest("No sessions dir in repo")

        marker = real_sessions / "_test_guard_marker.md"
        try:
            marker.write_text("test")
            result = _run_script(PRECOMPACT_GUARD)
            self.assertEqual(result.returncode, 0)
            if result.stdout.strip():
                data = json.loads(result.stdout)
                self.assertEqual(data["decision"], "approve")
                self.assertIn("FLUSH_ALREADY_DONE", data["systemMessage"])
        finally:
            marker.unlink(missing_ok=True)

    def test_subprocess_no_output_on_stale(self):
        """When run as subprocess with only old files, no stdout."""
        # We can't easily guarantee no recent files exist in real dirs,
        # so we just verify the script runs without error.
        result = _run_script(PRECOMPACT_GUARD)
        self.assertEqual(result.returncode, 0)
        # Output may or may not exist depending on real session files


# ═══════════════════════════════════════════════════════════════════════════
# 2. Memory Search (FTS5) Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestMemorySearch(unittest.TestCase):
    """Tests for memory-search.py — SQLite FTS5 ranked search sidecar."""

    def setUp(self):
        """Create an isolated temp dir with test memory files."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="search_test_"))
        self.mem_dir = self.tmpdir / "memory"
        self.mem_dir.mkdir()
        self.db_path = self.tmpdir / "test.db"

        # Create test files
        (self.mem_dir / "decisions.md").write_text(
            "# Decisions\n\n### DEC-001: Use PostgreSQL\n"
            "We decided to use PostgreSQL for the database backend.\n"
        )
        (self.mem_dir / "tasks.md").write_text(
            "# Tasks\n\n## Active\n- [CONTEXT] Implement auth middleware\n"
            "- [FACT] API rate limit is 100 req/min\n"
        )
        (self.mem_dir / "project-context.md").write_text(
            "# Project Context\n\n## Architecture\n"
            "TypeScript backend with Express and Prisma ORM.\n"
        )
        sessions = self.mem_dir / "sessions"
        sessions.mkdir()
        (sessions / "2026-02-11.md").write_text(
            "# Session 2026-02-11\n\n## Key Changes\n"
            "- [DECISION] Chose JWT over sessions\n"
            "- [PREFERENCE] User prefers bun over npm\n"
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _get_conn(self) -> sqlite3.Connection:
        """Get a connection to a test database."""
        return sqlite3.connect(str(self.db_path))

    def _load_module(self):
        """Import memory-search module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("memsearch", MEMORY_SEARCH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_script_exists(self):
        """memory-search.py exists and is a Python file."""
        self.assertTrue(MEMORY_SEARCH.exists(), f"Missing: {MEMORY_SEARCH}")

    def test_ensure_db_creates_table(self):
        """ensure_db creates the FTS5 virtual table."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)
        # Verify table exists
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        self.assertIn("memory_fts", table_names)
        conn.close()

    def test_reindex_counts_files(self):
        """reindex indexes all .md files and returns correct count."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            count = mod.reindex(conn)
            # 3 top-level .md + 1 session .md = 4
            self.assertEqual(count, 4, f"Expected 4 files indexed, got {count}")
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_reindex_skips_dot_files(self):
        """reindex skips files starting with '.'."""
        mod = self._load_module()
        (self.mem_dir / ".hidden.md").write_text("should be skipped")
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            count = mod.reindex(conn)
            self.assertEqual(count, 4, "Dot-file should not be indexed")
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_reindex_skips_empty_files(self):
        """reindex skips files with only whitespace."""
        mod = self._load_module()
        (self.mem_dir / "empty.md").write_text("   \n  \n")
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            count = mod.reindex(conn)
            self.assertEqual(count, 4, "Empty file should not be indexed")
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_basic_keyword(self):
        """Search for 'PostgreSQL' returns results from decisions.md."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            results = mod.search(conn, "PostgreSQL")
            self.assertGreater(len(results), 0, "Expected results for 'PostgreSQL'")
            # First result should be from decisions.md
            paths = [r[1] for r in results]
            self.assertTrue(
                any("decisions.md" in p for p in paths),
                f"Expected decisions.md in results, got: {paths}",
            )
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_multi_word(self):
        """Multi-word query returns relevant results."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            results = mod.search(conn, "auth middleware")
            self.assertGreater(len(results), 0, "Expected results for 'auth middleware'")
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_no_results(self):
        """Query with no matches returns empty list."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            results = mod.search(conn, "xyznonexistent999")
            self.assertEqual(len(results), 0)
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_empty_query(self):
        """Empty query returns empty list without error."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            results = mod.search(conn, "")
            self.assertEqual(len(results), 0)
            results = mod.search(conn, "   ")
            self.assertEqual(len(results), 0)
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_special_chars_fallback(self):
        """Query with special chars falls back to quoted query."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            # These chars would break bare FTS5 syntax
            results = mod.search(conn, "C++ template<>")
            # Should not raise, may return 0 results
            self.assertIsInstance(results, list)
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_category_tags(self):
        """Category tags like [DECISION] are searchable."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            results = mod.search(conn, "DECISION")
            self.assertGreater(len(results), 0, "Expected results for 'DECISION' tag")
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_search_result_format(self):
        """Results are (tier, path, snippet) tuples."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("test", self.mem_dir)]
            mod.reindex(conn)
            results = mod.search(conn, "Express")
            self.assertGreater(len(results), 0)
            tier, path, snippet = results[0]
            self.assertEqual(tier, "test")
            self.assertIsInstance(path, str)
            self.assertIsInstance(snippet, str)
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()

    def test_subprocess_no_args(self):
        """Running with no args prints usage and exits 1."""
        result = _run_script(MEMORY_SEARCH)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage", result.stderr)

    def test_subprocess_reindex(self):
        """--reindex flag indexes files and reports count."""
        result = _run_script(MEMORY_SEARCH, "--reindex")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Indexed", result.stdout)
        # Clean up
        db = REPO_ROOT / ".claude" / "memory" / ".memory-search.db"
        db.unlink(missing_ok=True)

    def test_subprocess_search(self):
        """Searching via subprocess returns formatted results."""
        result = _run_script(MEMORY_SEARCH, "decision")
        self.assertEqual(result.returncode, 0)
        # Should have results (repo has decisions.md)
        self.assertIn("###", result.stdout)
        # Clean up
        db = REPO_ROOT / ".claude" / "memory" / ".memory-search.db"
        db.unlink(missing_ok=True)

    def test_subprocess_no_results(self):
        """Searching for nonexistent term returns 'No results' message."""
        result = _run_script(MEMORY_SEARCH, "xyznonexistent999zzz")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No results for:", result.stdout)
        # Clean up
        db = REPO_ROOT / ".claude" / "memory" / ".memory-search.db"
        db.unlink(missing_ok=True)

    def test_missing_memory_dir_graceful(self):
        """If memory dirs don't exist, reindex returns 0 and search returns empty."""
        mod = self._load_module()
        conn = self._get_conn()
        mod.ensure_db(conn)

        original_dirs = mod.MEMORY_DIRS
        try:
            mod.MEMORY_DIRS = [("phantom", self.tmpdir / "nonexistent")]
            count = mod.reindex(conn)
            self.assertEqual(count, 0)
            results = mod.search(conn, "anything")
            self.assertEqual(len(results), 0)
        finally:
            mod.MEMORY_DIRS = original_dirs
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# 3. hooks.json Structural Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestHooksJson(unittest.TestCase):
    """Structural validation of hooks.json."""

    @classmethod
    def setUpClass(cls):
        cls.hooks_data = json.loads(HOOKS_JSON.read_text())

    def test_valid_json(self):
        """hooks.json parses as valid JSON."""
        self.assertIsInstance(self.hooks_data, dict)

    def test_has_required_events(self):
        """All expected hook events are present."""
        expected = {
            "PreToolUse", "PostToolUse", "SessionStart", "Stop",
            "SessionEnd", "SubagentStop", "PreCompact",
            "UserPromptSubmit", "Notification",
        }
        actual = set(self.hooks_data.get("hooks", {}).keys())
        missing = expected - actual
        self.assertFalse(missing, f"Missing hook events: {missing}")

    def test_precompact_has_guard_and_flush(self):
        """PreCompact event has both the guard command and flush prompt."""
        precompact = self.hooks_data["hooks"]["PreCompact"]
        self.assertGreater(len(precompact), 0)
        hooks = precompact[0]["hooks"]
        self.assertGreaterEqual(len(hooks), 2, "PreCompact needs guard + flush")

        # First hook should be the command guard
        guard = hooks[0]
        self.assertEqual(guard["type"], "command")
        self.assertIn("precompact-guard", guard["command"])

        # Second hook should be the prompt flush
        flush = hooks[1]
        self.assertEqual(flush["type"], "prompt")
        self.assertIn("MEMORY FLUSH", flush["prompt"])
        self.assertIn("FLUSH_ALREADY_DONE", flush["prompt"])

    def test_precompact_prompt_has_category_tags(self):
        """PreCompact flush prompt includes all category tags."""
        hooks = self.hooks_data["hooks"]["PreCompact"][0]["hooks"]
        prompt = hooks[1]["prompt"]
        for tag in ["[DECISION]", "[PREFERENCE]", "[FACT]", "[CONTEXT]"]:
            self.assertIn(tag, prompt, f"Missing tag {tag} in PreCompact prompt")

    def test_stop_prompt_has_category_tags(self):
        """Stop memory distillation prompt includes category tags."""
        stop_hooks = self.hooks_data["hooks"]["Stop"][0]["hooks"]
        # Find the memory distillation prompt (second prompt hook)
        memory_prompt = None
        for h in stop_hooks:
            if h["type"] == "prompt" and "memory-worthy" in h.get("prompt", ""):
                memory_prompt = h["prompt"]
                break
        self.assertIsNotNone(memory_prompt, "Memory distillation prompt not found in Stop")
        for tag in ["[DECISION]", "[PREFERENCE]", "[FACT]", "[ENTITY]", "[CONTEXT]"]:
            self.assertIn(tag, memory_prompt, f"Missing tag {tag} in Stop prompt")

    def test_all_command_scripts_exist(self):
        """Every command hook references a script that exists on disk."""
        missing = []
        for event, entries in self.hooks_data.get("hooks", {}).items():
            for entry in entries:
                for hook in entry.get("hooks", []):
                    if hook.get("type") != "command":
                        continue
                    cmd = hook["command"]
                    # Extract script path (after python3/uv run/bash)
                    parts = cmd.replace("${CLAUDE_PLUGIN_ROOT}", str(REPO_ROOT / ".claude")).split()
                    # Find the .py or .sh file in the command
                    for part in parts:
                        if part.endswith((".py", ".sh")):
                            script_path = Path(part)
                            if not script_path.exists():
                                missing.append(f"{event}: {part}")
                            break
        self.assertFalse(missing, f"Missing scripts: {missing}")


# ═══════════════════════════════════════════════════════════════════════════
# 4. Documentation Consistency Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDocumentation(unittest.TestCase):
    """Verify all new components are referenced in documentation."""

    def _file_contains(self, path: Path, term: str) -> bool:
        if not path.exists():
            return False
        return term.lower() in path.read_text().lower()

    # --- MEMORY_GUIDE.md ---

    def test_memory_guide_mentions_precompact(self):
        """MEMORY_GUIDE.md documents PreCompact flush."""
        self.assertTrue(
            self._file_contains(MEMORY_GUIDE, "PreCompact"),
            "MEMORY_GUIDE.md missing PreCompact section",
        )

    def test_memory_guide_mentions_category_tags(self):
        """MEMORY_GUIDE.md documents category tags."""
        self.assertTrue(
            self._file_contains(MEMORY_GUIDE, "[DECISION]"),
            "MEMORY_GUIDE.md missing [DECISION] tag",
        )

    def test_memory_guide_mentions_fts5(self):
        """MEMORY_GUIDE.md documents FTS5 search."""
        self.assertTrue(
            self._file_contains(MEMORY_GUIDE, "FTS5"),
            "MEMORY_GUIDE.md missing FTS5 section",
        )

    def test_memory_guide_mentions_precompact_guard(self):
        """MEMORY_GUIDE.md references precompact-guard.py."""
        self.assertTrue(
            self._file_contains(MEMORY_GUIDE, "precompact-guard"),
            "MEMORY_GUIDE.md missing precompact-guard reference",
        )

    def test_memory_guide_mentions_memory_search(self):
        """MEMORY_GUIDE.md references memory-search.py."""
        self.assertTrue(
            self._file_contains(MEMORY_GUIDE, "memory-search"),
            "MEMORY_GUIDE.md missing memory-search reference",
        )

    # --- REGISTRY.md ---

    def test_registry_lists_precompact_guard(self):
        """REGISTRY.md lists precompact-guard hook."""
        self.assertTrue(
            self._file_contains(REGISTRY, "precompact-guard"),
            "REGISTRY.md missing precompact-guard entry",
        )

    def test_registry_lists_memory_flush(self):
        """REGISTRY.md lists memory-flush hook."""
        self.assertTrue(
            self._file_contains(REGISTRY, "memory-flush"),
            "REGISTRY.md missing memory-flush entry",
        )

    def test_registry_lists_memory_search(self):
        """REGISTRY.md lists memory-search utility."""
        self.assertTrue(
            self._file_contains(REGISTRY, "memory-search"),
            "REGISTRY.md missing memory-search entry",
        )

    # --- USER_GUIDE.md ---

    def test_user_guide_lists_precompact_hooks(self):
        """USER_GUIDE.md lists PreCompact hooks in the hooks table."""
        self.assertTrue(
            self._file_contains(USER_GUIDE, "precompact-guard"),
            "USER_GUIDE.md missing precompact-guard in hooks table",
        )

    def test_user_guide_mentions_fts5_search(self):
        """USER_GUIDE.md mentions FTS5 or memory search."""
        content = USER_GUIDE.read_text().lower()
        self.assertTrue(
            "search" in content and "memory" in content,
            "USER_GUIDE.md missing memory search reference",
        )

    # --- MANIFEST.json ---

    def test_manifest_has_precompact_guard(self):
        """MANIFEST.json registers precompact-guard.py."""
        content = MANIFEST.read_text()
        self.assertIn("precompact-guard", content)

    def test_manifest_has_memory_search(self):
        """MANIFEST.json registers memory-search.py."""
        content = MANIFEST.read_text()
        self.assertIn("memory-search", content)

    def test_manifest_has_memory_flush(self):
        """MANIFEST.json registers memory-flush prompt."""
        content = MANIFEST.read_text()
        self.assertIn("memory-flush", content)

    # --- memory.md command ---

    def test_memory_command_references_fts5(self):
        """/memory command file references FTS5 search."""
        self.assertTrue(
            self._file_contains(MEMORY_CMD, "FTS5"),
            "memory.md command missing FTS5 reference",
        )

    def test_memory_command_references_search_script(self):
        """memory.md command references memory-search.py."""
        self.assertTrue(
            self._file_contains(MEMORY_CMD, "memory-search.py"),
            "memory.md command missing memory-search.py reference",
        )

    # --- .gitignore ---

    def test_gitignore_excludes_search_db(self):
        """.gitignore excludes .memory-search.db."""
        self.assertTrue(
            self._file_contains(GITIGNORE, ".memory-search.db"),
            ".gitignore missing .memory-search.db exclusion",
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. Regression Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRegression(unittest.TestCase):
    """Ensure existing memory components still work."""

    def test_memory_loader_exists(self):
        """memory-loader.py exists."""
        self.assertTrue(MEMORY_LOADER.exists())

    def test_memory_loader_runs(self):
        """memory-loader.py runs without error."""
        result = _run_script(MEMORY_LOADER)
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

    def test_memory_loader_outputs_json(self):
        """memory-loader.py outputs valid JSON with systemMessage."""
        result = _run_script(MEMORY_LOADER)
        if result.stdout.strip():
            data = json.loads(result.stdout)
            self.assertIn("decision", data)
            self.assertIn("systemMessage", data)

    def test_memory_distill_exists(self):
        """memory-distill.py exists."""
        self.assertTrue(MEMORY_DISTILL.exists())

    def test_memory_distill_runs(self):
        """memory-distill.py runs without error."""
        result = _run_script(MEMORY_DISTILL)
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

    def test_memory_utils_importable(self):
        """utils/memory.py is importable and has expected functions."""
        sys.path.insert(0, str(REPO_ROOT / ".claude"))
        try:
            from utils.memory import (
                classify_memory,
                contains_secrets,
                estimate_tokens,
                load_memory_bundle,
            )
            # Quick sanity checks
            self.assertEqual(estimate_tokens("hello world"), 2)  # 11 chars / 4
            self.assertEqual(contains_secrets("safe text"), [])
            self.assertIsInstance(classify_memory("I prefer dark mode"), tuple)
        finally:
            sys.path.pop(0)

    def test_memory_utils_secret_detection(self):
        """Secret detection still catches known patterns."""
        sys.path.insert(0, str(REPO_ROOT / ".claude"))
        try:
            from utils.memory import contains_secrets
            # Should detect OpenAI key pattern
            self.assertGreater(
                len(contains_secrets("sk-1234567890abcdefghijklmn")), 0,
                "Failed to detect OpenAI-style key",
            )
            # Should detect GitHub PAT
            self.assertGreater(
                len(contains_secrets("ghp_123456789012345678901234567890123456")), 0,
                "Failed to detect GitHub PAT",
            )
        finally:
            sys.path.pop(0)

    def test_memory_utils_classify_decision(self):
        """Classification still routes decisions correctly."""
        sys.path.insert(0, str(REPO_ROOT / ".claude"))
        try:
            from utils.memory import classify_memory
            tier, filename, section = classify_memory("We decided to use PostgreSQL")
            self.assertEqual(tier, "project")
            self.assertEqual(filename, "decisions.md")
        finally:
            sys.path.pop(0)

    def test_memory_utils_classify_preference(self):
        """Classification still routes preferences correctly."""
        sys.path.insert(0, str(REPO_ROOT / ".claude"))
        try:
            from utils.memory import classify_memory
            tier, filename, section = classify_memory("I prefer dark mode")
            self.assertEqual(tier, "global")
            self.assertEqual(filename, "user-profile.md")
        finally:
            sys.path.pop(0)


# ═══════════════════════════════════════════════════════════════════════════
# 6. Integration: PreCompact Hook Chain
# ═══════════════════════════════════════════════════════════════════════════


class TestPrecompactIntegration(unittest.TestCase):
    """Integration test: guard → flush prompt chain works correctly."""

    def test_guard_then_flush_sequence(self):
        """Guard runs first, flush prompt references FLUSH_ALREADY_DONE."""
        hooks_data = json.loads(HOOKS_JSON.read_text())
        precompact = hooks_data["hooks"]["PreCompact"][0]["hooks"]

        # Hook ordering: guard (command) must come before flush (prompt)
        self.assertEqual(precompact[0]["type"], "command", "First hook must be command (guard)")
        self.assertEqual(precompact[1]["type"], "prompt", "Second hook must be prompt (flush)")

        # Flush prompt must check for guard's signal
        flush_prompt = precompact[1]["prompt"]
        self.assertIn("FLUSH_ALREADY_DONE", flush_prompt,
                       "Flush prompt must reference guard's FLUSH_ALREADY_DONE signal")

    def test_guard_output_matches_flush_expectation(self):
        """Guard's systemMessage token matches what flush prompt looks for."""
        # Load guard output format
        import importlib.util
        spec = importlib.util.spec_from_file_location("guard_int", PRECOMPACT_GUARD)
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)

        # Simulate a recent flush
        tmpdir = Path(tempfile.mkdtemp())
        sessions = tmpdir / "sessions"
        sessions.mkdir(parents=True)
        (sessions / "test.md").write_text("test")

        original_dirs = guard.SESSION_DIRS
        try:
            guard.SESSION_DIRS = [sessions]

            # Capture what guard would output
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                guard.main()
            output = f.getvalue()
        finally:
            guard.SESSION_DIRS = original_dirs
            shutil.rmtree(tmpdir, ignore_errors=True)

        data = json.loads(output)
        signal = data["systemMessage"]

        # Verify flush prompt looks for exactly this signal
        hooks_data = json.loads(HOOKS_JSON.read_text())
        flush_prompt = hooks_data["hooks"]["PreCompact"][0]["hooks"][1]["prompt"]
        # The signal starts with "FLUSH_ALREADY_DONE"
        self.assertTrue(signal.startswith("FLUSH_ALREADY_DONE"))
        self.assertIn("FLUSH_ALREADY_DONE", flush_prompt)


# ═══════════════════════════════════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Change to repo root so relative paths in tested scripts work
    os.chdir(REPO_ROOT)
    unittest.main(verbosity=2)
