# Installing the Emanon CLI

The Emanon CLI is a Rust binary. Choose the method that fits your setup.

---

## From source (all platforms)

**Requirements:** Rust toolchain 1.75 or later. Install via [rustup](https://rustup.rs) if needed.

```sh
git clone https://github.com/h2ocoder/collatz
cd collatz/emanon/src/cli
cargo install --path .
```

`cargo install` places the `emanon` binary in `~/.cargo/bin/`. Make sure that's in your `PATH`:

```sh
# Bash / Zsh (add to ~/.bashrc or ~/.zshrc if not already present)
export PATH="$HOME/.cargo/bin:$PATH"
```

Verify:

```sh
emanon --version
```

---

## Prebuilt binaries

> **Status:** Prebuilt binaries will be available on the [GitHub Releases page](https://github.com/h2ocoder/collatz/releases) starting with the first public release. This section will be updated when they're available.

When available, download the binary for your platform:

| Platform | File |
|---|---|
| macOS (Apple Silicon) | `emanon-aarch64-apple-darwin.tar.gz` |
| macOS (Intel) | `emanon-x86_64-apple-darwin.tar.gz` |
| Linux (x86_64) | `emanon-x86_64-unknown-linux-gnu.tar.gz` |
| Windows | `emanon-x86_64-pc-windows-msvc.zip` |

Extract and move the binary to a directory in your `PATH`:

**macOS / Linux:**
```sh
tar xzf emanon-*.tar.gz
sudo mv emanon /usr/local/bin/
emanon --version
```

**Windows (PowerShell):**
```powershell
Expand-Archive emanon-*.zip .
Move-Item emanon.exe $env:USERPROFILE\bin\
# Make sure $env:USERPROFILE\bin is in your PATH
emanon --version
```

---

## Homebrew (macOS / Linux)

> **Status:** A Homebrew tap is planned. Not yet available.

When available:

```sh
brew tap h2ocoder/emanon
brew install emanon
```

---

## Verifying the install

Run a quick sanity check:

```sh
emanon --version
# emanon 0.1.0

emanon --help
# Emanon — git-based game engine for the multiverse
```

---

## Updating

**From source:**

```sh
cd /path/to/collatz
git pull
cd emanon/src/cli
cargo install --path . --force
```

**Homebrew** (when available):

```sh
brew upgrade emanon
```

---

## Prerequisites

Emanon calls `git` internally. You need git 2.30 or later:

```sh
git --version
# git version 2.39.0
```

On macOS, git comes with Xcode Command Line Tools (`xcode-select --install`). On Linux, use your package manager (`apt install git`, `dnf install git`, etc.). On Windows, install [Git for Windows](https://git-scm.com/download/win).

---

## Uninstalling

```sh
# Cargo install
cargo uninstall emanon

# Homebrew (when available)
brew uninstall emanon

# Manual binary
rm /usr/local/bin/emanon
```
