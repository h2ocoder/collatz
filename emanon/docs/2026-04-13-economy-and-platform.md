# Economy & Platform Design

> The economic and settlement layer for the gitverse. Three-market
> architecture prevents pay-to-win by structural separation. Universes
> are first-class assets represented as compressed NFTs on Solana.
> Settlement in USDC. Status as soulbound reputation that cannot be
> bought. No native fungible token.
>
> Drafted 2026-04-13 from the session crystallizing the bounty market,
> universe-mining economy, anti-P2W structural design, and Solana platform
> selection. Builds on
> [[2026-04-13-gitverse-design|Gitverse Design]] (the substrate) and
> closes the loop on Emanon's full architecture.

## Thesis

Emanon's economy is built around one structural principle: **the most
powerful currency in the system must be the one you cannot buy.**

Every prior crypto-game failure traces to a single token mediating
entry, power, status, and governance simultaneously. That single token
*must* convert money into in-game advantage because that's the only way
it has utility. Pay-to-win isn't an accident in those games; it's
mechanical inevitability.

The escape is **market separation**. Three distinct value layers, each
with its own currency, where money in one cannot become advantage in
another. Successful non-crypto games have this implicitly (cosmetics,
skill, and social are separate economies). Crypto games collapse them.
Emanon doesn't.

## The Three-Market Architecture

### Market 1 — The Universe Market (USDC + cNFTs)

**What's traded:** computed universes meeting commissioned constraints.

**Who participates:** anyone who wants a specific kind of universe
(researchers, storytellers, players, AI agents) and anyone with compute
to mine them.

**Currency:** **USDC**, no native fungible token.

**Asset class:** the universe itself, represented as a **compressed NFT
(cNFT)** on Solana. The cNFT's metadata:

| Field | Content |
|---|---|
| Seed | Verifiable random seed (Switchboard VRF or drand) committed before mining |
| Commit hash | Final HEAD of the mined universe repo |
| Predicate | The bounty's constraint expression that the universe satisfies |
| Miner | Address + signature |
| Storage | IPFS / Arweave pointer for the actual repo bundle |
| Production cost | Compute attestation (rough hardware-time estimate) |
| Royalty | Miner's perpetual royalty on secondary sale |

The cNFT is the **certificate of computation**. It proves the universe
was produced honestly, satisfies the predicate, and is not a forgery.
Anyone can verify by re-running from the seed and checking the predicate
against the resulting state.

**Bounty/counter-offer protocol:**

```
Buyer:  bounty.post(constraint=C, max_price=p, expires=t)
Miner:  bid.submit(constraint=C, price=p',
                   eta=hardware_time_estimate)
Miner:  counter.submit(constraint=C ∧ C', price=p")
        # "I'll deliver C, but the easiest space also has C'"
Buyer:  accept(bid_id) | reject(bid_id) | counter(...)
Miner:  deliver(seed, repo_url, attestation, signature)
Engine: verify(repo_url, predicate=C ∧ C', expected_seed=seed)
        → escrow.release(price")
        → cnft.mint(buyer, metadata)
```

**P2W status:** none. Buying a universe doesn't make you better at
playing one. You still play the universe. Custom-mined seeds aren't
allowed in tournaments (Market 2). The universe market is for
narrative/research/aesthetic value, not power.

### Market 2 — The Tournament Layer (USDC pools, neutral seeds)

**What's contested:** ranked competitive play.

**Critical rule:** tournaments require **standardized seeds** drawn from
a public randomness beacon at tournament-start time, and the
**canonical merge driver**. No mined universes allowed; no custom
physics; no commissioned starting states.

**Currency:** USDC for entry fees; USDC out as prize pools.

**Operational model:**
- A tournament is a special registry entry with rules
- Entry: pay USDC fee, register your wallet/key
- Genesis: tournament smart contract pulls a seed from VRF at start time
- Play: standard merge driver, standard `values.json` defaults
- Settlement: prize pool distributed by leaderboard at end

**P2W status:** none. Entry fee buys you a seat, not an advantage.
Skill determines outcome. The tournament-bound universe IS the same
universe for every participant.

### Market 3 — The Reputation Layer (soulbound, non-transferable)

**What's earned:** status, trust, access.

**Currency:** a **soulbound NFT** per wallet, mutable metadata that
accumulates achievements. Non-transferable by program design (the
Anchor program rejects all transfer instructions).

**Earned by:**
- Bounties delivered successfully on Market 1
- Tournament wins on Market 2
- Curation work (helping others find universes, maintaining registries)
- Long-tenure presence in the registry
- Governance participation
- Code/protocol contributions

**Spent by:** nothing. Reputation is purely accumulating. The cost is
opportunity cost — what you did or didn't earn.

**What it gates:**

| Gate | Effect |
|---|---|
| Voting weight in governance | Higher rep = more weight on protocol changes |
| High-value bounty access | Sellers can require minimum-rep miners |
| Registry priority | Higher-rep universes appear first in browses |
| Tournament seeding | Seeded matchups favor high-rep players |
| Visible badges | Status displayed in client UIs |
| Contract trust assumptions | Counterparties trust high-rep parties more |

**P2W status:** structurally impossible. **You cannot buy reputation.**
You can only earn it through verified contribution. The most powerful
currency in the system is the one money cannot touch.

### Cross-Market Dynamics

The three markets reinforce each other without converting:

- High-reputation miners (Market 3) can charge premium prices on Market 1
- Tournament winners (Market 2) gain reputation (Market 3), which gives
  access to better Market 1 jobs
- Successful Market 1 sellers gain reputation (Market 3), which lets
  them enter higher-tier tournaments (Market 2)

But:
- Money never *becomes* reputation
- Reputation never *becomes* tournament victory
- Tournament victory never *becomes* mining throughput

They're **orthogonal value dimensions**. Their interactions are real
but their conversion paths are blocked.

## The cNFT Asset Class

This deserves its own treatment. cNFTs are not a side feature; they're
the fundamental innovation that makes universe-as-property work at scale.

### Why compressed NFTs

Standard Solana NFTs cost ~$5-50 to mint. Compressed NFTs (cNFTs) via
Metaplex Bubblegum cost ~$0.0001 per mint by storing data in Merkle
trees off-chain with on-chain root commitments.

For Emanon, this matters because:
- Mining is high-volume (thousands of universes/day at scale)
- Each mined universe should be certifiable
- Standard NFT economics would price out 99% of bounties
- Compressed NFTs make every tiny universe economically certifiable

### What a universe cNFT represents

It's not a JPEG. It's not a "collectible." It's a **certificate of
computation** with content-addressable provenance:

- The seed proves the starting state was random and pre-committed
- The commit hash proves the trajectory existed at delivery time
- The predicate proves the universe satisfies the agreed constraint
- The miner signature proves who did the work
- The storage pointer makes the actual repo retrievable

**Verification is cheap:** anyone can clone the repo, verify the seed
matches the genesis commit, replay the trajectory, check the predicate
holds. The cNFT is just the on-chain index entry to all this.

### Universe ownership semantics

Owning a universe cNFT confers:

| Right | Mechanism |
|---|---|
| **Display authority** | You're listed as the owner in the registry |
| **Resale rights** | You can transfer the cNFT (with miner royalty) |
| **Branch authority** | You can publish "official" forks of the universe |
| **Curation rights** | You can lock the cNFT to prove permanence |
| **Derivative authority** | You can authorize derivative works (with terms) |

Owning does *not* confer:
- Exclusive read access (universes are public; the cNFT is the deed, not a paywall)
- Ability to alter the trajectory (the universe is immutable post-mint)
- Authority over other people's branches (they can fork freely)

### Fork lineage and royalties

When someone branches from your universe and mints a new cNFT for the
branch, the **royalty cascade** gives you a small cut. This creates a
derivative-works economy:

```
Universe A (mined by Alice)
  ↓ branched & rebuilt by Bob → Universe B (Alice gets 5% of any sale)
    ↓ branched & rebuilt by Carol → Universe C (Alice 2.5%, Bob 5%)
```

This rewards the **discovery of fertile starting points** even more
than it rewards specific mined universes. A miner who finds an
unusually-rich seed (one that produces many compelling derived
universes) earns a perpetual stream from descendants. This is the
crypto analogue of academic citation — discovery has long-tail value.

### Anti-speculation defenses

Even without a fungible token, cNFTs *can* become speculative.
Mitigations:

| Defense | Effect |
|---|---|
| **On-chain production cost** | cNFT metadata includes verified compute cost; speculation past 10× cost looks silly |
| **Miner perpetual royalty** | 5-10% of every resale goes to original miner — captures speculation premium for the worker |
| **Anti-wash-trading monitoring** | Volume on cNFTs is easy to fake; protocol-level detection flags suspicious patterns |
| **Curated vs. open marketplaces** | Canonical/competitive layer doesn't touch the speculation market |
| **No floor-price hyping** | Protocol does not surface floor prices; collections are not gamified the way OpenSea collections are |

Speculation will happen. The defenses bound it without trying to
eliminate it. Worst case: someone overpays for a universe NFT, which is
their own choice, not an extraction from other players.

## The Solana Decision

### Why Solana specifically

**Proof of History parallel.** Solana's consensus uses a sequential
SHA-256 hash chain — a verifiable delay function. This is the
*structural twin* of Emanon's universe-mining-as-VDF model (referenced
in the [[Verifiable Delay Function]] spec). The narrative is clean:
**Solana's PoH makes blockchain time provable; Emanon's mining makes
universe history provable. Both are VDF artifacts at different layers.**
This is technical truth, not marketing — the same construction
underpins both.

**Compressed NFTs solve the asset-class economics.** ~$0.0001 per mint
makes per-universe certification viable at scale. No other major chain
offers this on Bubblegum/Metaplex's level today.

**Sub-second finality matches negotiation.** The bounty/counter-offer
protocol is real-time. ~400ms block time means a full negotiation
round-trip takes seconds, not minutes.

**Micropayment economics.** $0.00025/tx means a $1 bounty has 0.025%
fee overhead. On Ethereum L1 it would be 100% overhead. Small bounties
are economically viable, and *most bounties will be small*.

**USDC native.** No bridges, no wrapped tokens. Players see "$5" and
pay $5.

**Rust ecosystem alignment.** The CLI is most likely Rust (single static
binary, fast startup, perfect for git wrapping). Solana programs are
also Rust via Anchor. Same toolchain, same mental model.

**x402 status note:** x402 is HTTP-layer and chain-agnostic but its
current dominant deployment is on Base. **Practical recommendation:**
mainline payments use direct USDC on Solana from day one. Add x402
when Solana support matures (or via Base bridge for early adopters who
demand it). Don't let x402's current Base bias dictate the chain.

### The honest cons

- **Network halts.** Solana has historically halted occasionally under
  load. Improving but real. Not blocking for game economics (universes
  don't need 100% uptime to function), but worth knowing.
- **Validator centralization.** High hardware costs limit validator
  count. Real concern; Emanon doesn't depend on extreme decentralization
  but worth tracking.
- **Smaller dev mindshare than EVM.** Hiring contractors for Solana work
  is harder than EVM. Manageable.

### Why not other chains

- **Base / Ethereum L2:** broader ecosystem, native x402, but mint costs
  are 10-100× cNFTs. Lose the per-universe certification economics.
- **Sui / Aptos:** elegant Move language but smaller ecosystems and no
  cNFT equivalent at scale today.
- **Bitcoin L2 (Stacks, etc.):** narratively pure but slow and tooling-poor.
- **Multi-chain via bridges:** complexity multiplier, security surface,
  bad for v1.

The tradeoffs land Solana for this specific use case.

## On-Chain Architecture

| Component | Tech | Purpose |
|---|---|---|
| **Bounty escrow** | Anchor program | Holds USDC until verifiable delivery; releases on predicate-pass |
| **Universe cNFT** | Bubblegum / Metaplex | Mass-mint universe certificates at ~$0.0001 |
| **Soulbound reputation** | Custom Anchor program | Non-transferable per-wallet NFT; mutable metadata |
| **Registry index** | One Anchor account per universe | Authoritative on-chain index of canonical universes |
| **VRF** | Switchboard or Pyth | Verifiable randomness for seeds |
| **Tournament contracts** | Anchor program | Entry fee pooling, neutral-seed enforcement, prize distribution |
| **Identity** | Solana wallet + GPG | Wallet for payments; GPG for git commit signing (separate but bound) |
| **Storage (off-chain)** | IPFS + Arweave | Universe repo bundles too large for chain; pointers stored in cNFTs |

Everything heavy is off-chain. The chain holds hashes, ownership, and
escrow logic. This is intentional — keeps fees minimal and respects
the chain's role as settlement layer rather than compute layer.

## Funding the Project

**No pre-sale. No ICO. No founder token allocation. No native fungible
token.** This is non-negotiable. Pre-sales destroy community trust on
contact, and the entire architecture is built around earned-not-bought.

Sustainable funding sources, in priority order:

1. **Marketplace fee (1-2%)** on Market 1 settlements. Aligned with
   player value creation; small enough to not feel extractive.
2. **Tournament hosting fee (5%)** of prize pools for officially-hosted
   events.
3. **Premium registry tier.** Free for individuals; paid for organizations
   running large registries.
4. **Optional cosmetics.** Vanity universe addresses, custom badge art,
   named registries. Pure cosmetic; never affects gameplay.
5. **Grants.** Solana Foundation (PoH-VDF parallel), Anthropic
   (agent-skill story), academic grants (Collatz / symbolic-regression
   angle). Cleanest early funding.

Notably absent: token speculation, VC token-vest, founder allocation,
private sales. Open source from day one means community trust is the
most valuable asset.

## Player Experience by Phase

The crypto layer must be invisible to the median player.

| Day | Activity | Crypto needed? |
|---|---|---|
| Day 1 | `emanon init` | No |
| Day 1 | `emanon play` / `snapshot` | No |
| Day 1 | Push to GitHub | No (free git host) |
| Day 5 | `emanon bounty list` | No (browsing is free) |
| Day 7 | First wallet setup | Yes, optional |
| Day 7 | `emanon mine <bounty>` | Yes, USDC payout to wallet |
| Day 10 | `emanon mint <universe>` | Yes, optional cNFT mint |
| Day 30 | `emanon tournament join` | Yes, USDC entry fee |

**90% of players never touch crypto.** They play, fork, merge, enjoy.
The 10% who do are buying real artifacts and being paid for real
compute. Nobody is being scammed; nobody is being yield-farmed; nobody
is being pressured to speculate.

This is the YouTube model: most viewers watch free, some creators
monetize, the platform sustains because monetization is opt-in and
aligned with real value creation.

## Build Sequence Integration

Crypto enters at M5+ and is opt-in at every layer above the base game.

| Phase | Component | Crypto |
|---|---|---|
| M0 | CLI skeleton (`init`, `snapshot`) | None |
| M1 | Collatz merge driver | None |
| M2 | Two-player local play | None |
| M3 | Agent skill | None |
| M4 | Public template repo | None |
| M5 | Registry + optional cNFT mint | Opt-in |
| M6 | Bounty CLI (escrow simulation) | Opt-in |
| M7 | Switchboard VRF for seeds | Opt-in |
| M8 | Real USDC settlement + soulbound rep | Opt-in |
| M9 | Counter-offer protocol on-chain | Opt-in |

Base game is fully playable through M4 without ever touching a wallet.
Marketplace participation is layered on for those who want it.

## The Public Position

The framing for public announcement matters because the crypto-game
space is a smoking crater of broken promises. Emanon must
differentiate aggressively.

> Emanon has no token. We use USDC for payments because dollars are
> stable and players think in dollars. We use compressed NFTs to
> certify computed universes, because those are real artifacts
> deserving real provenance. We use soulbound reputation because status
> should be earned, not bought. We separate the universe market from
> the tournament layer because pay-to-win is a choice, and we choose
> against it.
>
> The base game is free, open-source, and works without crypto forever.
> The marketplace is opt-in for those who want to buy or sell computed
> universes. We take 1-2% on settlements and that's how we survive.
>
> We chose Solana because its Proof of History is a verifiable delay
> function, structurally parallel to the work miners do producing
> universes. Both are about making time and computation provable. The
> chain matches the game.

## Risks Worth Naming

1. **Collector speculation.** Even without a fungible token, cNFTs can
   become speculative. Mitigated by miner royalties, on-chain cost
   transparency, and separation from competitive layers — but not
   eliminated. Bounded harm.
2. **Solana network halts.** Real but improving. Game state survives
   halts (universes are off-chain repos); only marketplace operations
   pause.
3. **x402 ecosystem currently Base-biased.** Use direct USDC on Solana
   for now; layer x402 when Solana support matures.
4. **Regulatory ambiguity around cNFTs.** They're closer to digital
   collectibles than securities, but jurisdictions vary. Not blocking
   but worth monitoring.
5. **Reputation system gaming.** Sophisticated actors will try to farm
   reputation. Detection and slashing required. Standard
   anti-Sybil hygiene.
6. **Bootstrap problem.** The marketplace needs both buyers and miners
   from day one. Likely solution: seed initial bounties from grants and
   internal play; build organic demand from there.

## The Complete Architecture

```
╔══════════════════════════════════════════════════════════════╗
║                          EMANON                               ║
║                                                               ║
║  Substrate:    Git (gitverse)                                 ║
║  Dynamics:     Collatz (T^k bit destruction, mixing)          ║
║  Distribution: P2P via git remotes (solo → MMO continuum)     ║
║  Discovery:    EML symbolic regression (deferred)             ║
║                                                               ║
║  Economy:      Three-market separation                        ║
║    Market 1:   Universe trade (USDC + cNFTs)                  ║
║    Market 2:   Tournaments (USDC pools, neutral seeds)        ║
║    Market 3:   Reputation (soulbound, earned only)            ║
║                                                               ║
║  Settlement:   Solana                                         ║
║    PoH-VDF parallel to Collatz-VDF mining                     ║
║    cNFTs (Bubblegum) for universe certification               ║
║    USDC for payments                                          ║
║    Switchboard VRF for verifiable seeds                       ║
║    Anchor programs for escrow + reputation                    ║
║                                                               ║
║  Funding:      1-2% marketplace fees + grants                 ║
║                No pre-sale, no ICO, no founder vest           ║
║                                                               ║
║  Interface:    CLI (emanon/src/cli) + agent skill             ║
║  Distribution: Open source from day 1; fork to play           ║
╚══════════════════════════════════════════════════════════════╝
```

A peer-to-peer multiverse where information dynamics are physics, git
is spacetime, narrative artifacts are commodities, and pay-to-win is
structurally impossible by design.

## Related

- [[2026-04-13-gitverse-design|Gitverse Design]] — the substrate this
  economy operates on
- [[2026-04-13-collatz-scrambling-protocol|Collatz Scrambling Protocol]]
  — the underlying information-theoretic model
- [[Verifiable Delay Function]] — Collatz orbits as VDF; structural
  parallel to Solana PoH
- [[Energy & Conservation]] — in-game energy economy that maps to the
  USDC settlement layer at the boundary
- [[Multiplayer & Sessions]] — async tick model that fits the
  bounty-driven async play style
