#!/usr/bin/env python3
"""
Rigorous-proof orchestrator.

Manages the entire proof workflow (Phases 0–9) by dispatching each phase as a
separate `claude -p` call, tracking progress via a state file, and
maintaining a heartbeat to detect stalled agents.

The user's initial Claude prompt writes proof_work/00_user_input.md, then
launches this script. The orchestrator handles everything from there.

Phase mapping:
  0 — Environment check, create proof_work/
  1 — Distill problem from user input -> 00_distilled.md
  2 — Literature survey (optional, difficult only) -> 00_survey.md
  3 — Strategy + decomposition -> 00_strategy.md + 01_decomposition.md
  4 — Proof execution (one lemma at a time) -> proof_lemma_k.md
  5 — Self-audit (hostile referee) -> audit_lemma_k_iter_n.md
  6 — Gap resolution and forking -> fork_lemma_k_gap_j.md
  7 — Revision -> overwrites proof_lemma_k.md
  8 — Dual loop (inner: 5-7 per lemma; outer: back to 3)
  9 — Cold read assembly -> final_proof.md, proof_journal.md
 10 — Done sentinel

Usage:
    python orchestrate.py                  # start in terminal mode (default)
    python orchestrate.py --no-terminal    # run in current session instead
    python orchestrate.py --resume         # resume after disruption
    python orchestrate.py --max-effort     # force iterative loop (auto-enabled for difficult problems)
    python orchestrate.py --work-dir DIR   # specify working directory
"""

import argparse
import concurrent.futures
import json
import os
import random
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure stdout can handle Unicode (arrows, checkmarks, etc.) on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from prompts import (
    PHASE_1_DISTILL,
    PHASE_2_SURVEY,
    PHASE_3_STRATEGY_DECOMPOSITION,
    PHASE_4_PROOF_LEMMA,
    PHASE_5_AUDIT_LEMMA,
    PHASE_6_GAP_ANALYSIS,
    PHASE_7_REVISION,
    PHASE_9B_COLD_READ,
    PHASE_9C_FINAL_PROOF,
    PHASE_9D_JOURNAL,
    SKILL_PREAMBLE,
    format_prompt,
    get_dependency_files_text,
)
from context import ContextBuilder


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_STALE_THRESHOLD = 120  # seconds
FORK_TIMEOUT = 600  # seconds (Phase 6 user input)
FORK_FAILURE_THRESHOLD = 3  # after N failures, auto-default to A (accept stronger assumption)
MAX_INNER_ITERATIONS = 7  # Phase 8 inner audit loop cap
MAX_OUTER_ITERATIONS = 3  # Phase 8 outer re-strategization loop cap

# Default concurrency for Phase 4 (prove) and Phase 5 (audit).
# 0 is a sentinel meaning "unlimited" — every independent lemma in a
# dependency-DAG wave runs in its own worker (max_workers = len(wave)).
# Pass --parallel 1 to force the prior fully sequential behavior, or
# --parallel N to cap concurrency at N workers per wave.
PARALLEL_DEFAULT = 0
PARALLEL_UNLIMITED = 0

# Retry defaults — covers both rate limits (seconds) and usage limits (~5h reset)
RETRY_MAX_ATTEMPTS = 20          # enough for 5h at ~15 min avg intervals
RETRY_FALLBACK_DELAY = 300       # 5 min initial (used only when no retry-after is parsed)
RETRY_MAX_DELAY = 1800           # 30 min cap per individual fallback wait
RETRY_MAX_TOTAL_WAIT = 19800     # 5.5 hours — covers a full usage-limit reset cycle
RETRY_JITTER_FACTOR = 0.25      # +/- 25% jitter on fallback only

RETRYABLE_PATTERNS = [
    "rate limit", "rate_limit", "overloaded", "429",
    "quota", "usage limit", "too many requests", "capacity",
    "try again", "temporarily unavailable", "service unavailable",
    "503", "529",
]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# File-based logging: set by init_log_file(), used as fallback when console
# output is unreliable (e.g., CREATE_NEW_CONSOLE windows on some systems).
_log_file_path: Path | None = None

# Lock that serializes log() calls so parallel workers don't interleave bytes
# in the console or in the file log.
_log_lock = threading.Lock()

# Thread-local prefix that parallel workers set (e.g. "[L3] ") so each line
# from a per-lemma worker is identifiable.
_log_local = threading.local()


def init_log_file(proof_dir: Path) -> None:
    """Enable persistent file logging alongside console output."""
    global _log_file_path
    _log_file_path = proof_dir / "_orchestrator_console.log"


def set_log_prefix(prefix: str | None) -> None:
    """Set a per-thread prefix prepended to every log line from this thread."""
    if prefix is None:
        if hasattr(_log_local, "prefix"):
            del _log_local.prefix
    else:
        _log_local.prefix = prefix


def log(msg: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = getattr(_log_local, "prefix", "")
    line = f"[{timestamp}] {prefix}{msg}"
    with _log_lock:
        try:
            print(line, flush=True)
        except OSError:
            pass
        if _log_file_path:
            try:
                with open(_log_file_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except OSError:
                pass


def parse_json_from_output(text: str) -> dict | None:
    """Try to extract a JSON object from Claude's output."""
    # Look for JSON in the result field of --output-format json
    try:
        outer = json.loads(text)
        if isinstance(outer, dict) and "result" in outer:
            text = outer["result"]
    except (json.JSONDecodeError, TypeError):
        pass

    # Try to find a JSON block in the text
    # First try the whole text
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Look for ```json blocks
    match = re.search(r"```json\s*\n(.*?)\n\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Look for any { ... } block
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

class OrchestratorState:
    """Manages proof_work/orchestrator_state.json. Thread-safe."""

    def __init__(self, proof_dir: Path):
        self.path = proof_dir / "orchestrator_state.json"
        self._lock = threading.RLock()
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                log("Warning: state file corrupt, will detect phase from files")
                return {}
        return {}

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def get(self, key: str, default=None):
        with self._lock:
            return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        with self._lock:
            self.data[key] = value
            self.save()

    def update_heartbeat(self) -> None:
        with self._lock:
            self.data["heartbeat"] = now_iso()
            self.save()

    def add_concurrent_lemma(self, lemma_k: int) -> None:
        with self._lock:
            current = list(self.data.get("concurrent_lemmas", []))
            if lemma_k not in current:
                current.append(lemma_k)
            self.data["concurrent_lemmas"] = sorted(current)
            self.save()

    def remove_concurrent_lemma(self, lemma_k: int) -> None:
        with self._lock:
            current = [k for k in self.data.get("concurrent_lemmas", []) if k != lemma_k]
            self.data["concurrent_lemmas"] = current
            self.save()

    def is_heartbeat_stale(self) -> bool:
        with self._lock:
            hb = self.data.get("heartbeat")
        if not hb:
            return True
        try:
            hb_time = datetime.fromisoformat(hb)
            age = (datetime.now(timezone.utc) - hb_time).total_seconds()
            return age > HEARTBEAT_STALE_THRESHOLD
        except (ValueError, TypeError):
            return True


# ---------------------------------------------------------------------------
# Heartbeat thread
# ---------------------------------------------------------------------------

class HeartbeatThread:
    """Background thread that updates the heartbeat in the state file."""

    def __init__(self, state: OrchestratorState):
        self.state = state
        self._stop = threading.Event()
        self._thread = None

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.state.update_heartbeat()
            except OSError:
                pass
            self._stop.wait(HEARTBEAT_INTERVAL)


# ---------------------------------------------------------------------------
# Phase detection from files
# ---------------------------------------------------------------------------

def detect_phase_from_files(proof_dir: Path) -> tuple[int, int, int]:
    """
    Determine (phase, lemma_k, iteration) by examining proof_work/ files.
    Returns the phase to START (not the last completed phase).
    """
    # No proof_work dir or empty → fresh start
    if not proof_dir.exists():
        return (0, 0, 0)

    # Check final_proof.md → done
    if (proof_dir / "final_proof.md").exists():
        return (10, 0, 0)  # sentinel: done

    # No distilled file → need Phase 1
    if not (proof_dir / "00_distilled.md").exists():
        # Check if user input exists → Phase 1, otherwise Phase 0
        if (proof_dir / "00_user_input.md").exists():
            return (1, 0, 0)
        return (0, 0, 0)

    # No strategy or decomposition → Phase 3
    if not (proof_dir / "00_strategy.md").exists() or \
       not (proof_dir / "01_decomposition.md").exists():
        return (3, 0, 0)

    # Check cold_read_audit.md → Phase 9c
    if (proof_dir / "cold_read_audit.md").exists():
        return (9, 0, 0)

    # Parse lemma count from decomposition
    lemma_count = _count_lemmas(proof_dir)
    if lemma_count == 0:
        return (3, 0, 0)  # re-do strategy + decomposition

    # Find first lemma without a proof file → Phase 4
    for k in range(1, lemma_count + 1):
        if not (proof_dir / f"proof_lemma_{k}.md").exists():
            return (4, k, 1)

    # All proofs exist. Check audits.
    for k in range(1, lemma_count + 1):
        latest_iter = _latest_audit_iteration(proof_dir, k)
        if latest_iter == 0:
            return (5, k, 1)  # no audit yet

        # Check if audit passed
        audit_file = proof_dir / f"audit_lemma_{k}_iter_{latest_iter}.md"
        if _audit_has_failures(audit_file):
            # Check if revision already happened for this iteration
            proof_file = proof_dir / f"proof_lemma_{k}.md"
            if proof_file.exists():
                text = proof_file.read_text(encoding="utf-8")
                iter_match = re.search(r"Iteration:\s*(\d+)", text)
                if iter_match and int(iter_match.group(1)) > latest_iter:
                    continue  # revision done, move to next lemma

            # Check for fork files (gap analysis done?)
            fork_files = list(proof_dir.glob(f"fork_lemma_{k}_gap_*.md"))
            if not fork_files:
                return (6, k, latest_iter)  # needs gap analysis
            else:
                return (7, k, latest_iter)  # needs revision

    # All audits pass → Phase 9
    return (9, 0, 0)


def _count_lemmas(proof_dir: Path) -> int:
    """Count lemmas from decomposition file or proof files."""
    decomp = proof_dir / "01_decomposition.md"
    if decomp.exists():
        text = decomp.read_text(encoding="utf-8")
        # Count "Lemma N" patterns (handles markdown headings like ### Lemma 1,
        # bold like **Lemma 1**, and plain Lemma 1)
        matches = re.findall(r"(?:^|\n)\s*(?:#{1,6}\s+)?\*{0,2}Lemma\s+(\d+)", text, re.IGNORECASE)
        if matches:
            return max(int(m) for m in matches)
    # Fallback: count proof_lemma_*.md files
    files = list(proof_dir.glob("proof_lemma_*.md"))
    if files:
        nums = []
        for f in files:
            m = re.search(r"proof_lemma_(\d+)\.md", f.name)
            if m:
                nums.append(int(m.group(1)))
        return max(nums) if nums else 0
    return 0


def _latest_audit_iteration(proof_dir: Path, lemma_k: int) -> int:
    """Find the highest iteration number for audit files of a lemma."""
    files = list(proof_dir.glob(f"audit_lemma_{lemma_k}_iter_*.md"))
    if not files:
        return 0
    iters = []
    for f in files:
        m = re.search(r"iter_(\d+)\.md", f.name)
        if m:
            iters.append(int(m.group(1)))
    return max(iters) if iters else 0


def _audit_has_failures(audit_file: Path) -> bool:
    """Check if an audit file contains any ❌ marks."""
    if not audit_file.exists():
        return True
    text = audit_file.read_text(encoding="utf-8")
    return "❌" in text


def _parse_lemma_dependencies(proof_dir: Path, lemma_k: int) -> list[int]:
    """Parse dependency list for a lemma from the decomposition file."""
    decomp = proof_dir / "01_decomposition.md"
    if not decomp.exists():
        return []
    text = decomp.read_text(encoding="utf-8")
    # Look for "Lemma k" section and its "Depends on" line
    pattern = rf"Lemma\s+{lemma_k}\b.*?Depends\s+on[:\s]*(.*?)(?:\n\s*\n|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    deps_text = match.group(1)
    dep_nums = re.findall(r"(?:Lemma\s+)?(\d+)", deps_text)
    return [int(d) for d in dep_nums if int(d) != lemma_k]


def _get_difficulty(proof_dir: Path) -> str:
    """Parse difficulty from 00_distilled.md. Returns 'easy', 'moderate', or 'difficult'."""
    distilled = proof_dir / "00_distilled.md"
    if not distilled.exists():
        return "moderate"
    text = distilled.read_text(encoding="utf-8").lower()
    # Look for explicit difficulty classification
    m = re.search(r"difficulty[^:]*:\s*\*?\*?(difficult|moderate|easy)", text, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    # Fallback heuristics
    if "difficult" in text:
        return "difficult"
    if "easy" in text:
        return "easy"
    return "moderate"


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------

def _is_retryable_error(stderr: str) -> bool:
    """Check if a claude CLI error is transient and worth retrying."""
    lower = stderr.lower()
    return any(p in lower for p in RETRYABLE_PATTERNS)


def _parse_retry_after(stderr: str) -> float | None:
    """
    Try to extract the recommended wait time from stderr.

    Looks for (in priority order):
    - "retry-after: 30" or "Retry-After: 30" (HTTP header style)
    - "retry in 30 seconds" / "try again in 30s" (prose style)
    - RFC 3339 timestamps near "reset" keywords

    Returns seconds to wait, or None if unparseable.
    """
    # Pattern 1: retry-after header (exact seconds)
    m = re.search(r'retry[- ]after[:\s]+(\d+)', stderr, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # Pattern 2: "retry in N seconds" / "try again in N seconds"
    m = re.search(r'(?:retry|try again)\s+in\s+(\d+)\s*s', stderr, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # Pattern 3: RFC 3339 timestamp near "reset"
    m = re.search(
        r'reset[^"]*?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))',
        stderr, re.IGNORECASE,
    )
    if m:
        try:
            reset_time = datetime.fromisoformat(m.group(1).replace('Z', '+00:00'))
            delta = (reset_time - datetime.now(timezone.utc)).total_seconds()
            if delta > 0:
                return delta + 2  # +2s safety margin; no cap — usage limits can be hours
        except (ValueError, TypeError):
            pass

    return None


# ---------------------------------------------------------------------------
# Claude CLI invocation
# ---------------------------------------------------------------------------

def invoke_claude(prompt: str, system_prompt: str | None = None,
                  cwd: Path | str | None = None,
                  max_retries: int = RETRY_MAX_ATTEMPTS,
                  max_total_wait: float = RETRY_MAX_TOTAL_WAIT) -> str:
    """
    Invoke `claude -p` and return the output text.

    On transient errors (rate limits, usage limits), automatically retries
    with parsed retry-after timing or exponential backoff as fallback.
    Prints the full agent output to stdout so the user can follow along.
    """
    cmd = ["claude", "-p", "--model", "opus", "--output-format", "json"]
    if system_prompt:
        cmd.extend(["--append-system-prompt", system_prompt])
    cmd.append(prompt)

    log(f"Invoking claude ({len(prompt)} chars prompt)...")

    total_waited = 0.0

    # max_retries=0 means 1 attempt with no retries (--no-retry behavior)
    # On Windows, prevent each subprocess from opening a new console window
    extra_kwargs: dict = {}
    if sys.platform == "win32":
        extra_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    for attempt in range(1 + max_retries):
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            **extra_kwargs,
        )

        if result.returncode == 0:
            break

        stderr = result.stderr.strip() if result.stderr else ""
        stdout_text = result.stdout.strip() if result.stdout else ""
        error_desc = stderr or stdout_text or "(no output)"

        if not _is_retryable_error(stderr) and not _is_retryable_error(stdout_text):
            # Non-zero exit with no stderr is likely a transient failure
            # (e.g. usage limit with --output-format json produces no stderr)
            if not stderr:
                log(f"  claude exited with code {result.returncode} and no stderr "
                    f"— treating as retryable")
            else:
                raise RuntimeError(
                    f"claude exited with code {result.returncode}: {error_desc}")

        if attempt >= max_retries:
            if max_retries > 0:
                raise RuntimeError(
                    f"claude failed after {max_retries} retries "
                    f"(waited {total_waited:.0f}s total): {error_desc}")
            else:
                raise RuntimeError(
                    f"claude exited with code {result.returncode}: {error_desc}")

        # Determine wait time: parse from error first, fallback to backoff
        # Check both stderr and stdout since CLI may report limits in either
        combined_for_parse = f"{stderr}\n{stdout_text}"
        parsed_delay = _parse_retry_after(combined_for_parse)
        if parsed_delay is not None:
            delay = parsed_delay  # exact time from server — no cap, no jitter
            source = "retry-after"
        else:
            # Exponential backoff with jitter
            delay = RETRY_FALLBACK_DELAY * (2 ** attempt)
            delay = min(delay, RETRY_MAX_DELAY)
            delay *= 1 + RETRY_JITTER_FACTOR * (2 * random.random() - 1)
            source = "backoff"

        if total_waited + delay > max_total_wait:
            raise RuntimeError(
                f"claude retry budget exhausted "
                f"({total_waited:.0f}s / {max_total_wait:.0f}s max): {stderr}")

        # Human-readable wait time
        if delay >= 3600:
            wait_str = f"{delay / 3600:.1f}h"
        elif delay >= 60:
            wait_str = f"{delay / 60:.0f}m"
        else:
            wait_str = f"{delay:.0f}s"

        log(f"  Rate limited (attempt {attempt + 1}/{1 + max_retries}). "
            f"Waiting {wait_str} ({source}). Total waited: {total_waited / 60:.0f}m")

        # Sleep in chunks, printing progress for long waits
        remaining = delay
        while remaining > 0:
            chunk = min(remaining, 60)
            time.sleep(chunk)
            remaining -= chunk
            total_waited += chunk
            if remaining > 0:
                if remaining >= 3600:
                    rem_str = f"{remaining / 3600:.1f}h"
                elif remaining >= 60:
                    rem_str = f"{remaining / 60:.0f}m"
                else:
                    rem_str = f"{remaining:.0f}s"
                log(f"    ... {rem_str} remaining until next retry")

    output = result.stdout.strip()

    # Extract the result text from JSON output
    result_text = output
    try:
        parsed = json.loads(output)
        if isinstance(parsed, dict) and "result" in parsed:
            result_text = parsed["result"]
    except (json.JSONDecodeError, TypeError):
        pass

    return result_text


# ---------------------------------------------------------------------------
# User input with timeout (Phase 6)
# ---------------------------------------------------------------------------

def prompt_user_fork_decision(gap_summary: str, timeout: int = FORK_TIMEOUT,
                              default: str = "B") -> tuple[str, bool]:
    """
    Present fork options to the user with a timeout.
    Returns (choice letter, was_auto_selected).
    *default* is the choice made when the user doesn't respond in time.
    """
    default = default.upper()
    option_labels = {
        "A": "Accept the stronger assumption and continue",
        "B": "Try the alternative proof strategy",
        "C": "Prove the weaker conclusion instead",
        "D": "Abandon this lemma and restructure",
    }

    print("\n" + "=" * 60)
    print("FORK DECISION REQUIRED")
    print("=" * 60)
    print(gap_summary)
    print()
    print("Options:")
    for letter, label in option_labels.items():
        suffix = " (default)" if letter == default else ""
        print(f"  ({letter}) {label}{suffix}")
    print(f"\nYou have {timeout} seconds to respond. Default: {default}")
    print()

    result = {"choice": None}

    def read_input():
        try:
            choice = input("Your choice [A/B/C/D]: ").strip().upper()
            if choice in ("A", "B", "C", "D"):
                result["choice"] = choice
        except EOFError:
            pass

    thread = threading.Thread(target=read_input, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if result["choice"] is None:
        log(f"No response after {timeout}s — auto-selecting {default}")
        return (default, True)

    return (result["choice"], False)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class ProofOrchestrator:
    def __init__(self, work_dir: Path, max_effort: bool = False,
                 max_retries: int = RETRY_MAX_ATTEMPTS,
                 max_total_wait: float = RETRY_MAX_TOTAL_WAIT,
                 parallel: int = PARALLEL_DEFAULT):
        self.work_dir = work_dir
        self.proof_dir = work_dir / "proof_work"
        self.max_effort = max_effort
        self.max_retries = max_retries
        self.max_total_wait = max_total_wait
        # parallel == 0 → unlimited (one worker per lemma in each wave).
        # parallel == 1 → fully sequential (matches pre-optimization behavior).
        # parallel >= 2 → cap at N concurrent workers per wave.
        self.parallel = max(0, int(parallel))
        self.state = OrchestratorState(self.proof_dir)
        self.heartbeat = HeartbeatThread(self.state)
        self.context = ContextBuilder(self.proof_dir)
        self.lemma_count = 0

    def run(self) -> None:
        """Main entry point — detect phase and run from there."""
        # Ensure proof_work/ exists (Phase 0 creates it, but for resume we need state)
        self.proof_dir.mkdir(parents=True, exist_ok=True)

        # Enable file-based logging for debugging
        init_log_file(self.proof_dir)

        # Detect where to resume
        phase, lemma_k, iteration = self._detect_resume_point()

        if phase == 10:
            log("Proof already complete (final_proof.md exists).")
            return

        log(f"Starting from Phase {phase}" +
            (f", Lemma {lemma_k}" if lemma_k else "") +
            (f", Iteration {iteration}" if iteration > 1 else ""))

        self.state.set("started_at", now_iso())
        self.state.set("max_effort", self.max_effort)

        self.heartbeat.start()
        try:
            self._run_from(phase, lemma_k, iteration)
        finally:
            self.heartbeat.stop()

        log("Proof workflow complete.")

    def _detect_resume_point(self) -> tuple[int, int, int]:
        """Detect resume point from state file or file system."""
        # Check state file first
        current = self.state.get("current_phase")
        if current is not None:
            status = self.state.get("phase_status", "done")
            if status == "in_progress" and self.state.is_heartbeat_stale():
                log(f"Phase {current} was in progress but heartbeat is stale — restarting it")
                return (
                    current,
                    self.state.get("current_lemma", 0),
                    self.state.get("current_iteration", 1),
                )
            elif status == "done":
                # State says current phase is done; detect next from files
                pass

        # Fall back to file-based detection
        return detect_phase_from_files(self.proof_dir)

    def _run_from(self, phase: int, lemma_k: int, iteration: int) -> None:
        """Execute the workflow starting from the given phase."""
        # Phase 0: Environment check
        if phase <= 0:
            self._run_phase_0()
            phase = 1

        # Phase 1: Distill problem
        if phase <= 1:
            self._run_phase_1()
            phase = 2

        # Phase 2: Literature survey (optional)
        if phase <= 2:
            difficulty = self._get_difficulty()
            # Auto-detect: difficult problems get max effort automatically
            if difficulty == "difficult" and not self.max_effort:
                log(f"Auto-enabling max effort (difficulty={difficulty})")
                self.max_effort = True
                self.state.set("max_effort", True)
            if difficulty == "difficult":
                self._run_phase_2_survey()
            else:
                log(f"Phase 2: Skipping survey (difficulty={difficulty})")
            phase = 3

        # Phase 3: Strategy + decomposition
        if phase <= 3:
            self._run_phase_3()
            phase = 4
            lemma_k = 1
            iteration = 1

        # Prefer the count Phase 3 already set from its JSON summary; only
        # re-parse from the file if Phase 3 didn't populate one. This avoids
        # losing a valid count when the agent uses non-numeric lemma names
        # (e.g., "Lemma L1") that _count_lemmas can't match.
        if not self.lemma_count:
            self.lemma_count = _count_lemmas(self.proof_dir)
        if self.lemma_count == 0:
            log("Error: could not determine lemma count")
            sys.exit(1)

        log(f"Total lemmas: {self.lemma_count}")

        # Phase 4: prove each lemma (parallelized when --parallel > 1)
        if phase <= 4:
            self._run_phase_4_all(start_lemma=lemma_k, iteration=iteration)
            phase = 5
            lemma_k = 1
            iteration = 1

        # Phase 5–8: dual loop (inner audit loop + outer re-strategization)
        if phase <= 8:
            self._run_dual_loop(lemma_k, iteration)

        # Phase 9: cold read assembly
        if phase <= 9:
            self._run_phase_9()

    def _set_phase(self, phase: int, lemma: int = 0, iteration: int = 1,
                   status: str = "in_progress") -> None:
        self.state.data.update({
            "current_phase": phase,
            "current_lemma": lemma,
            "current_iteration": iteration,
            "phase_status": status,
        })
        self.state.save()

    def _mark_done(self) -> None:
        self.state.set("phase_status", "done")

    def _invoke(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Invoke claude with the orchestrator's working directory.

        If no explicit system_prompt is given, the cached ContextBuilder blob
        is used so Anthropic's prompt cache can hit on repeated calls within
        the same proof run.
        """
        if system_prompt is None:
            sp = self.context.system_prompt()
            if not sp.strip():
                sp = None
            system_prompt = sp
        return invoke_claude(
            prompt, system_prompt=system_prompt, cwd=self.work_dir,
            max_retries=self.max_retries, max_total_wait=self.max_total_wait,
        )

    def _get_difficulty(self) -> str:
        """Get difficulty from state or parse from distilled file."""
        # Check state first (set during Phase 1)
        difficulty = self.state.get("difficulty")
        if difficulty:
            return difficulty
        return _get_difficulty(self.proof_dir)

    # -- Phase 0: Environment check --

    def _run_phase_0(self) -> None:
        log("Phase 0: Environment Check")
        self._set_phase(0)

        self.proof_dir.mkdir(parents=True, exist_ok=True)

        log(f"  Working directory: {self.work_dir}")
        log(f"  Proof directory:   {self.proof_dir}")
        log(f"  Max effort:        {self.max_effort}")

        # Verify user input exists
        user_input = self.proof_dir / "00_user_input.md"
        if not user_input.exists():
            log("Error: proof_work/00_user_input.md not found.")
            log("The skill should write the user's problem to this file before launching.")
            sys.exit(1)

        self._mark_done()

    # -- Phase 1: Distill problem --

    def _run_phase_1(self) -> None:
        log("Phase 1: Distilling problem from user input")
        self._set_phase(1)

        prompt = format_prompt(PHASE_1_DISTILL)
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        if summary:
            difficulty = summary.get("difficulty", "moderate")
            self.state.set("difficulty", difficulty)
            log(f"  → Difficulty: {difficulty}")
            log(f"  → Proposition: {summary.get('proposition_summary', '?')}")
        else:
            log("  → Distilled problem written (could not parse summary)")

        self._mark_done()

    # -- Phase 2: Literature survey (optional) --

    def _run_phase_2_survey(self) -> None:
        log("Phase 2: Literature Survey")
        self._set_phase(2)

        prompt = format_prompt(PHASE_2_SURVEY)
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        if summary:
            log(f"  → Applicable theorems: {summary.get('applicable_theorems', '?')}")
            log(f"  → Counterexamples: {summary.get('counterexamples', '?')}")
        else:
            log("  → Survey written (could not parse summary)")

        self._mark_done()

    # -- Phase 3: Strategy + decomposition --

    def _run_phase_3(self) -> None:
        log("Phase 3: Strategy and Decomposition")
        self._set_phase(3)

        # Build context for survey and status log
        survey_ctx = ""
        if (self.proof_dir / "00_survey.md").exists():
            survey_ctx = "- Read `proof_work/00_survey.md` (literature survey)."

        status_log_ctx = ""
        if (self.proof_dir / "status_log.md").exists():
            status_log_ctx = (
                "- Read `proof_work/status_log.md` — use the 'Lessons for next iteration' "
                "entries to avoid repeating failed strategies."
            )

        prompt = format_prompt(
            PHASE_3_STRATEGY_DECOMPOSITION,
            survey_context=survey_ctx,
            status_log_context=status_log_ctx,
        )
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        if summary and "lemma_count" in summary:
            self.lemma_count = summary["lemma_count"]
            log(f"  → Strategy: {summary.get('strategy', '?')}")
            log(f"  → {self.lemma_count} lemmas identified")
        else:
            log("  → Strategy and decomposition written (could not parse summary)")
            self.lemma_count = _count_lemmas(self.proof_dir)

        self._mark_done()

    # -- Phase 4: Proof execution --

    def _run_phase_4(self, lemma_k: int, iteration: int = 1) -> None:
        log(f"Phase 4: Proving Lemma {lemma_k}")
        self._set_phase(4, lemma_k, iteration)

        deps = _parse_lemma_dependencies(self.proof_dir, lemma_k)
        dep_text = get_dependency_files_text(deps)

        prompt = format_prompt(
            PHASE_4_PROOF_LEMMA,
            lemma_k=lemma_k,
            iteration=iteration,
            dependency_files=dep_text,
        )
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        if summary:
            gaps = summary.get("gaps", [])
            log(f"  → Lemma {lemma_k}: {summary.get('steps', '?')} steps, "
                f"gaps: {gaps if gaps else 'none'}")
        else:
            log(f"  → Lemma {lemma_k} proof written")

        self._mark_done()

    # -- Phase 5: Self-audit --

    def _run_phase_5(self, lemma_k: int, iteration: int) -> dict | None:
        log(f"Phase 5: Auditing Lemma {lemma_k} (iter {iteration})")
        self._set_phase(5, lemma_k, iteration)

        deps = _parse_lemma_dependencies(self.proof_dir, lemma_k)
        dep_text = get_dependency_files_text(deps)

        prompt = format_prompt(
            PHASE_5_AUDIT_LEMMA,
            lemma_k=lemma_k,
            iteration=iteration,
            dependency_files=dep_text,
        )
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        if summary:
            failures = summary.get("failures", [])
            status = "✅ all pass" if not failures else f"❌ {len(failures)} failure(s)"
            log(f"  → Lemma {lemma_k}: {status}")
        else:
            log(f"  → Audit written (could not parse summary)")

        self._mark_done()
        return summary

    # -- Phase 6: Gap resolution --

    def _run_phase_6(self, lemma_k: int, iteration: int) -> str | None:
        """Run gap analysis and prompt user for fork decision. Returns chosen option."""
        log(f"Phase 6: Gap Resolution for Lemma {lemma_k}")
        self._set_phase(6, lemma_k, iteration)

        # Track failure count for this lemma
        lemma_failures = self.state.get("lemma_failure_counts", {})
        fail_key = str(lemma_k)
        prev_count = lemma_failures.get(fail_key, 0)
        lemma_failures[fail_key] = prev_count + 1
        self.state.set("lemma_failure_counts", lemma_failures)

        log(f"  Failure count for Lemma {lemma_k}: {lemma_failures[fail_key]}")

        prompt = format_prompt(
            PHASE_6_GAP_ANALYSIS,
            lemma_k=lemma_k,
            iteration=iteration,
        )
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        crucial = 0
        if summary:
            crucial = summary.get("crucial", 0)
            fatal = summary.get("fatal", 0)
            fixable = summary.get("fixable", 0)
            log(f"  → Fixable: {fixable}, Crucial: {crucial}, Fatal: {fatal}")

        self._mark_done()

        # If there are crucial gaps, prompt user for fork decision
        if crucial > 0:
            gap_text = self._read_fork_summaries(lemma_k)

            # After FORK_FAILURE_THRESHOLD failures, default to A (accept stronger assumption)
            current_failures = lemma_failures[fail_key]
            if current_failures >= FORK_FAILURE_THRESHOLD:
                fork_default = "A"
                log(f"  ⚠️ Lemma {lemma_k} failed {current_failures} times "
                    f"(≥ {FORK_FAILURE_THRESHOLD}) — defaulting to A (accept stronger assumption)")
            else:
                fork_default = "B"

            choice, was_auto = prompt_user_fork_decision(
                gap_text, default=fork_default)

            decision_note = f"Decision: {choice}"
            if was_auto:
                decision_note += f" (auto-selected after {FORK_TIMEOUT}s timeout"
                if current_failures >= FORK_FAILURE_THRESHOLD:
                    decision_note += f", default changed to A after {current_failures} failures"
                decision_note += ")"

            # Record decision in state
            fork_decisions = self.state.get("fork_decisions", {})
            fork_decisions[str(lemma_k)] = {"choice": choice, "note": decision_note}
            self.state.set("fork_decisions", fork_decisions)

            log(f"  → Fork decision for Lemma {lemma_k}: {choice}")
            return choice

        return None

    def _read_fork_summaries(self, lemma_k: int) -> str:
        """Read fork analysis files for display to user."""
        lines = []
        for f in sorted(self.proof_dir.glob(f"fork_lemma_{lemma_k}_gap_*.md")):
            lines.append(f.read_text(encoding="utf-8"))
            lines.append("")
        return "\n".join(lines) if lines else "(No fork analysis files found)"

    # -- Phase 7: Revision --

    def _run_phase_7(self, lemma_k: int, iteration: int) -> None:
        log(f"Phase 7: Revising Lemma {lemma_k} (iter {iteration} → {iteration + 1})")
        self._set_phase(7, lemma_k, iteration)

        fork_decisions = self.state.get("fork_decisions", {})
        fork_ctx = ""
        if str(lemma_k) in fork_decisions:
            decision = fork_decisions[str(lemma_k)]
            fork_ctx = (
                f"- Fork decision: {decision['choice']}. "
                f"Read fork files: proof_work/fork_lemma_{lemma_k}_gap_*.md"
            )

        prompt = format_prompt(
            PHASE_7_REVISION,
            lemma_k=lemma_k,
            iteration=iteration,
            next_iteration=iteration + 1,
            fork_context=fork_ctx,
        )
        output = self._invoke(prompt)

        summary = parse_json_from_output(output)
        if summary:
            log(f"  → {summary.get('steps_changed', '?')} steps changed, "
                f"all addressed: {summary.get('all_issues_addressed', '?')}")
        else:
            log(f"  → Revision written")

        # Phase 7 may rewrite 00_distilled.md (added hypotheses) and always
        # appends to status_log.md. Force the next invocation to rebuild the
        # cached system prompt so the agent sees the latest stable context.
        self.context.invalidate()

        self._mark_done()

    # -- Phase 8: Dual loop --

    def _run_dual_loop(self, start_lemma: int = 1, start_iteration: int = 1) -> None:
        """
        Phase 8: Dual loop architecture.
        Inner loop: per-lemma audit→gap→revision (phases 5-7), max MAX_INNER_ITERATIONS.
        Outer loop: if inner loop exhausts, go back to Phase 3 to re-strategize,
                     re-decompose, and re-prove. Max MAX_OUTER_ITERATIONS.
        """
        max_outer = MAX_OUTER_ITERATIONS if self.max_effort else 1

        for outer in range(max_outer):
            if outer > 0:
                log(f"\n{'='*60}")
                log(f"OUTER LOOP: Re-strategization attempt {outer + 1} / {max_outer}")
                log(f"{'='*60}\n")

                # Re-strategize (Phase 3)
                self._run_phase_3()
                self.lemma_count = _count_lemmas(self.proof_dir)
                if self.lemma_count == 0:
                    log("Error: could not determine lemma count after re-strategization")
                    break

                # Clear passed lemmas — decomposition changed, all need re-audit
                self.state.set("passed_lemmas", [])

                # Re-prove all lemmas (Phase 4) — parallel when configured
                self._run_phase_4_all(start_lemma=1, iteration=1)

                start_lemma = 1
                start_iteration = 1

            all_pass = self._run_inner_audit_loop(start_lemma, start_iteration)

            if all_pass:
                break
        else:
            if max_outer > 1:
                log(f"\n⚠️ {max_outer} outer iterations exhausted with remaining failures")
                log("Proceeding to Phase 9 with honest reporting of remaining gaps")

    def _run_inner_audit_loop(self, start_lemma: int = 1,
                              start_iteration: int = 1) -> bool:
        """
        Inner audit loop: phases 5-7 per-lemma.
        Returns True if all lemmas pass all audit checks.
        Lemmas that fully pass are marked and skipped in future iterations.
        """
        max_iters = MAX_INNER_ITERATIONS if self.max_effort else 1

        # Track passed lemmas — restore from state if resuming
        passed_lemmas: set[int] = set(self.state.get("passed_lemmas", []))

        end_iteration = max(start_iteration + 1, MAX_INNER_ITERATIONS + 1)
        for iteration in range(start_iteration, end_iteration):
            log(f"\n{'='*50}")
            log(f"AUDIT ITERATION {iteration} / {end_iteration - 1}")
            if passed_lemmas:
                log(f"  Passed lemmas (skipping): {sorted(passed_lemmas)}")
            log(f"{'='*50}\n")

            all_pass = True

            # Determine which lemmas need auditing this iteration.
            lemmas_to_audit = [
                k for k in range(start_lemma, self.lemma_count + 1)
                if k not in passed_lemmas
            ]
            for k in range(start_lemma, self.lemma_count + 1):
                if k in passed_lemmas:
                    log(f"  Lemma {k}: already passed — skipping")

            # Phase 5: audit (parallel when --parallel > 1)
            audit_summaries = self._run_phase_5_all(lemmas_to_audit, iteration)

            # Phase 6/7 sequential per failing lemma — Phase 7 may mutate
            # 00_distilled.md, and that mutation must be visible to subsequent
            # revisions in this iteration.
            for k in lemmas_to_audit:
                summary = audit_summaries.get(k)
                has_failures = True  # default to cautious
                if summary:
                    has_failures = bool(summary.get("failures"))
                else:
                    audit_file = self.proof_dir / f"audit_lemma_{k}_iter_{iteration}.md"
                    has_failures = _audit_has_failures(audit_file)

                if has_failures:
                    all_pass = False
                    # Phase 6: gap resolution
                    self._run_phase_6(k, iteration)
                    # Phase 7: revision
                    self._run_phase_7(k, iteration)
                else:
                    # Mark lemma as passed — won't be re-audited
                    passed_lemmas.add(k)
                    self.state.set("passed_lemmas", sorted(passed_lemmas))
                    log(f"  ✅ Lemma {k} passed — marked, will skip in future iterations")

            # After first iteration, always start from lemma 1
            start_lemma = 1

            if all_pass:
                log(f"\n✅ All lemmas pass all 6 audit checks at iteration {iteration}")
                return True
        else:
            if max_iters > 1:
                log(f"\n⚠️ {max_iters} inner iterations exhausted with remaining failures")
            return False

        return False  # unreachable but explicit

    # -- Phase 9: Cold read assembly --

    def _run_phase_9(self) -> None:
        # 9a: compile (Python — mechanical file ordering, no LLM needed)
        log("Phase 9a: Compiling proof (Python)")
        self._set_phase(9, status="in_progress")

        order_file, lemma_files = self._compile_assembled_order()
        log(f"  → Proof compiled ({len(lemma_files)} lemma files → {order_file.name})")

        # 9b: cold read
        log("Phase 9b: Cold read audit")
        output = self._invoke(PHASE_9B_COLD_READ)
        summary = parse_json_from_output(output)
        if summary:
            unresolved = summary.get("unresolved_critical", 0)
            if unresolved > 0:
                log(f"  → ⚠️ {unresolved} UNRESOLVED CRITICAL GAP(S)")
            else:
                log(f"  → ✅ Cold read passed ({summary.get('issues_found', 0)} issues found, all resolved)")
        else:
            log("  → Cold read audit written")

        # 9c: final proof
        log("Phase 9c: Writing final proof")
        prompt = format_prompt(PHASE_9C_FINAL_PROOF)
        output = self._invoke(prompt)
        summary = parse_json_from_output(output)
        if summary:
            complete = summary.get("complete", False)
            if complete:
                log("  → ✅ Final proof written (complete)")
            else:
                gaps = summary.get("unresolved_gaps", "?")
                log(f"  → ⚠️ Final proof written (INCOMPLETE — {gaps} unresolved gaps)")
        else:
            log("  → Final proof written")

        # 9d: journal
        log("Phase 9d: Compiling proof journal")
        prompt = format_prompt(PHASE_9D_JOURNAL)
        self._invoke(prompt)
        log("  → Proof journal compiled")

        self._mark_done()
        self._print_completion()

    # -- Phase 9a Python replacement --

    def _compile_assembled_order(self) -> tuple[Path, list[Path]]:
        """
        Replace the LLM Phase 9a call with deterministic file ordering.

        Globs proof_lemma_*.md files in numeric order and writes
        proof_work/assembled_proof_order.md listing them. Returns
        (order_file_path, ordered_lemma_files).

        Same output shape as the prior LLM-driven phase, so downstream
        consumers (Phase 9b/9c/9d, tests) see no semantic difference.
        """
        files = list(self.proof_dir.glob("proof_lemma_*.md"))
        numbered: list[tuple[int, Path]] = []
        for f in files:
            m = re.search(r"proof_lemma_(\d+)\.md", f.name)
            if m:
                numbered.append((int(m.group(1)), f))
        numbered.sort(key=lambda t: t[0])
        ordered_files = [f for _, f in numbered]

        # Detect gaps in lemma numbering (e.g., proof_lemma_3.md missing)
        if numbered:
            present = {n for n, _ in numbered}
            expected = set(range(1, max(present) + 1))
            missing = sorted(expected - present)
            if missing:
                log(f"  ⚠️ Missing lemma proof files: {missing}")

        lines = ["# Assembled Proof Order", ""]
        lines.append(f"Total lemma files: {len(ordered_files)}")
        lines.append("")
        for n, f in numbered:
            lines.append(f"- Lemma {n}: `proof_work/{f.name}`")
        lines.append("")

        order_file = self.proof_dir / "assembled_proof_order.md"
        order_file.write_text("\n".join(lines), encoding="utf-8")
        return order_file, ordered_files

    # -- Parallel scheduling --

    def _build_dependency_waves(self, lemma_count: int) -> list[list[int]]:
        """
        Build topological waves from the lemma dependency graph.

        Wave w contains every lemma whose dependencies are all in waves < w.
        Lemmas with no in-decomposition dependencies form wave 0.
        Self-references and forward references are ignored.
        """
        deps: dict[int, set[int]] = {}
        for k in range(1, lemma_count + 1):
            raw = _parse_lemma_dependencies(self.proof_dir, k)
            deps[k] = {d for d in raw if 1 <= d <= lemma_count and d != k}

        waves: list[list[int]] = []
        scheduled: set[int] = set()
        remaining = set(range(1, lemma_count + 1))

        while remaining:
            wave = sorted(k for k in remaining if deps[k] <= scheduled)
            if not wave:
                # Cycle or unsatisfiable dependencies — fall back to sequential
                # so we still make progress. Log it once.
                log(f"  ⚠️ Dependency cycle or unresolved dep among {sorted(remaining)} "
                    f"— falling back to sequential order")
                waves.extend([k] for k in sorted(remaining))
                break
            waves.append(wave)
            scheduled.update(wave)
            remaining.difference_update(wave)

        return waves

    def _run_phase_4_all(self, start_lemma: int, iteration: int = 1) -> None:
        """
        Run Phase 4 across all lemmas, parallelized when self.parallel > 1.

        Sequential path (parallel=1): identical to the old per-lemma loop.
        Parallel path: schedule lemmas in dependency waves, dispatch each
        wave concurrently with up to self.parallel workers.
        """
        if self.parallel == 1:
            for k in range(start_lemma, self.lemma_count + 1):
                self._run_phase_4(k, iteration)
            return

        waves = self._build_dependency_waves(self.lemma_count)
        # If resuming mid-Phase-4, drop already-completed lemmas from waves.
        if start_lemma > 1:
            done = set(range(1, start_lemma))
            waves = [[k for k in w if k not in done] for w in waves]
            waves = [w for w in waves if w]

        for wave_idx, wave in enumerate(waves):
            if len(wave) == 1:
                self._run_phase_4(wave[0], iteration)
                continue

            cap_str = "unlimited" if self.parallel == PARALLEL_UNLIMITED \
                else f"max {self.parallel}"
            log(f"Phase 4 wave {wave_idx + 1}/{len(waves)}: "
                f"proving lemmas {wave} in parallel ({cap_str})")
            self._dispatch_lemma_workers(
                wave, lambda k: self._run_phase_4(k, iteration)
            )

    def _run_phase_5_all(self, lemmas_to_audit: list[int],
                          iteration: int) -> dict[int, dict | None]:
        """
        Run Phase 5 audit for the given lemmas, parallelized when self.parallel > 1.

        Returns a dict mapping lemma index → audit JSON summary (or None if
        the agent didn't return parseable JSON).
        """
        results: dict[int, dict | None] = {}

        if self.parallel == 1 or len(lemmas_to_audit) <= 1:
            for k in lemmas_to_audit:
                results[k] = self._run_phase_5(k, iteration)
            return results

        cap_str = "unlimited" if self.parallel == PARALLEL_UNLIMITED \
            else f"max {self.parallel}"
        log(f"Phase 5: auditing lemmas {lemmas_to_audit} in parallel ({cap_str})")

        results_lock = threading.Lock()

        def worker(k: int) -> None:
            summary = self._run_phase_5(k, iteration)
            with results_lock:
                results[k] = summary

        self._dispatch_lemma_workers(lemmas_to_audit, worker)
        return results

    def _dispatch_lemma_workers(self, lemmas: list[int],
                                  fn) -> None:
        """
        Dispatch `fn(lemma_k)` for each lemma concurrently using a thread pool.

        Each worker gets a `[L{k}] ` log prefix. Tracks in-flight lemmas in
        the state file via add/remove_concurrent_lemma. Re-raises the first
        worker exception after all workers finish (or fail-fast cancellation
        if pool is small).
        """
        def wrapped(k: int) -> None:
            set_log_prefix(f"[L{k}] ")
            self.state.add_concurrent_lemma(k)
            try:
                fn(k)
            finally:
                self.state.remove_concurrent_lemma(k)
                set_log_prefix(None)

        if self.parallel == PARALLEL_UNLIMITED:
            max_workers = len(lemmas)
        else:
            max_workers = min(self.parallel, len(lemmas))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(wrapped, k): k for k in lemmas}
            first_exc: BaseException | None = None
            for fut in concurrent.futures.as_completed(futures):
                try:
                    fut.result()
                except BaseException as e:  # noqa: BLE001
                    if first_exc is None:
                        first_exc = e
            if first_exc is not None:
                raise first_exc

    def _print_completion(self) -> None:
        print("\n" + "=" * 60)
        print("  PROOF WORKFLOW COMPLETE")
        print("=" * 60)
        print(f"  Final proof:   {self.proof_dir / 'final_proof.md'}")
        print(f"  Proof journal: {self.proof_dir / 'proof_journal.md'}")

        if self._final_proof_has_unresolved_gaps():
            print()
            print("  ⚠️  WARNING: Proof has UNRESOLVED CRITICAL GAPS")
            print("  See final_proof.md for details")

        print("=" * 60)

    def _final_proof_has_unresolved_gaps(self) -> bool:
        """
        Detect real unresolved gaps in the final proof.

        Phase 9c writes one of two terminators:
        - clean: ends with `∎`
        - incomplete: ends with `□ (INCOMPLETE — see unresolved gaps)` and
          marks each gap inline as `[UNRESOLVED: ...]`.

        We check the final proof — not cold_read_audit.md — because the cold
        read file contains the literal phrase `[UNRESOLVED CRITICAL GAP]` as
        part of the rubric instructions even when the cold read passes
        cleanly. Looking at final_proof.md is unambiguous.
        """
        final = self.proof_dir / "final_proof.md"
        if not final.exists():
            return False
        text = final.read_text(encoding="utf-8")
        return "□ (INCOMPLETE" in text or "[UNRESOLVED:" in text


# ---------------------------------------------------------------------------
# Terminal mode (cross-platform)
# ---------------------------------------------------------------------------

def _build_extra_args(args) -> list[str]:
    """Build extra CLI arguments from parsed args for the inner invocation.

    Always includes --no-terminal so the inner process runs in-place
    instead of spawning yet another terminal window.
    """
    extra = ["--no-terminal"]
    if args.resume:
        extra.append("--resume")
    if args.max_effort:
        extra.append("--max-effort")
    if args.max_retries != RETRY_MAX_ATTEMPTS:
        extra.extend(["--max-retries", str(args.max_retries)])
    if args.max_wait != RETRY_MAX_TOTAL_WAIT:
        extra.extend(["--max-wait", str(args.max_wait)])
    if args.no_retry:
        extra.append("--no-retry")
    parallel = getattr(args, "parallel", PARALLEL_DEFAULT)
    if parallel and parallel != PARALLEL_DEFAULT:
        extra.extend(["--parallel", str(parallel)])
    return extra


def _launch_in_new_console(args) -> bool:
    """
    Re-launch orchestrate.py in a new terminal window, then return True.
    Supports Windows, macOS, and Linux.

    Uses platform-specific scripts to avoid quoting issues with paths
    containing spaces and to guarantee the window stays open after completion.
    Python is invoked with -u for unbuffered output.
    """
    script = Path(__file__).resolve()
    work_dir = Path(args.work_dir).resolve()
    proof_dir = work_dir / "proof_work"
    proof_dir.mkdir(parents=True, exist_ok=True)

    extra_args = _build_extra_args(args)
    extra_str = " ".join(extra_args)

    if sys.platform == "win32":
        return _launch_windows(script, work_dir, proof_dir, extra_str)
    elif sys.platform == "darwin":
        return _launch_macos(script, work_dir, proof_dir, extra_args)
    else:
        return _launch_linux(script, work_dir, proof_dir, extra_str)


def _launch_windows(script: Path, work_dir: Path, proof_dir: Path,
                    extra_str: str) -> bool:
    """Launch orchestrator in a new Windows console window via batch file."""
    batch_file = proof_dir / "_run_orchestrator.bat"
    batch_file.write_text(
        f'@echo off\r\n'
        f'chcp 65001 >nul 2>&1\r\n'
        f'title Rigorous Proof Orchestrator\r\n'
        f'echo Starting orchestrator at %date% %time%\r\n'
        f'echo Working directory: "{work_dir}"\r\n'
        f'echo.\r\n'
        f'"{sys.executable}" -u "{script}" --work-dir "{work_dir}" {extra_str}\r\n'
        f'echo.\r\n'
        f'echo Orchestrator exited with code: %ERRORLEVEL%\r\n'
        f'echo.\r\n'
        f'pause\r\n',
        encoding="utf-8",
    )

    CREATE_NEW_CONSOLE = 0x00000010
    subprocess.Popen(
        ["cmd", "/c", str(batch_file)],
        creationflags=CREATE_NEW_CONSOLE,
        close_fds=True,
    )

    log("Orchestrator launched in new console window.")
    log(f"  The orchestrator will continue running independently of this session.")
    log(f"  Monitor progress in: proof_work/orchestrator_state.json")
    return True


def _launch_macos(script: Path, work_dir: Path, proof_dir: Path,
                  extra_args: list[str]) -> bool:
    """Launch orchestrator in a new macOS Terminal.app window via osascript."""
    shell_file = proof_dir / "_run_orchestrator.sh"
    extra_str = " ".join(extra_args)
    shell_file.write_text(
        f'#!/bin/bash\n'
        f'echo "Starting orchestrator at $(date)"\n'
        f'echo "Working directory: {work_dir}"\n'
        f'echo\n'
        f'"{sys.executable}" -u "{script}" --work-dir "{work_dir}" {extra_str}\n'
        f'EXIT_CODE=$?\n'
        f'echo\n'
        f'echo "Orchestrator exited with code: $EXIT_CODE"\n'
        f'echo\n'
        f'echo "Press any key to close..."\n'
        f'read -n 1 -s\n',
        encoding="utf-8",
    )
    import stat
    shell_file.chmod(shell_file.stat().st_mode | stat.S_IEXEC)

    # Use osascript to open a new Terminal.app window running the script
    apple_script = (
        f'tell application "Terminal"\n'
        f'  do script "{shell_file}"\n'
        f'  activate\n'
        f'end tell'
    )
    subprocess.Popen(
        ["osascript", "-e", apple_script],
        close_fds=True,
    )

    log("Orchestrator launched in new Terminal.app window.")
    log(f"  The orchestrator will continue running independently of this session.")
    log(f"  Monitor progress in: proof_work/orchestrator_state.json")
    return True


def _launch_linux(script: Path, work_dir: Path, proof_dir: Path,
                  extra_str: str) -> bool:
    """Launch orchestrator in a new Linux terminal window."""
    shell_file = proof_dir / "_run_orchestrator.sh"
    shell_file.write_text(
        f'#!/bin/bash\n'
        f'echo "Starting orchestrator at $(date)"\n'
        f'echo "Working directory: {work_dir}"\n'
        f'echo\n'
        f'"{sys.executable}" -u "{script}" --work-dir "{work_dir}" {extra_str}\n'
        f'EXIT_CODE=$?\n'
        f'echo\n'
        f'echo "Orchestrator exited with code: $EXIT_CODE"\n'
        f'echo\n'
        f'echo "Press any key to close..."\n'
        f'read -n 1 -s\n',
        encoding="utf-8",
    )
    import stat
    shell_file.chmod(shell_file.stat().st_mode | stat.S_IEXEC)

    # Try common Linux terminal emulators in order of popularity
    terminals = [
        ["gnome-terminal", "--", "bash", str(shell_file)],
        ["konsole", "-e", "bash", str(shell_file)],
        ["xfce4-terminal", "-e", f"bash {shell_file}"],
        ["xterm", "-e", "bash", str(shell_file)],
    ]

    for cmd in terminals:
        try:
            subprocess.Popen(cmd, close_fds=True)
            log(f"Orchestrator launched in new terminal window ({cmd[0]}).")
            log(f"  The orchestrator will continue running independently of this session.")
            log(f"  Monitor progress in: proof_work/orchestrator_state.json")
            return True
        except FileNotFoundError:
            continue

    log("No supported terminal emulator found (tried gnome-terminal, konsole, xfce4-terminal, xterm).")
    log("Running in current session instead.")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Rigorous-proof orchestrator — manages the entire proof workflow (Phases 0–9)."
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last saved state after a disruption",
    )
    parser.add_argument(
        "--max-effort",
        action="store_true",
        help="Enable dual loop (Phase 8) — inner audit cycles + outer re-strategization",
    )
    parser.add_argument(
        "--work-dir",
        type=str,
        default=".",
        help="Working directory containing proof_work/ (default: current dir)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=RETRY_MAX_ATTEMPTS,
        help=f"Max retries on rate/usage limit errors (default: {RETRY_MAX_ATTEMPTS})",
    )
    parser.add_argument(
        "--max-wait",
        type=float,
        default=RETRY_MAX_TOTAL_WAIT,
        help=f"Max total retry wait in seconds (default: {RETRY_MAX_TOTAL_WAIT} = 5.5h)",
    )
    parser.add_argument(
        "--no-retry",
        action="store_true",
        help="Disable automatic retry on rate/usage limit errors",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=PARALLEL_DEFAULT,
        help="Concurrent lemma workers in Phase 4 and Phase 5. "
             "0 (default) = unlimited: every independent lemma in a "
             "dependency-DAG wave runs in its own worker. "
             "1 = fully sequential (the prior pre-optimization behavior). "
             "N >= 2 = cap concurrency at N workers per wave.",
    )
    parser.add_argument(
        "--terminal-mode",
        action="store_true",
        help="Launch in a new terminal window (cross-platform). "
             "This is the DEFAULT — use --no-terminal to disable.",
    )
    parser.add_argument(
        "--no-terminal",
        action="store_true",
        help="Disable terminal mode — run in the current session instead of "
             "opening a new terminal window.",
    )
    args = parser.parse_args()

    # Terminal mode is now the default. Use --no-terminal to disable.
    # --terminal-mode is still accepted for backwards compatibility.
    use_terminal = not args.no_terminal
    if use_terminal:
        if _launch_in_new_console(args):
            return

    work_dir = Path(args.work_dir).resolve()
    max_retries = 0 if args.no_retry else args.max_retries
    orchestrator = ProofOrchestrator(
        work_dir, max_effort=args.max_effort,
        max_retries=max_retries, max_total_wait=args.max_wait,
        parallel=args.parallel,
    )
    try:
        orchestrator.run()
    except Exception as e:
        import traceback
        log(f"\nFATAL ERROR: {e}")
        log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
