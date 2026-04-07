# 🔓 Hash Cracker

> **Made by [rikixz](https://github.com/blaxkmiradev)**

A fast, zero-dependency command-line hash cracker that **auto-detects** the algorithm, prompts for your hash file and wordlist, and can **auto-download a public wordlist** if you don't have one.

---

## Features

- **Interactive prompts** — asks for hash file path and wordlist path at runtime; no hardcoded filenames
- **Auto-download wordlists** — choose from built-in SecLists mirrors if you don't have a local wordlist
- **Auto-detection** — identifies MD5, SHA-1, SHA-256, and SHA-512 from digest length
- **Multi-hash mode** — load a full list and crack them all in a single pass over the wordlist
- **Live progress** — rolling speed readout every 50 000 attempts (K/M pw/s)
- **Colour output** — ANSI colours for cracked results, progress, and errors
- **Clean exit codes** — `0` = all cracked, `1` = some remain (pipeline-friendly)
- **Zero dependencies** — standard library only (`hashlib`, `urllib`, `pathlib`, `time`)

---

## Supported Algorithms

| Algorithm | Digest length |
|-----------|--------------|
| MD5       | 32 hex chars |
| SHA-1     | 40 hex chars |
| SHA-256   | 64 hex chars |
| SHA-512   | 128 hex chars |

---

## Requirements

- Python **3.10+**

---

## Setup

```bash
git clone https://github.com/blaxkmiradev/hash-cracker.git
cd hash-cracker
```

No installation needed — runs directly with the standard library.

---

## Usage

### Run

```bash
python3 hash_cracker.py
```

The script will prompt you interactively:

```
  Path to hash file [hash.txt] : /path/to/my/hashes.txt

  Path to wordlist (leave blank to download) :
```

If you leave the wordlist blank (or give a path that doesn't exist), a download menu appears:

```
  Available wordlists to download:
    1)  rockyou-75k (lightweight, fast)
    2)  top-10k common passwords
    3)  top-1k common passwords (quick test)
    0)  Cancel — exit

  Choose a wordlist [1] :
```

### Hash file format

One hash per line:
```
5f4dcc3b5aa765d61d8327deb882cf99
aaf4c61ddcc5e8a2dabede0f3b482cd9
```

### Wordlist format

One candidate password per line (standard `.txt` wordlist):
```
password
hello
letmein
```

---

## Example Output

```
╔══════════════════════════════════════════════════════╗
║              Hash Cracker  v2.0                      ║
║      Auto-detect · MD5 / SHA-1 / SHA-256 / SHA-512   ║
║                                                      ║
║  Author  : rikixz                                    ║
║  GitHub  : https://github.com/blaxkmiradev            ║
╚══════════════════════════════════════════════════════╝

  Path to hash file [hash.txt] : hashes.txt
  Path to wordlist (leave blank to download) : rockyou.txt

  Algorithm : MD5
  Hashes    : 3
  Wordlist  : rockyou.txt

  [+] CRACKED  5f4dcc3b5aa765d61d8327deb882cf99  →  'password'  (0.00s)
  [+] CRACKED  aaf4c61ddcc5e8a2dabede0f3b482cd9  →  'hello'     (0.00s)
  ...     50,000 tried | cracked: 2/3 | 2.1M pw/s
  [+] CRACKED  d8578edf8458ce06fbc5bb76a58c5ca4  →  'qwerty'    (0.03s)

  ✔ All hashes cracked!

  Result   : 3 cracked / 0 uncracked
  Tried    : 52,341 passwords
  Time     : 0.03s  (1.7M pw/s)

  Made by rikixz — github.com/blaxkmiradev
```

---

## Recommended Wordlists

| Name | Size | Link |
|------|------|------|
| rockyou.txt | ~133 MB | [SecLists](https://github.com/danielmiessler/SecLists) |
| top-1M passwords | ~8 MB | [SecLists](https://github.com/danielmiessler/SecLists) |
| Kaonashi | ~10 GB | [GitHub](https://github.com/kaonashi-passwords/Kaonashi) |

---

## Limitations

- **Dictionary attacks only** — no brute-force or rule mutations
- **Single-threaded** — no parallelism
- Salted hashes (bcrypt, argon2, PBKDF2, scrypt) are **not** supported

---

## Legal Notice

For **authorised security testing, CTF challenges, and educational purposes only.**  
Cracking hashes without permission is illegal. The author accepts no liability for misuse.

---

## License

[MIT](LICENSE) — © rikixz
