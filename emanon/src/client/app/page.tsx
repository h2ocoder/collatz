import { Button } from "@/components/ui/Button";

interface ScenarioCard {
  id: string;
  name: string;
  description: string;
  tag: string;
  color: string;
  borderColor: string;
  objectives: number;
  available: boolean;
}

const scenarios: ScenarioCard[] = [
  {
    id: "tutorial",
    name: "Tutorial: First Light",
    description: "Learn the basics. Declare, scan, observe, share, ignite a star.",
    tag: "tutorial",
    color: "text-accent-blue",
    borderColor: "border-accent-blue",
    objectives: 7,
    available: true,
  },
  {
    id: "frontier",
    name: "The Frontier",
    description: "A fertile region with scattered primes and a dying star. Explore, merge, survive.",
    tag: "territory + exploration",
    color: "text-star",
    borderColor: "border-star",
    objectives: 4,
    available: false,
  },
  {
    id: "collision",
    name: "The Collision",
    description: "Two composites sharing prime factors. Contested streams. Resolve or dominate.",
    tag: "conflict",
    color: "text-danger",
    borderColor: "border-danger",
    objectives: 2,
    available: false,
  },
  {
    id: "witness",
    name: "The Witness",
    description: "Two factions merging. Your attestation determines trust. Choose carefully.",
    tag: "specialist",
    color: "text-trust",
    borderColor: "border-trust",
    objectives: 3,
    available: false,
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-void flex flex-col items-center px-8 py-16">
      <h1 className="font-ui text-text-primary text-4xl tracking-[0.25em] font-extralight mb-4">
        EMANON
      </h1>
      <p className="font-narrative text-text-secondary text-sm italic mb-16">
        The name that means &ldquo;this points at something none of us can name.&rdquo;
      </p>

      <div className="w-full max-w-lg flex flex-col gap-3">
        {scenarios.map((s) => (
          <div
            key={s.id}
            className={`
              border rounded-lg p-4
              ${s.available ? s.borderColor : "border-border opacity-50"}
              ${s.available ? "bg-surface" : "bg-deep"}
            `}
          >
            <div className="flex justify-between items-center">
              <div>
                <div className={`font-ui text-sm font-normal ${s.available ? s.color : "text-text-muted"}`}>
                  {s.name}
                </div>
                <div className="font-ui text-xs text-text-muted mt-1">
                  {s.description}
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className={`font-data text-[10px] ${s.color} border ${s.borderColor}/30 px-2 py-0.5 rounded-sm`}>
                  {s.tag}
                </span>
                {s.available && (
                  <span className="font-data text-[10px] text-text-muted">
                    {s.objectives} objectives
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Cold Drop */}
        <div className="border border-border rounded-lg p-4 bg-deep mt-2">
          <div className="flex justify-between items-center">
            <div>
              <div className="font-ui text-sm text-text-primary">Cold Drop</div>
              <div className="font-ui text-xs text-text-muted mt-1">
                No objectives. No guidance. Just you and the multiverse.
              </div>
            </div>
            <span className="font-data text-[10px] text-text-muted border border-border px-2 py-0.5 rounded-sm">
              freeplay
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
