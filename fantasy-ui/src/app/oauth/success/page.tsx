"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api"; // your shared axios instance

export default function OAuthSuccess() {
  const router = useRouter();

  useEffect(() => {
    (async () => {
      try {
        // this will set global.LEAGUE_KEY and return { league_key, name }
        await api.get("/setup");
      } catch (e) {
        // ignore; dashboard can also try to fetch
      } finally {
        router.replace("/"); // go to dashboard
      }
    })();
  }, [router]);

  return (
    <div className="bg-card rounded-xl border p-6 max-w-md mx-auto mt-16 text-center">
      <div className="text-lg font-semibold mb-2">Finishing sign-in…</div>
      <div className="text-sm text-muted-foreground">Loading your league and sending you back.</div>
    </div>
  );
}
