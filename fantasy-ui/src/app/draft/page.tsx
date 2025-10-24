"use client";

import { useEffect, useMemo, useState } from "react";
import { getDraftRecommend } from "@/lib/api";
import { PuntToggles } from "@/components/PuntToggles";

export default function DraftPage() {
  const [season, setSeason] = useState("2024");
  const [limit, setLimit] = useState(150);
  const [punt, setPunt] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Awaited<ReturnType<typeof getDraftRecommend>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load(curr: { season: string; limit: number; punt: string[] }) {
    setLoading(true);
    setError(null);
    try {
      const res = await getDraftRecommend(curr);
      setData({
        league_key: res.league_key ?? "",
        season: res.season ?? curr.season,
        punt: Array.isArray(res.punt) ? res.punt : [],
        count: Number.isFinite(res.count) ? res.count : 0,
        top: Array.isArray(res.top) ? res.top : [],
      });
    } catch (e: any) {
      setError(e?.message || "Failed to load");
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  // Auto-load whenever controls change
  useEffect(() => {
    load({ season, limit, punt });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [season, limit, punt]);

  const shown = data?.top?.length ?? 0;
  const total = data?.count ?? 0;
  const puntLabel = useMemo(
    () => (punt.length ? `Punting: ${punt.join(", ")}` : "No punts"),
    [punt]
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Draft Recommendations</h1>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="rounded-xl border p-4 bg-card space-y-3">
          <div className="text-sm font-medium">Season</div>
          <select
            className="w-full border rounded-md p-2 bg-background text-foreground"
            value={season}
            onChange={(e) => setSeason(e.target.value)}
          >
            <option value="2024">2024 (last season)</option>
            <option value="2025">2025 (this season)</option>
          </select>

          <div className="text-sm font-medium mt-2">Limit</div>
          <input
            type="number"
            className="w-full border rounded-md p-2 bg-background text-foreground"
            value={limit}
            min={25}
            max={300}
            onChange={(e) => setLimit(Number(e.target.value))}
          />

          <div className="mt-4">
            <div className="text-sm font-medium mb-2">Punt categories</div>
            <PuntToggles value={punt} onChange={setPunt} />
          </div>

          <div className="text-xs text-muted-foreground mt-2">
            {puntLabel}
          </div>
        </div>

        <div className="md:col-span-2 rounded-xl border bg-card">
          <div className="p-4 border-b flex items-center justify-between">
            <div className="font-semibold">Top Recommendations</div>
            <div className="text-sm text-muted-foreground">
              {loading ? "Loading…" : data ? `${shown} shown of ${total}` : "—"}
            </div>
          </div>

          <div className="divide-y">
            {error && <div className="p-4 text-red-600">{error}</div>}

            {!error && loading && <div className="p-4">Loading…</div>}

            {!error && !loading && (!data || shown === 0) && (
              <div className="p-4">
                No results yet. Try:
                <ul className="list-disc ml-5 mt-2">
                  <li>Season = 2024 (preseason baseline)</li>
                  <li>Increase Limit (e.g., 200)</li>
                  <li>Clear all punts</li>
                </ul>
              </div>
            )}

            {!error &&
              !loading &&
              data &&
              shown > 0 &&
              data.top.map((r: { player: { id: any; name: any; team: any; pos: any; }; cats: { fg_pct: number | undefined; ft_pct: number | undefined; tpm_pg: number | undefined; pts_pg: number | undefined; reb_pg: number | undefined; ast_pg: number | undefined; stl_pg: number | undefined; blk_pg: number | undefined; tov_pg: number | undefined; }; score: unknown; }, idx: number) => (
                <div key={`${r?.player?.id ?? "p"}-${idx}`} className="p-4 flex items-start gap-4">
                  <div className="w-8 text-right tabular-nums text-muted-foreground">{idx + 1}.</div>
                  <div className="flex-1">
                    <div className="font-semibold">{r?.player?.name ?? "Unknown Player"}</div>
                    <div className="text-sm text-muted-foreground">
                      {(r?.player?.team ?? "—")} · {(r?.player?.pos ?? []).join("/")}
                    </div>
                  </div>
                  <div className="grid grid-cols-5 gap-2 text-sm">
                    <Stat label="FG%" value={r?.cats?.fg_pct} fmt="pct" />
                    <Stat label="FT%" value={r?.cats?.ft_pct} fmt="pct" />
                    <Stat label="3PM" value={r?.cats?.tpm_pg} />
                    <Stat label="PTS" value={r?.cats?.pts_pg} />
                    <Stat label="REB" value={r?.cats?.reb_pg} />
                    <Stat label="AST" value={r?.cats?.ast_pg} />
                    <Stat label="STL" value={r?.cats?.stl_pg} />
                    <Stat label="BLK" value={r?.cats?.blk_pg} />
                    <Stat label="TOV" value={r?.cats?.tov_pg} />
                    <div className="text-right font-semibold">
                      Score: {isNum(r?.score) ? r!.score.toFixed(2) : "—"}
                    </div>
                    <div className="text-right text-xs text-subtext">
                      {Number.isFinite((r as any).pos_bonus) ? `Pos bonus: +${(r as any).pos_bonus.toFixed(2)}` : null}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, fmt }: { label: string; value: number | undefined; fmt?: "pct" }) {
  const v =
    fmt === "pct"
      ? isNum(value) ? (value as number).toFixed(3) : "-"
      : isNum(value) ? (value as number).toFixed(1) : "-";
  return (
    <div className="text-right">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-mono tabular-nums">{v}</div>
    </div>
  );
}

function isNum(x: unknown): x is number {
  return typeof x === "number" && Number.isFinite(x);
}
