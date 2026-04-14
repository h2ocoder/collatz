# Vertical Slice 1: "First Light" — Design Spec

**Date:** 2026-04-13
**Status:** approved

## Goal

Build the minimum to play the tutorial end to end. Genesis, scan, observe, share, light a star, survive 20 ticks, make a choice. Polished UI from day one with a design system and Storybook. Every component reviewable in isolation.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (App Router) + React + TypeScript |
| Styling | Tailwind CSS + CSS custom properties (design tokens) |
| Component dev | Storybook |
| Fonts | Inter (UI), Literata (narrative), JetBrains Mono (data) |
| Backend | ASP.NET Core Web API + SignalR (C#) |
| ORM | Entity Framework Core |
| Database | PostgreSQL |
| Identity | Dex (OpenID Connect) |
| SDK generation | NSwag (TypeScript client from OpenAPI spec) |
| Real-time | SignalR (tick events, scan results, observations, energy updates) |

## Architecture

```
emanon/
  src/
    client/                         ← Next.js frontend
      app/
        page.tsx                    ← Landing / run selection
        game/page.tsx               ← Game client
        login/page.tsx              ← OIDC login flow
      components/
        ui/                         ← Design system primitives
          Button.tsx
          Card.tsx
          Badge.tsx
          EnergyBar.tsx
          ProgressBar.tsx
          Input.tsx
          Tooltip.tsx
        game/                       ← Game-specific components
          GenesisPrompt.tsx
          MapView.tsx
          LogView.tsx
          PrimeNode.tsx
          ScanRadius.tsx
          ObjectiveOverlay.tsx
          DecisionPrompt.tsx
          StarNode.tsx
          AnomalyNode.tsx
      lib/
        tokens/
          tokens.css                ← CSS custom properties
          colors.ts                 ← Token exports for JS
        sdk/                        ← NSwag auto-generated TypeScript client
        auth/                       ← OIDC client helpers (Dex integration)
        signalr/                    ← SignalR connection manager + typed hooks
      stories/
        ui/                         ← One story per UI primitive
        game/                       ← One story per game component
      .storybook/
      tailwind.config.ts
      next.config.ts
      package.json
      tsconfig.json

    server/
      Emanon.sln
      Emanon.Api/                   ← ASP.NET Core Web API + SignalR
        Program.cs
        Hubs/
          GameHub.cs                ← Real-time game events
        Controllers/
          AuthController.cs         ← Token exchange / user info
          ScenarioController.cs     ← Start/join/leave scenarios
          PrimeController.cs        ← Prime CRUD + actions
        Services/
          Engine/
            EventService.cs         ← Event creation, log append, recipe tracking
            PrimeService.cs         ← Prime creation, addressing, factorization
            EnergyService.cs        ← Budget, spend, receive, death detection
            TickService.cs          ← Turn loop orchestration
            ScanService.cs          ← Bloom filter queries
            NpcService.cs           ← Scripted NPC behavior tree evaluation
            ScenarioService.cs      ← Scenario lifecycle, objective evaluation
            VdfService.cs           ← Collatz orbit computation
          Auth/
            DexAuthService.cs       ← JWT validation, user resolution
        Middleware/
          JwtAuthMiddleware.cs

      Emanon.Domain/                ← Domain models, no dependencies
        Models/
          Event.cs
          Log.cs
          Prime.cs
          Composite.cs
          Recipe.cs
          BloomFilter.cs
          Star.cs
          MetaProfile.cs
          Scenario.cs
          Objective.cs
        Enums/
          PrimeType.cs              ← Particle, Force, Field, Law, Story, Witness
          GovernanceType.cs         ← Anarchic, Constitutional, Authoritarian
          DeathType.cs              ← EnergyDeath, Absorption, BlackHole, Voluntary
          LootType.cs               ← Atlas, TrustResidue, MerkleFragment

      Emanon.Data/                  ← EF Core + PostgreSQL
        EmanonDbContext.cs
        Migrations/
        Configurations/             ← EF entity configurations
        Repositories/
          PrimeRepository.cs
          EventRepository.cs
          ScenarioRepository.cs
          MetaProfileRepository.cs

      Emanon.Contracts/             ← Shared DTOs — single source of truth for SDK
        Requests/
          CreatePrimeRequest.cs
          EmitEventRequest.cs
          ScanRequest.cs
          ObserveRequest.cs
          StartScenarioRequest.cs
        Responses/
          PrimeResponse.cs
          EventResponse.cs
          ScanResultResponse.cs
          ObservationResponse.cs
          TickStateResponse.cs
          ScenarioStateResponse.cs
        Hubs/
          IGameHubClient.cs         ← Server → client SignalR methods
          IGameHubServer.cs         ← Client → server SignalR methods

      Emanon.Tests/
        Engine/
        Api/
        Integration/

  docs/                             ← Obsidian vault (exists)
  seed.txt

  docker-compose.yml                ← PostgreSQL + Dex + API
```

## Identity (Dex)

- Dex runs as a Docker container alongside PostgreSQL
- Issues JWTs via OpenID Connect
- Pluggable connectors: GitHub, Google, email/password for dev
- ASP.NET Core validates JWTs via standard auth middleware
- SignalR connections authenticated via JWT (access_token query param)
- Meta-profile linked to Dex subject ID — persistent identity across runs
- Client handles OIDC redirect flow on `/login`

## Design System: Cosmic Manuscript

### Color Tokens

```css
:root {
  /* Backgrounds */
  --color-void: #0a0a12;
  --color-deep: #0f0f1a;
  --color-surface: #1a1520;
  --color-raised: #242030;

  /* Text */
  --color-text-primary: #e2e0f0;
  --color-text-secondary: #b8b0d0;
  --color-text-muted: #6b6880;

  /* Accents */
  --color-accent-violet: #8b5cf6;
  --color-accent-blue: #3b82f6;

  /* Semantic */
  --color-star: #f59e0b;
  --color-danger: #ef4444;
  --color-trust: #22c55e;

  /* Borders */
  --color-border: #2a2540;
  --color-border-subtle: #1f1b2e;
}
```

### Typography

| Role | Font | Weight | Use |
|------|------|--------|-----|
| UI | Inter | 200-400 | Headers, labels, buttons, navigation |
| Narrative | Literata | 400, 400i | Lore text, witness testimony, genesis prompt, objectives |
| Data | JetBrains Mono | 400 | Event logs, tick counters, addresses, bloom filter data |

### Spacing

4px base unit. Scale: 1(4), 2(8), 3(12), 4(16), 6(24), 8(32), 12(48), 16(64).

### Component Library (Storybook)

Every component gets a Storybook story with:
- Default state
- All variants (primary/secondary/ghost for buttons, etc.)
- Interactive states (hover, active, disabled)
- Dark-only (the game is always dark mode)

#### UI Primitives (Phase 1)

| Component | Variants | Story |
|-----------|----------|-------|
| Button | primary, secondary, ghost, danger | All states + sizes |
| Card | default, highlighted, selected | With mock content |
| Badge | type (particle/force/field/law/story/witness), status | All 6 types |
| EnergyBar | healthy, warning, critical, empty | Animated transitions |
| ProgressBar | default, with label | Various fill levels |
| Input | text, genesis (special styled) | With placeholder, focus |
| Tooltip | default | Positioning variants |

#### Game Components (Phase 5)

| Component | Description | Story |
|-----------|-------------|-------|
| GenesisPrompt | "Hello world. I am ______" full-screen input | Empty, typing, submitted |
| MapView | Spatial view of address space with signals | Empty, populated, scanning |
| LogView | Event log reader with decision prompts | Short log, long log, with decisions |
| PrimeNode | A prime on the map (type-colored, size=mass) | All 6 types, various masses |
| StarNode | A star on the map (luminosity glow) | Healthy, dying, dead |
| AnomalyNode | Pulsing anomaly on the map | Various types |
| ScanRadius | Animated scan radius circle | Expanding, settled |
| ObjectiveOverlay | Tutorial objective in corner | Active, completing, completed |
| DecisionPrompt | Share/observe/merge choice at bottom of LogView | All option sets |

## SignalR Hub Interface

```csharp
// Server → Client (push events)
public interface IGameHubClient
{
    Task OnTickAdvanced(TickStateResponse state);
    Task OnScanResult(ScanResultResponse result);
    Task OnObservationResult(ObservationResponse result);
    Task OnEnergyChanged(int current, int max);
    Task OnMergeProposal(MergeProposalResponse proposal);
    Task OnObjectiveCompleted(string objectiveId);
    Task OnObjectiveStarted(string objectiveId, string text);
    Task OnGameOver(DeathType deathType, LootResponse loot);
}

// Client → Server (player actions)
public interface IGameHubServer
{
    Task SubmitGenesis(string genesisLine);
    Task Scan(ScanRequest request);
    Task Observe(ObserveRequest request);
    Task Emit(EmitEventRequest request);
    Task ShareLog(Guid targetPrimeId);
    Task ProposeMerge(Guid targetPrimeId);
    Task EndTurn();
}
```

## NSwag SDK Generation

- Source: OpenAPI spec generated from Emanon.Api controllers
- Output: `client/lib/sdk/EmanonClient.ts`
- Regenerated on build (or via npm script)
- SignalR hub types maintained manually in `client/lib/signalr/` from Emanon.Contracts hub interfaces (NSwag doesn't cover SignalR)

## Tutorial: First Light

### Starting Distribution
- 1 dim star (fuel for ~30 ticks)
- 1 friendly NPC (willing to share/merge, trust 0.3)
- 1 cautious NPC (shares only after player shares first, trust 0.1)
- 1 witness narrator (scripted attestation log)
- 1 bloom filter anomaly (for objective 7 exploration path)
- Player starts with 100 energy

### Objective Chain
1. "Declare yourself." → Player submits genesis line
2. "Scan your surroundings." → 3+ scans completed
3. "Observe something." → Any prime observed
4. "Share your log." → Log shared with any prime
5. "Light a star." → Star ignites (2+ contributors)
6. "Survive 20 ticks." → Reach tick 20 with energy > 0
7. "Make a choice." → Player chooses merge or solo exploration

## Build Order

### Phase 1: Scaffolding + Design System
1. Scaffold Next.js app with Storybook + Tailwind
2. Create design tokens (tokens.css + tailwind.config.ts)
3. Configure fonts (Inter, Literata, JetBrains Mono via next/font)
4. Scaffold C# solution (Api, Domain, Data, Contracts, Tests)
5. Docker Compose: PostgreSQL + Dex
6. Build UI primitives with Storybook stories: Button, Card, Badge, EnergyBar, Input

### Phase 2: Domain + Data
7. Domain models: Event, Log, Prime, Recipe, Star, MetaProfile, Scenario, Objective
8. Domain enums: PrimeType, GovernanceType, DeathType, LootType
9. EF Core DbContext + entity configurations
10. Initial migration + seed data
11. Repositories: Prime, Event, Scenario, MetaProfile

### Phase 3: Engine Services
12. EventService: create event, append to log, hash chaining, recipe tracking
13. PrimeService: create prime, addressing, factorization (port from Python)
14. EnergyService: budget allocation, cost deduction, death detection
15. ScanService: bloom filter queries (simplified for v1)
16. TickService: solo turn-based loop, action dispatch, state advancement
17. VdfService: Collatz orbit computation (port core functions from Python)
18. NpcService: behavior tree evaluator, friendly + cautious presets
19. ScenarioService: load scenario definition, evaluate objectives, win/loss

### Phase 4: API + Real-time
20. Dex integration: JWT validation middleware, auth controller
21. SignalR GameHub: implement IGameHubServer, push IGameHubClient events
22. REST controllers: ScenarioController, PrimeController
23. Contracts: all request/response DTOs, hub interfaces
24. NSwag: generate TypeScript client SDK
25. SignalR typed hooks for React

### Phase 5: Game UI
26. GenesisPrompt component + story
27. MapView component + story (canvas or SVG, bloom signals as radial gradients)
28. LogView component + story (monospace event list, decision prompts)
29. PrimeNode + StarNode + AnomalyNode components + stories
30. ScanRadius component + story (animated expanding circle)
31. ObjectiveOverlay component + story
32. DecisionPrompt component + story
33. Wire up SignalR: connect, authenticate, bind to game state
34. Run selection page

### Phase 6: Tutorial Integration
35. First Light scenario definition (starting distribution, objectives, NPCs)
36. Witness narrator NPC (scripted log with 5-8 attestation entries)
37. Objective chain wiring (triggers, completion, sequential reveal)
38. Starting distribution generator (deterministic from seed)
39. End-to-end playtest: play through all 7 objectives
40. Polish pass: animations, transitions, sound design hooks

## Specs Covered

This slice touches these Jira stories:
- ALPHA-10 Event Schema & Log (core)
- ALPHA-11 Prime Addressing (core)
- ALPHA-12 Bloom Filters & Scanning (simplified)
- ALPHA-14 Energy & Conservation (core)
- ALPHA-15 Stellar Compression (ignition only)
- ALPHA-17 Turn Mechanics & Game Loop (solo turn-based only)
- ALPHA-20 Verifiable Delay Function (basic orbit computation)
- ALPHA-22 Tutorial & Scenario System (First Light only)
- ALPHA-23 NPC System (scripted tier only)

Deferred to later slices:
- ALPHA-13 Merkle Trees (slice 2)
- ALPHA-16 Merge & Governance (slice 3 — The Collision)
- ALPHA-18 Em Language Spec (slice 5+)
- ALPHA-19 Infrastructure & Scale (slice 4 — multiplayer)
- ALPHA-21 Roguelite Persistence (slice 2 — needs death states working)
- ALPHA-24 Multiplayer & Sessions (slice 4)
