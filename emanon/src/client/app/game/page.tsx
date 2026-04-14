"use client";

import { useState } from "react";
import { GenesisPrompt } from "@/components/game/GenesisPrompt";
import { MapView } from "@/components/game/MapView";
import { ObjectiveOverlay } from "@/components/game/ObjectiveOverlay";

type GamePhase = "genesis" | "playing";

const mockMapData = {
  primes: [
    { id: 47, type: "witness" as const, mass: 2, label: "YOU", x: 0, y: 0, isPlayer: true },
    { id: 23, type: "particle" as const, mass: 4, label: "Unknown", x: -120, y: -40 },
    { id: 11, type: "particle" as const, mass: 3, label: "Cautious", x: 80, y: 100 },
    { id: 2, type: "witness" as const, mass: 8, label: "Ancient Witness", x: -60, y: 140 },
  ],
  stars: [
    { id: "star-1", luminosity: 3, state: "dying" as const, label: "Dim Star", x: 100, y: -80 },
  ],
  anomalies: [
    { id: "anomaly-1", type: "merkle_fragment" as const, label: "Anomaly", x: -150, y: -120 },
  ],
};

export default function GamePage() {
  const [phase, setPhase] = useState<GamePhase>("genesis");
  const [energy, setEnergy] = useState({ current: 100, max: 100 });

  const handleGenesis = (line: string) => {
    setTimeout(() => setPhase("playing"), 1500);
  };

  if (phase === "genesis") {
    return <GenesisPrompt onSubmit={handleGenesis} />;
  }

  return (
    <div className="h-screen relative">
      <ObjectiveOverlay
        current={{ id: "scan", text: "Scan your surroundings.", progress: "0 / 3 scans", completed: false }}
      />
      <MapView
        primes={mockMapData.primes}
        stars={mockMapData.stars}
        anomalies={mockMapData.anomalies}
        energy={energy}
        scanRadius={150}
        playerPosition={{ x: 0, y: 0 }}
      />
    </div>
  );
}
