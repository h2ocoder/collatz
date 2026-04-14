import { Badge } from "@/components/ui/Badge";

type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";

interface LogEvent {
  tick: number;
  type: "genesis" | "emit" | "observe" | "scan" | "share" | "merge";
  content: string;
}

interface LogViewProps {
  primeName: string;
  primeId: number;
  primeType: PrimeType;
  events: LogEvent[];
  className?: string;
}

const eventTypeColors: Record<LogEvent["type"], string> = {
  genesis: "text-trust",
  emit: "text-text-primary",
  observe: "text-accent-blue",
  scan: "text-accent-blue/60",
  share: "text-star",
  merge: "text-accent-violet",
};

export function LogView({ primeName, primeId, primeType, events, className = "" }: LogViewProps) {
  return (
    <div className={`bg-deep border border-border rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
        <div className="flex items-center gap-3">
          <span className="font-ui text-sm text-text-primary">{primeName}</span>
          <Badge type={primeType} />
        </div>
        <span className="font-data text-xs text-text-muted">prime {primeId}</span>
      </div>

      {/* Events */}
      <div className="px-4 py-3 font-data text-xs leading-[1.8] max-h-80 overflow-y-auto">
        {events.map((event, i) => (
          <div key={i}>
            <span className="text-text-muted">tick {event.tick}: </span>
            <span className={eventTypeColors[event.type]}>{event.content}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
