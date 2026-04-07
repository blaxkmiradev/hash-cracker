#!/usr/bin/env python3
"""
Hash Cracker v2.1 — by rikixz
github.com/blaxkmiradev
"""

import hashlib
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ──────────────────────────────────────────────────────
#  ANSI colour palette
# ──────────────────────────────────────────────────────

RST    = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
BLACK   = "\033[30m"

BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLACK   = "\033[40m"

def red(t):     return f"{RED}{t}{RST}"
def green(t):   return f"{GREEN}{t}{RST}"
def yellow(t):  return f"{YELLOW}{t}{RST}"
def blue(t):    return f"{BLUE}{t}{RST}"
def magenta(t): return f"{MAGENTA}{t}{RST}"
def cyan(t):    return f"{CYAN}{t}{RST}"
def white(t):   return f"{WHITE}{t}{RST}"
def dim(t):     return f"{DIM}{t}{RST}"
def bold(t):    return f"{BOLD}{t}{RST}"
def success(t): return f"{BOLD}{GREEN}{t}{RST}"
def warn(t):    return f"{BOLD}{YELLOW}{t}{RST}"
def error(t):   return f"{BOLD}{RED}{t}{RST}"
def info(t):    return f"{BOLD}{CYAN}{t}{RST}"

# ──────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────

ALGO_COLOUR = {
    "MD5":     MAGENTA,
    "SHA-1":   YELLOW,
    "SHA-256": CYAN,
    "SHA-512": BLUE,
}

HASH_TYPES = {
    32:  ("MD5",     hashlib.md5),
    40:  ("SHA-1",   hashlib.sha1),
    64:  ("SHA-256", hashlib.sha256),
    128: ("SHA-512", hashlib.sha512),
}

PROGRESS_INTERVAL = 50_000

WORDLIST_SOURCES = {
    "1": (
        "top-1M passwords  (~8 MB)",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/"
        "master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
    ),
    "2": (
        "top-10K passwords (~80 KB)",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/"
        "master/Passwords/Common-Credentials/10-million-password-list-top-10000.txt",
    ),
    "3": (
        "top-1K  passwords  (quick test)",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/"
        "master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt",
    ),
}

DEFAULT_WORDLIST_PATH = Path("wordlist.txt")

# ──────────────────────────────────────────────────────
#  Banner
# ──────────────────────────────────────────────────────

def banner():
    lines = [
        "╔══════════════════════════════════════════════════════╗",
        "║                                                      ║",
        "║          ██╗  ██╗ █████╗ ███████╗██╗  ██╗           ║",
        "║          ██║  ██║██╔══██╗██╔════╝██║  ██║           ║",
        "║          ███████║███████║███████╗███████║           ║",
        "║          ██╔══██║██╔══██║╚════██║██╔══██║           ║",
        "║          ██║  ██║██║  ██║███████║██║  ██║           ║",
        "║          ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝           ║",
        "║                                                      ║",
        "║           C R A C K E R    v 2 . 1                  ║",
        "║      MD5 · SHA-1 · SHA-256 · SHA-512 · Auto         ║",
        "║                                                      ║",
        "║  Author : rikixz                                     ║",
        "║  GitHub : github.com/blaxkmiradev                    ║",
        "╚══════════════════════════════════════════════════════╝",
    ]
    gradient = [CYAN, CYAN, BLUE, BLUE, MAGENTA, MAGENTA, CYAN, CYAN,
                BLUE, GREEN, CYAN, BLUE, DIM, DIM, CYAN]
    print()
    for line, col in zip(lines, gradient):
        print(f"  {col}{BOLD}{line}{RST}")
    print()

# ──────────────────────────────────────────────────────
#  Section headers
# ──────────────────────────────────────────────────────

def section(title):
    bar = "─" * (50 - len(title) - 3)
    print(f"\n  {CYAN}{BOLD}┌─ {title} {DIM}{bar}{RST}")

def section_end():
    print(f"  {DIM}{CYAN}└{'─' * 52}{RST}\n")

# ──────────────────────────────────────────────────────
#  Input helper
# ──────────────────────────────────────────────────────

def ask(prompt, default=""):
    default_hint = f" {DIM}[{default}]{RST}" if default else ""
    try:
        value = input(f"  {CYAN}❯{RST} {BOLD}{prompt}{RST}{default_hint} : ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n  {warn('Aborted.')}")
        sys.exit(0)
    return value if value else default

# ──────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────

def format_speed(tried, elapsed):
    speed = tried / elapsed if elapsed > 0 else 0
    if speed >= 1_000_000:
        return f"{speed / 1_000_000:.2f}M pw/s"
    if speed >= 1_000:
        return f"{speed / 1_000:.1f}K pw/s"
    return f"{speed:.0f} pw/s"

def progress_bar(pct, width=28):
    filled = int(width * pct / 100)
    empty  = width - filled
    if pct < 40:
        bar_col = GREEN
    elif pct < 75:
        bar_col = YELLOW
    else:
        bar_col = CYAN
    bar = f"{bar_col}{'█' * filled}{DIM}{'░' * empty}{RST}"
    return f"[{bar}]"

def detect_hash_type(hash_str):
    return HASH_TYPES.get(len(hash_str.strip()), (None, None))

def algo_tag(name):
    col = ALGO_COLOUR.get(name, WHITE)
    return f"{BOLD}{col}[{name}]{RST}"

def load_hashes(path):
    file = Path(path)
    if not file.exists():
        print(f"\n  {error('[✗ ERROR]')} {red(f'File not found: {path}')}")
        sys.exit(1)
    lines = [
        ln.strip().lower()
        for ln in file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if ln.strip()
    ]
    if not lines:
        print(f"\n  {error('[✗ ERROR]')} {red(f'{path!r} is empty.')}")
        sys.exit(1)
    return lines

# ──────────────────────────────────────────────────────
#  Wordlist helpers
# ──────────────────────────────────────────────────────

def pick_wordlist():
    section("Wordlist")
    user_path = ask("Path to wordlist  (blank = download menu)", "")

    if user_path:
        p = Path(user_path)
        if p.exists():
            print(f"  {success('✔')} Using {cyan(str(p))}")
            section_end()
            return p
        print(f"  {warn('[!]')} {yellow(f'{user_path!r} not found')} — showing download menu.")

    print(f"\n  {info('Available wordlists:')}\n")
    for key, (label, _) in WORDLIST_SOURCES.items():
        print(f"    {BOLD}{CYAN}{key}{RST})  {WHITE}{label}{RST}")
    print(f"    {BOLD}{RED}0{RST})  {dim('Cancel — exit')}\n")

    choice = ask("Choose", "1")
    if choice == "0" or choice not in WORDLIST_SOURCES:
        print(f"\n  {dim('Cancelled.')}")
        sys.exit(0)

    label, url = WORDLIST_SOURCES[choice]
    section_end()
    return download_wordlist(url, DEFAULT_WORDLIST_PATH, label)

def download_wordlist(url, dest, label):
    print(f"  {info('↓ Downloading:')} {white(label)}")
    print(f"  {dim(url)}")
    print(f"  {dim('Saving →')} {cyan(str(dest))}\n")

    try:
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                pct = min(downloaded / total_size * 100, 100)
                bar = progress_bar(pct, 28)
                mb  = downloaded / 1_048_576
                print(f"\r  {bar} {BOLD}{pct:5.1f}%{RST}  {dim(f'{mb:.1f} MB')}  ", end="", flush=True)
            else:
                mb = downloaded / 1_048_576
                print(f"\r  {cyan('↓')} {dim(f'{mb:.1f} MB downloaded')}  ", end="", flush=True)

        urllib.request.urlretrieve(url, dest, reporthook)
        print(f"\n\n  {success('✔ Download complete.')}\n")
        return dest

    except urllib.error.URLError as exc:
        print(f"\n\n  {error('[✗ ERROR]')} {red(f'Download failed: {exc.reason}')}")
        sys.exit(1)

# ──────────────────────────────────────────────────────
#  Core cracker
# ──────────────────────────────────────────────────────

def crack(hashes, hasher, algo, wordlist_path):
    remaining = set(hashes)
    cracked   = 0
    total     = len(hashes)
    tag       = algo_tag(algo)
    start     = time.perf_counter()

    with open(wordlist_path, encoding="utf-8", errors="ignore") as fh:
        for tried, raw_line in enumerate(fh, start=1):
            password = raw_line.rstrip("\n")
            if not password:
                continue

            digest = hasher(password.encode("utf-8")).hexdigest()

            if digest in remaining:
                elapsed = time.perf_counter() - start
                crack_num = f"{BOLD}{GREEN}[+] CRACKED {cracked + 1}/{total}{RST}"
                print(
                    f"  {crack_num}  {tag}  "
                    f"{dim(digest[:16] + '…')}  "
                    f"{BOLD}{GREEN}→  {WHITE}{password!r}{RST}  "
                    f"{dim(f'({elapsed:.2f}s)')}"
                )
                remaining.discard(digest)
                cracked += 1

                if not remaining:
                    print(f"\n  {BG_GREEN}{BLACK}{BOLD}  ✔  ALL {total} HASHES CRACKED!  {RST}\n")
                    return cracked, tried

            if tried % PROGRESS_INTERVAL == 0:
                elapsed = time.perf_counter() - start
                pct = (cracked / total * 100) if total else 0
                bar = progress_bar(pct, 20)
                print(
                    f"  {dim('...')} {bar}  "
                    f"{cyan(f'{tried:,}')} tried  "
                    f"{green(str(cracked))}{dim(f'/{total}')} cracked  "
                    f"{yellow(format_speed(tried, elapsed))}"
                )

    return cracked, tried

# ──────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────

def main():
    banner()

    section("Hash File")
    hash_path  = ask("Path to hash file", "hash.txt")
    raw_hashes = load_hashes(hash_path)
    algo_name, hasher = detect_hash_type(raw_hashes[0])

    if algo_name is None:
        first_len = len(raw_hashes[0])
        supported = "  ".join(f"{n}({b})" for b, (n, _) in HASH_TYPES.items())
        print(f"  {error('[✗ ERROR]')} Unknown hash length: {red(str(first_len))} chars")
        print(f"  {dim('Supported:')} {supported}")
        sys.exit(1)

    hash_set = set(raw_hashes)
    col = ALGO_COLOUR.get(algo_name, WHITE)
    print(f"  {success('✔')} Loaded {cyan(str(len(hash_set)))} hash(es)  {algo_tag(algo_name)}")
    section_end()

    wordlist_path = pick_wordlist()

    section("Starting")
    print(f"  {dim('Algorithm')}  {col}{BOLD}{algo_name}{RST}")
    print(f"  {dim('Hashes   ')}  {cyan(str(len(hash_set)))}")
    print(f"  {dim('Wordlist ')}  {cyan(str(wordlist_path))}")
    section_end()

    wall_start = time.perf_counter()
    cracked, tried = crack(hash_set, hasher, algo_name, wordlist_path)
    elapsed = time.perf_counter() - wall_start

    uncracked     = len(hash_set) - cracked
    result_bg     = BG_GREEN if uncracked == 0 else BG_YELLOW
    result_label  = "ALL CRACKED" if uncracked == 0 else f"{cracked} cracked / {uncracked} remaining"

    section("Results")
    print(f"  {result_bg}{BLACK}{BOLD}  {result_label}  {RST}")
    print(f"\n  {dim('Cracked  ')}  {green(str(cracked))} / {str(len(hash_set))}")
    print(f"  {dim('Tried    ')}  {white(f'{tried:,}')} passwords")
    print(f"  {dim('Time     ')}  {yellow(f'{elapsed:.2f}s')}  {dim(f'({format_speed(tried, elapsed)})')}")
    section_end()

    print(f"  {DIM}Made by {CYAN}rikixz{RST}{DIM} — {CYAN}github.com/blaxkmiradev{RST}\n")

    sys.exit(0 if uncracked == 0 else 1)


if __name__ == "__main__":
    main()
