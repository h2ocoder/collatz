# VRF Costs & Cost Model

> Cost analysis for `emanon vrf request` — the verifiable random seed provider
> used to commit universe genesis seeds before mining begins.

## Devnet (testing)

Devnet SOL is free and can be airdropped:

```bash
solana airdrop 2 --url https://api.devnet.solana.com
```

| Operation | Cost (devnet SOL) | Notes |
|-----------|-------------------|-------|
| `getSlot` RPC call | Free | Read-only JSON-RPC |
| `getBlock` RPC call | Free | Read-only JSON-RPC |
| SHA-256 seed derivation | Free | Local computation |
| **Total per VRF request** | **0 SOL** | No transactions submitted |

The current implementation reads the canonical blockhash for the current slot via
Solana's JSON-RPC API and derives the seed locally.  No transactions are submitted,
so there are zero network fees.

## Mainnet-beta (production)

The same approach applies on mainnet-beta since read-only RPC calls are free.
However, for **full Switchboard VRF** (on-chain VRF account protocol), costs apply:

| Operation | Estimated Cost (mainnet SOL) | At $150/SOL |
|-----------|------------------------------|-------------|
| Current: blockhash-based VRF | 0.000000000 SOL | $0.00 |
| Upgrade: Switchboard VRF account creation | ~0.002 SOL (rent-exempt) | ~$0.30 |
| Upgrade: VRF request transaction | ~0.000005 SOL | ~$0.00075 |
| Upgrade: Oracle fulfillment (network overhead) | ~0.000025 SOL | ~$0.004 |
| **Total per bounty (upgrade path)** | **~0.002030 SOL** | **~$0.305** |

## Verification cost

Verification is always free — it only requires a read-only `getBlock` RPC call
plus local SHA-256 computation.

## Upgrade path to full Switchboard VRF

The current implementation uses slot blockhashes as a practical, zero-cost VRF.
The design supports upgrading to on-chain Switchboard VRF when:

1. The `switchboard-solana` Rust crate is added as a dependency.
2. A funded mainnet wallet is available.
3. Stronger randomness guarantees are required (e.g. to prevent miner-slot
   correlation attacks on mainnet bounties).

The `VrfResult` wire format is stable — the `request_id`, `seed_hex`, and
`wallet_pubkey` fields will remain unchanged after the upgrade.

## Comparison: alternative VRF sources

| Source | Cost | Verifiable | Latency | Notes |
|--------|------|------------|---------|-------|
| `switchboard-vrf` (blockhash) | Free | ✓ | <1 s | Current implementation |
| Full Switchboard VRF (on-chain) | ~0.002 SOL | ✓ | 5–30 s | Upgrade path |
| `drand` (Cloudflare/League of Entropy) | Free | ✓ | <1 s | Alternative |
| `local-prng` (/dev/urandom) | Free | ✗ | <1 ms | Testing only |

## RPC provider options

| Provider | Devnet | Mainnet | Rate limit (free tier) |
|----------|--------|---------|------------------------|
| `api.devnet.solana.com` (Solana Labs) | ✓ | — | ~100 req/s |
| `api.mainnet-beta.solana.com` (Solana Labs) | — | ✓ | ~10 req/s |
| Helius | ✓ | ✓ | 10 req/s (free), 500k/month |
| QuickNode | ✓ | ✓ | 5 req/s (free) |
| Triton | ✓ | ✓ | 30 req/s (free) |

For production use, a dedicated RPC provider (Helius, QuickNode, or Triton) is
recommended to avoid public rate limits.  Configure with:

```toml
# ~/.config/emanon/config.toml
[wallet]
keypair_path = "~/.config/solana/id.json"
rpc_url      = "https://rpc.helius.xyz/?api-key=YOUR_KEY"
```

## How to use `emanon vrf request`

### Quick start (devnet, no wallet required)

```bash
# Generate a seed from the current devnet slot blockhash.
# Wallet defaults to ~/.config/solana/id.json (pubkey only — no transaction).
emanon vrf request

# Use local PRNG for offline testing (not verifiable).
emanon vrf request --source local-prng
```

### With explicit wallet and RPC

```bash
emanon vrf request \
  --keypair ~/.config/solana/my-wallet.json \
  --rpc https://api.devnet.solana.com
```

### Verify a previously issued seed

```bash
# Verify from the saved result file.
emanon vrf verify --from-file .gitverse/vrf-result.json

# Verify inline (share with any third party).
emanon vrf verify \
  --request-id slot:12345678 \
  --seed a3b4c5d6... \
  --wallet-pubkey ed25519:7GRmBw...
```
