# Emanon Wallet Setup

This guide walks you through creating or importing a Solana wallet for use with
the Emanon CLI.  The wallet is used for on-chain actions: posting bounties,
minting Universe cNFTs, and tracking reputation on Solana.

---

## Prerequisites

All wallet operations use the **Solana CLI** to generate and inspect keypairs.
Install it before running `emanon wallet init`:

```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Then verify the install:

```bash
solana --version          # e.g. solana-cli 1.18.x
solana-keygen --version   # same version
```

Full instructions: <https://docs.solanalabs.com/cli/install>

---

## Quick Start (devnet)

```bash
# 1. Generate a new keypair
emanon wallet init

# 2. Request 1 devnet SOL (for gas fees on devnet)
emanon wallet airdrop

# 3. Check your balances
emanon wallet show
```

Expected output for `emanon wallet show`:

```
Emanon Wallet
=============
  File:       /home/alice/.config/emanon/wallet.json
  Public key: 7GRmBwnBChf32GrKBbqBRR...
  Network:    devnet  (https://api.devnet.solana.com)

  SOL:   1.000000000 SOL
  USDC:  0.000000 USDC
```

---

## Wallet Location

The Emanon wallet is stored at:

```
~/.config/emanon/wallet.json
```

This is a standard Solana JSON keypair file — a flat array of 64 unsigned
bytes where the first 32 bytes are the Ed25519 private key seed and the last
32 bytes are the compressed public key.

The file is created with `0600` permissions (owner read+write only).  Emanon
warns you if it detects that the permissions are too permissive:

```
warning: /home/alice/.config/emanon/wallet.json has permissions 644 — private key may be exposed.
Fix with: chmod 0600 /home/alice/.config/emanon/wallet.json
```

---

## Commands Reference

### `emanon wallet init`

Generate a new keypair and save it to `~/.config/emanon/wallet.json`.

```bash
emanon wallet init                   # devnet (default)
emanon wallet init --force           # overwrite existing wallet
emanon wallet init --network mainnet # mainnet-beta
emanon wallet init --output /custom/path/wallet.json
```

⚠ **WARNING**: `--force` will permanently overwrite your existing private key.
Back up `~/.config/emanon/wallet.json` before using this flag.

### `emanon wallet import <keypair-path>`

Import an existing Solana keypair as your Emanon wallet.

```bash
# Import the default Solana CLI keypair
emanon wallet import ~/.config/solana/id.json

# Import from a Ledger export or other source
emanon wallet import ~/Downloads/my-keypair.json
```

The source file must be a valid 64-byte Solana JSON array.  The file is
copied to `~/.config/emanon/wallet.json` with `0600` permissions.

### `emanon wallet show`

Display your wallet's public key and on-chain balances.

```bash
emanon wallet show                   # devnet (default)
emanon wallet show --network mainnet # mainnet-beta
emanon wallet show --keypair /custom/path/wallet.json
```

Balances are queried from the Solana RPC.  A few seconds of lag is normal.
If the RPC is unavailable the command still prints your public key; balance
lines show `(unavailable — <reason>)`.

### `emanon wallet airdrop`

Request a devnet SOL airdrop from the public Solana faucet.

```bash
emanon wallet airdrop            # request 1.0 SOL (default)
emanon wallet airdrop --amount 2 # request 2.0 SOL (faucet cap)
```

Airdrops are **only available on devnet** — the command refuses to run with
`--network mainnet`.  The faucet rate-limits requests; wait ~24 hours between
airdrops if you hit the limit.

For larger devnet balances use the web faucet: <https://faucet.solana.com>

---

## Using the Wallet with Other Commands

Once `~/.config/emanon/wallet.json` exists, other commands use it
automatically:

| Command | Wallet usage |
|---------|-------------|
| `emanon bounty post` | Derives `buyer_pubkey` from the wallet if `[bounty] buyer_pubkey` is not set in config |
| `emanon vrf request` | Uses wallet pubkey to personalise the VRF seed (see [vrf-costs.md](vrf-costs.md)) |
| `emanon registry push` | Signs the registry entry with your wallet pubkey |

### Explicit config override

If you prefer to use a specific pubkey rather than the wallet file, set it in
`~/.config/emanon/config.toml`:

```toml
[bounty]
buyer_pubkey = "ed25519:<your-base58-pubkey>"
```

Explicit config values always take precedence over the wallet file.

---

## Mainnet Opt-in

By default Emanon targets **devnet** for safety.  To use mainnet-beta:

```bash
# Generate (or verify) your mainnet wallet
emanon wallet init --network mainnet  # generates a separate wallet — or reuse devnet wallet
emanon wallet show --network mainnet
```

Add to `~/.config/emanon/config.toml`:

```toml
[wallet]
rpc_url = "https://api.mainnet-beta.solana.com"
```

Mainnet SOL has real monetary value.  Understand the risks before opting in.
Emanon will never airdrop funds on mainnet.

---

## Backup and Recovery

Your private key is **not recoverable** if lost.  Back up your wallet file
securely:

```bash
# Encrypted backup with GPG
gpg --symmetric --cipher-algo AES256 ~/.config/emanon/wallet.json

# Or simply copy to secure offline storage
cp ~/.config/emanon/wallet.json ~/Backups/emanon-wallet-$(date +%Y%m%d).json
chmod 0600 ~/Backups/emanon-wallet-*.json
```

Alternatively, use `solana-keygen recover` to re-derive a keypair from a
BIP39 seed phrase if you originally generated it with `--bip39-passphrase`.

---

## Troubleshooting

### `solana-keygen not found`

Install the Solana CLI: <https://docs.solanalabs.com/cli/install>

### `Wallet already exists`

Use `--force` to overwrite (backs up first is your responsibility):

```bash
cp ~/.config/emanon/wallet.json ~/.config/emanon/wallet.json.bak
emanon wallet init --force
```

### Balance shows `(unavailable)`

The Solana devnet RPC is sometimes rate-limited.  Wait a few seconds and
retry, or supply a custom RPC endpoint:

```toml
# ~/.config/emanon/config.toml
[wallet]
rpc_url = "https://your-private-devnet-rpc.example.com"
```

### Permissions warning

Run: `chmod 0600 ~/.config/emanon/wallet.json`

---

## Security Notes

- The `wallet.json` file contains your **unencrypted private key**.
  Anyone with access to this file can drain your wallet.
- Do **not** commit it to git. Emanon's `.gitignore` template excludes it
  by default (`*.json` is not excluded, so add `wallet.json` to your shell
  profile's global gitignore if needed).
- Consider hardware wallet support (Ledger) for mainnet funds — see
  the Solana docs for `solana config set --keypair usb://ledger`.

---

## See Also

- [vrf-costs.md](vrf-costs.md) — VRF seed generation and Solana cost estimates
- [beacon-seeds.md](beacon-seeds.md) — Verifiable genesis seeds
- [bounty-protocol.md](bounty-protocol.md) — Bounty posting and delivery
