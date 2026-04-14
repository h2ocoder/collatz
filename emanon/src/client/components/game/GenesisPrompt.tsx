"use client";

import { useState, KeyboardEvent } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

interface GenesisPromptProps {
  onSubmit: (genesisLine: string) => void;
}

export function GenesisPrompt({ onSubmit }: GenesisPromptProps) {
  const [value, setValue] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (value.trim() && !submitted) {
      setSubmitted(true);
      onSubmit(value.trim());
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="min-h-screen bg-void flex flex-col items-center justify-center px-8">
      <h1 className="font-ui text-text-primary text-5xl tracking-[0.3em] font-extralight mb-16 opacity-60">
        EMANON
      </h1>

      {!submitted ? (
        <div className="text-center max-w-md w-full">
          <p className="font-data text-text-muted text-sm mb-8 tracking-wide">
            Hello world. I am
          </p>
          <Input
            variant="genesis"
            placeholder="_______"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
          <div className="mt-8">
            <Button
              variant="primary"
              onClick={handleSubmit}
              disabled={!value.trim()}
            >
              Declare
            </Button>
          </div>
          <p className="font-ui text-text-muted/50 text-xs mt-6">
            What you type determines your prime type
          </p>
        </div>
      ) : (
        <div className="text-center">
          <p className="font-narrative text-text-secondary text-xl italic">
            Hello world. I am {value}.
          </p>
          <p className="font-data text-text-muted text-xs mt-4">
            Genesis event emitted. Tick 0.
          </p>
        </div>
      )}
    </div>
  );
}
