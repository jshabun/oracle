"use client";
import { useState, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

const CATS: { key: string; label: string }[] = [
  { key: "fg_pct", label: "FG%" },
  { key: "ft_pct", label: "FT%" },
  { key: "tpm_pg", label: "3PM" },
  { key: "pts_pg", label: "PTS" },
  { key: "reb_pg", label: "REB" },
  { key: "ast_pg", label: "AST" },
  { key: "stl_pg", label: "STL" },
  { key: "blk_pg", label: "BLK" },
  { key: "tov_pg", label: "TOV" },
];

export function PuntToggles({ value, onChange }: { value: string[]; onChange: (v: string[]) => void; }) {
  const [local, setLocal] = useState<string[]>(value);
  useEffect(() => setLocal(value), [value]);

  function toggle(k: string) {
    const next = local.includes(k) ? local.filter(x => x !== k) : [...local, k];
    setLocal(next);
    onChange(next);
  }

  return (
    <div className="grid grid-cols-3 gap-3">
      {CATS.map((c) => (
        <label key={c.key} className="flex items-center gap-2">
          <Switch checked={local.includes(c.key)} onCheckedChange={() => toggle(c.key)} />
          <Label>{c.label}</Label>
        </label>
      ))}
    </div>
  );
}