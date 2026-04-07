#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║              Hash Cracker  v2.0                      ║
║      Auto-detect · MD5 / SHA-1 / SHA-256 / SHA-512   ║
║                                                      ║
║  Author  : rikixz                                    ║
║  GitHub  : https://github.com/blaxkmiradev            ║
╚══════════════════════════════════════════════════════╝
"""

import hashlib
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ──────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────

HASH_TYPES: dict[int, tuple[str, object]] = {
    32:  ("MD5",     hashlib.md5),
    40:  ("SHA-1",   hashlib.sha1),
    64:  ("SHA-256", hashlib.sha256),
    128: ("SHA-512", hashlib.sha512),
}

PROGRESS_INTERVAL = 50_000

# Public wordlists that can be auto-downloaded
WORDLIST_SOURCES: dict[str, str] = {
    "1": (
        "rockyou-75k (lightweight, fast)",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/"
        "master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
    ),
    "2": (
        "top-10k common passwords",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/"
        "master/Passwords/Common-Credentials/10-million-password-list-top-10000.txt",
    ),
    "3": (
        "top-1k common passwords (quick test)",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/"
        "master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt",
    ),
}

DEFAULT_WORDLIST_PATH = Path("wordlist.txt")

# ──────────────────────────────────────────────────────
#  UI helpers
# ──────────────────────────────────────────────────────

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def c(text: str, colour: str) -> str:
    """Wrap text in ANSI colour codes."""
    return f"{colour}{text}{RESET}"


def banner() -> None:
    print(c("""
╔══════════════════════════════════════════════════════╗
║              Hash Cracker  v2.0                      ║
║      Auto-detect · MD5 / SHA-1 / SHA-256 / SHA-512   ║
║                                                      ║
║  Author  : rikixz                                    ║
║  GitHub  : https://github.com/blaxkmiradev            ║
╚══════════════════════════════════════════════════════╝
""", CYAN))


def ask(prompt: str, default: str = "") -> str:
    """Prompt the user; return stripped input or *default* on empty enter."""
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"  {BOLD}{prompt}{RESET}{DIM}{suffix}{RESET} : ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\n  Aborted.")
        sys.exit(0)
    return value if value else default


def format_speed(tried: int, elapsed: float) -> str:
    speed = tried / elapsed if elapsed > 0 else 0
    if speed >= 1_000_000:
        return f"{speed / 1_000_000:.2f}M pw/s"
    if speed >= 1_000:
        return f"{speed / 1_000:.1f}K pw/s"
    return f"{speed:.0f} pw/s"

# ──────────────────────────────────────────────────────
#  Hash helpers
# ──────────────────────────────────────────────────────

def detect_hash_type(hash_str: str) -> tuple[str, object] | tuple[None, None]:
    return HASH_TYPES.get(len(hash_str.strip()), (None, None))


def load_hashes(path: str) -> list[str]:
    file = Path(path)
    if not file.exists():
        print(c(f"\n  [ERROR] File not found: {path}", RED))
        sys.exit(1)
    lines = [ln.strip().lower() for ln in file.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
    if not lines:
        print(c(f"\n  [ERROR] '{path}' is empty.", RED))
        sys.exit(1)
    return lines

# ──────────────────────────────────────────────────────
#  Wordlist helpers
# ──────────────────────────────────────────────────────

def pick_wordlist() -> Path:
    """
    Ask the user for a wordlist path.
    If they skip or the path doesn't exist, offer to auto-download.
    """
    print(c("\n  ── Wordlist ─────────────────────────────", DIM))
    user_path = ask("Path to wordlist (leave blank to download)", "")

    if user_path:
        p = Path(user_path)
        if p.exists():
            return p
        print(c(f"\n  [WARN] '{user_path}' not found.", YELLOW))

    # Offer download menu
    print(c("\n  Available wordlists to download:", CYAN))
    for key, (label, _) in WORDLIST_SOURCES.items():
        print(f"    {c(key, BOLD)})  {label}")
    print(f"    {c('0', BOLD)})  Cancel — exit")

    choice = ask("Choose a wordlist", "1")
    if choice == "0" or choice not in WORDLIST_SOURCES:
        print("\n  Cancelled.")
        sys.exit(0)

    label, url = WORDLIST_SOURCES[choice]
    return download_wordlist(url, DEFAULT_WORDLIST_PATH, label)


def download_wordlist(url: str, dest: Path, label: str) -> Path:
    """Download *url* to *dest* with a simple progress indicator."""
    print(c(f"\n  Downloading: {label}", CYAN))
    print(c(f"  Source : {url}", DIM))
    print(f"  Saving → {dest}\n")

    try:
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                pct = min(downloaded / total_size * 100, 100)
                bar_len = 30
                filled = int(bar_len * pct / 100)
                bar = "█" * filled + "░" * (bar_len - filled)
                mb = downloaded / 1_048_576
                print(f"\r  [{bar}] {pct:5.1f}%  {mb:.1f} MB", end="", flush=True)
            else:
                mb = downloaded / 1_048_576
                print(f"\r  Downloaded {mb:.1f} MB", end="", flush=True)

        urllib.request.urlretrieve(url, dest, reporthook)
        print(c("\n\n  ✔ Download complete.", GREEN))
        return dest

    except urllib.error.URLError as exc:
        print(c(f"\n\n  [ERROR] Download failed: {exc.reason}", RED))
        sys.exit(1)

# ──────────────────────────────────────────────────────
#  Core cracker
# ──────────────────────────────────────────────────────

def crack(hashes: set[str], hasher, wordlist_path: Path) -> tuple[int, int]:
    remaining = set(hashes)
    cracked   = 0
    start     = time.perf_counter()

    with open(wordlist_path, encoding="utf-8", errors="ignore") as fh:
        for tried, raw_line in enumerate(fh, start=1):
            password = raw_line.rstrip("\n")
            if not password:
                continue

            digest = hasher(password.encode("utf-8")).hexdigest()

            if digest in remaining:
                elapsed = time.perf_counter() - start
                print(
                    f"  {c('[+] CRACKED', GREEN)}  "
                    f"{c(digest, DIM)}  →  "
                    f"{c(repr(password), BOLD)}  "
                    f"{c(f'({elapsed:.2f}s)', DIM)}"
                )
                remaining.discard(digest)
                cracked += 1

                if not remaining:
                    print(c("\n  ✔ All hashes cracked!\n", GREEN))
                    return cracked, tried

            if tried % PROGRESS_INTERVAL == 0:
                elapsed = time.perf_counter() - start
                print(
                    c(
                        f"  ... {tried:>10,} tried | "
                        f"cracked: {cracked}/{len(hashes)} | "
                        f"{format_speed(tried, elapsed)}",
                        DIM,
                    )
                )

    return cracked, tried

# ──────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────

def main() -> None:
    banner()

    # ── Ask for hash file ──────────────────────
    print(c("  ── Hash File ────────────────────────────", DIM))
    hash_path = ask("Path to hash file", "hash.txt")

    raw_hashes = load_hashes(hash_path)
    algo_name, hasher = detect_hash_type(raw_hashes[0])

    if algo_name is None:
        first_len = len(raw_hashes[0])
        supported = ", ".join(f"{n}({b})" for b, (n, _) in HASH_TYPES.items())
        print(c(f"\n  [ERROR] Unknown hash length ({first_len} chars).", RED))
        print(f"  Supported: {supported}")
        sys.exit(1)

    hash_set = set(raw_hashes)

    # ── Ask for / download wordlist ────────────
    wordlist_path = pick_wordlist()

    # ── Summary before starting ────────────────
    print(c("\n  ── Starting ─────────────────────────────", DIM))
    print(f"  Algorithm : {c(algo_name, CYAN)}")
    print(f"  Hashes    : {c(str(len(hash_set)), CYAN)}")
    print(f"  Wordlist  : {c(str(wordlist_path), CYAN)}\n")

    # ── Crack ──────────────────────────────────
    start    = time.perf_counter()
    cracked, tried = crack(hash_set, hasher, wordlist_path)
    elapsed  = time.perf_counter() - start

    # ── Final summary ──────────────────────────
    uncracked = len(hash_set) - cracked
    status_colour = GREEN if uncracked == 0 else YELLOW

    print(c("  ─" * 21, DIM))
    print(f"  Result   : {c(f'{cracked} cracked', status_colour)} / {uncracked} uncracked")
    print(f"  Tried    : {tried:,} passwords")
    print(f"  Time     : {elapsed:.2f}s  ({format_speed(tried, elapsed)})")
    print(c("  ─" * 21, DIM))
    print(c("\n  Made by rikixz — github.com/blaxkmiradev\n", DIM))

    sys.exit(0 if uncracked == 0 else 1)


if __name__ == "__main__":
    main()
