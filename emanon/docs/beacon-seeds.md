# Beacon Seeds — Verifiable Genesis for Emanon Universes

## Why genesis seeds matter

Every Emanon universe begins with a **genesis seed** — a 64-hex-char number that
drives the Collatz dynamics (genus assignment, merge resolution, bounty predicates).
Whoever controls that seed controls the starting state.

For casual play, a local random seed is fine.  But for **bounty-bound universes**
or **competitive tournaments**, you need *provable fairness*: anyone should be
able to confirm that you didn't cherry-pick a seed that conveniently satisfies the
bounty predicate before you started playing.

Beacon seeds solve this by tying the genesis seed to **publicly auditable randomness**
that existed before your universe was created.

---

## Quick start

```bash
# Verifiable genesis using the Solana devnet slot blockhash
emanon init my-world --beacon switchboard-vrf

# Verifiable genesis using the drand public randomness beacon
emanon init my-world --beacon drand

# Verifiable genesis using a specific Solana slot
emanon init my-world --beacon solana-slot:123456789

# Explicit seed (not verifiable — useful for reproducible testing)
emanon init my-world --seed 0xdeadbeef

# Default: local PRNG (casual play, no verifiability)
emanon init my-world
```

---

## Beacon types

### `switchboard-vrf` (recommended for Solana players)

Derives the seed from the **canonical blockhash** of the current Solana devnet
slot at the moment `emanon init` is called:

```
seed = SHA-256( slot_blockhash || ":" || wallet_pubkey )
```

Any observer with the `request_id` (e.g. `slot:123456789`) and your wallet
public key can independently verify the seed by fetching the same blockhash
from any Solana RPC and recomputing the SHA-256.

**Requirements:** network access to `https://api.devnet.solana.com`.  
**Optional:** a Solana wallet keypair at `~/.config/solana/id.json` personalises
the seed (prevents two players who happen to init at the same slot from getting
identical seeds).

### `drand`

Uses the [drand Cloudflare public randomness beacon](https://drand.cloudflare.com/).
The `randomness` field of the latest round becomes the genesis seed directly.

```
seed = drand_randomness_hex (latest round)
```

Verify at: `https://drand.cloudflare.com/public/<round>`

**Requirements:** network access to `https://drand.cloudflare.com`.  
**No wallet needed** — drand randomness is global and fully public.

### `solana-slot:N`

Like `switchboard-vrf` but pinned to a **specific Solana slot** you name.  
Use this when you want to agree on a seed with another player in advance:
both players agree on a future slot number, and anyone who calls
`emanon init --beacon solana-slot:<N>` after that slot is confirmed will get
the same seed (modulo wallet-pubkey personalisation).

---

## What gets committed

When any `--beacon` is used, `emanon init` writes two extra files inside
`.gitverse/` and includes a trailer in the genesis commit:

### `.gitverse/genesis.json`

```json
{
  "request_id": "slot:123456789",
  "slot": 123456789,
  "blockhash": "4vJ9JU1bJJE96RNPU2d3YMuHBB1yxBsS3b9Bk3y9rP",
  "seed_hex": "a3b4c5d6e7f8...",
  "source": "switchboard-vrf",
  "wallet_pubkey": "ed25519:7GRmBwnBChf32G...",
  "timestamp": "2026-04-14T17:00:00Z",
  "rpc_url": "https://api.devnet.solana.com",
  "network": "devnet",
  "verifiable": true,
  "verify_note": "sha256(slot_blockhash + \":\" + wallet_pubkey)"
}
```

### `.gitverse/genesis_seed`

Plain text file containing the 64-hex-char seed (also stored in `genesis.json`).
Used by the mining and genus-assignment subsystems.

### Genesis commit trailers

```
init: bootstrap my-world universe

Beacon: switchboard-vrf
Beacon-RequestId: slot:123456789
```

The trailers let anyone inspect `git log` to check provenance without reading
the `.gitverse/` files.

---

## Verifying a genesis seed

After receiving a universe (e.g. via `emanon bounty deliver`), verify the
genesis seed:

```bash
# 1. Read the beacon info from genesis.json
cat .gitverse/genesis.json

# 2. Re-derive the seed from the beacon source
emanon vrf verify \
  --request-id slot:123456789 \
  --seed a3b4c5d6... \
  --wallet-pubkey ed25519:7GRmBwnB...

# 3. Cross-check with the committed genesis_seed
diff <(cat .gitverse/genesis_seed) <(echo "a3b4c5d6...")
```

`emanon validate` also checks basic consistency (genesis.json seed_hex matches
genesis_seed) without requiring network access.

---

## Mining with beacon seeds

When mining a bounty-bound universe, use `--beacon` to make the first attempt
verifiable:

```bash
emanon mine <bounty-uuid> --beacon switchboard-vrf
```

Attempt 1 will use a Solana-slot-derived seed (and write `genesis.json`).
Subsequent attempts fall back to local PRNG (to avoid RPC rate limits on the
search loop).

If the bounty requires a beacon-attested seed in its predicate, use
`emanon vrf request` first to get a seed, then mine manually:

```bash
# Get a verifiable seed
emanon vrf request --source switchboard-vrf --save-to vrf-result.json

# Extract seed
SEED=$(cat vrf-result.json | grep seed_hex | cut -d'"' -f4)

# Init a universe with that seed
emanon init my-world --seed "$SEED"
# Then copy vrf-result.json → .gitverse/genesis.json manually for full provenance.
```

---

## When NOT to use beacon seeds

- **Casual play / local experiments** — local PRNG is faster, requires no network.
- **CI / automated tests** — use `--seed <fixed-hex>` for reproducibility.
- **Offline environments** — all beacon types require network access.

---

## Security notes

- The `switchboard-vrf` and `solana-slot:N` seeds are personalised by your
  `wallet_pubkey`.  Two players calling `--beacon switchboard-vrf` at the *same*
  slot will get **different seeds** if they have different wallets.
- `drand` seeds are **global** — anyone who calls `--beacon drand` at the same
  round will get the same seed.  This is intentional for use cases where multiple
  players want identical starting conditions.
- Beacon seeds prevent retroactive seed manipulation (you can't claim you started
  from a particular seed without the blockchain record), but they don't prevent
  *future* manipulation of the universe history.  The Collatz merge driver handles
  history integrity via genus stamps.
