"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function OAuthError() {
  const params = useSearchParams();
  const router = useRouter();
  const reason = params.get("reason") || "unknown";

  useEffect(() => {
    const t = setTimeout(() => router.replace("/"), 2500);
    return () => clearTimeout(t);
  }, [router]);

  return (
    <div className="bg-card rounded-xl border p-6 max-w-md mx-auto mt-16 text-center">
      <div className="text-lg font-semibold mb-2">Sign-in error</div>
      <div className="text-sm text-muted-foreground">Reason: {reason}</div>
      <div className="text-xs text-muted-foreground mt-3">Returning to dashboard…</div>
    </div>
  );
}
