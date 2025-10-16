"use client";
import { useState } from "react";
import { getDraftRecs } from "@/lib/api";

export default function DraftPage() {
  const [leagueKey, setLeagueKey] = useState("");
  const [data, setData] = useState<any>(null);

  const load = async () => {
    const res = await getDraftRecs(leagueKey);
    setData(res);
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-semibold">Draft Assistant</h2>
      <div className="flex gap-2">
        <input className="border rounded px-3 py-2 flex-1" placeholder="league key" value={leagueKey} onChange={e=>setLeagueKey(e.target.value)} />
        <button className="border rounded px-4" onClick={load}>Load</button>
      </div>
      <pre className="bg-black/5 p-4 rounded text-sm overflow-auto">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}