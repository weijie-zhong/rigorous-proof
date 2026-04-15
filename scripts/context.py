"""
ContextBuilder: builds and caches the system-prompt blob for orchestrator phases.

The cached blob is passed as `--append-system-prompt` on every `claude -p` call.
Anthropic's prompt cache (5-minute TTL on identical prefixes) then makes
re-reads of the stable proof-work files near-free across all Phase 4/5/6/7
calls within a proof run.

Stable files (cached):
- 00_distilled.md          (problem statement, hypotheses, definitions)
- 00_strategy.md           (proof strategy and known results)
- 01_decomposition.md      (lemma list and dependency graph)
- status_log.md            (last K iteration entries only)

Excluded from the cache (would invalidate too often):
- proof_lemma_*.md         (mutated by Phase 4 and Phase 7)
- audit_lemma_*_iter_*.md  (written by Phase 5)
- fork_lemma_*_gap_*.md    (written by Phase 6)
- cold_read_audit.md       (written by Phase 9b)

Cache invalidation: the builder snapshots stable-file mtimes; on the next
`system_prompt()` call, any mtime drift forces a rebuild and bumps `version`.
Phase 7 also calls `invalidate()` explicitly because it may rewrite
`00_distilled.md` and definitely appends to `status_log.md`.
"""

from pathlib import Path
import threading

from prompts import SKILL_PREAMBLE


STABLE_FILES = (
    "00_distilled.md",
    "00_strategy.md",
    "01_decomposition.md",
    "status_log.md",
)

# How many trailing iteration entries of status_log.md to keep in the cached blob.
# The full file remains untouched on disk; this only bounds the cached prefix
# so the cache key stays stable as the log grows.
STATUS_LOG_KEEP = 5

# XML-style block tags used to label each file in the cached prompt
_BLOCK_TAGS = {
    "00_distilled.md": "distilled_problem",
    "00_strategy.md": "proof_strategy",
    "01_decomposition.md": "lemma_decomposition",
    "status_log.md": "recent_status_log",
}

_FOOTER = """\
The blocks above contain the stable context for this proof run. They are
already loaded — do NOT re-read `proof_work/00_distilled.md`,
`proof_work/00_strategy.md`, `proof_work/01_decomposition.md`, or
`proof_work/status_log.md` from disk. Use the content above directly.
You should still read per-lemma proof files, audit files, and fork files
when a phase asks you to.
"""


class ContextBuilder:
    """Builds and caches the system-prompt blob for orchestrator phases."""

    def __init__(self, proof_dir: Path):
        self.proof_dir = Path(proof_dir)
        self._lock = threading.Lock()
        self._cached_prompt: str | None = None
        self._cached_mtimes: tuple[float, ...] | None = None
        self._version = 0

    def system_prompt(self) -> str:
        """Return the cached system-prompt blob, rebuilding if any stable file changed."""
        with self._lock:
            current = self._mtimes()
            if self._cached_prompt is None or current != self._cached_mtimes:
                self._cached_prompt = self._build()
                self._cached_mtimes = current
                self._version += 1
            return self._cached_prompt

    def version(self) -> int:
        """Monotonic version counter; bumps on every rebuild."""
        return self._version

    def invalidate(self) -> None:
        """Force the next system_prompt() call to rebuild from disk."""
        with self._lock:
            self._cached_prompt = None
            self._cached_mtimes = None

    def _mtimes(self) -> tuple[float, ...]:
        """Snapshot mtimes of stable files; missing files contribute 0.0."""
        out = []
        for name in STABLE_FILES:
            p = self.proof_dir / name
            try:
                out.append(p.stat().st_mtime)
            except FileNotFoundError:
                out.append(0.0)
        return tuple(out)

    def _build(self) -> str:
        """Assemble the system-prompt blob from currently-existing stable files."""
        parts = [SKILL_PREAMBLE.rstrip(), ""]
        any_block = False
        for name in STABLE_FILES:
            p = self.proof_dir / name
            if not p.exists():
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            if name == "status_log.md":
                text = self._prune_status_log(text)
                if not text.strip():
                    continue
            tag = _BLOCK_TAGS[name]
            parts.append(f"<{tag}>")
            parts.append(text.rstrip())
            parts.append(f"</{tag}>")
            parts.append("")
            any_block = True

        if any_block:
            parts.append(_FOOTER.rstrip())
        return "\n".join(parts)

    @staticmethod
    def _prune_status_log(text: str) -> str:
        """
        Keep only the last STATUS_LOG_KEEP iteration entries.

        Entries are delimited by lines starting with `## Iteration `. Anything
        before the first such header (e.g. a file-level title) is dropped from
        the cached view; the full file stays untouched on disk.
        """
        marker = "\n## Iteration "
        # Normalize so an entry at the very top is also detected
        scan = "\n" + text
        positions = []
        start = 0
        while True:
            idx = scan.find(marker, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + 1

        if not positions:
            return text

        if len(positions) <= STATUS_LOG_KEEP:
            kept_start = positions[0]
        else:
            kept_start = positions[-STATUS_LOG_KEEP]

        # +1 to skip the leading "\n" we prepended for scanning
        return scan[kept_start + 1:].lstrip("\n")
