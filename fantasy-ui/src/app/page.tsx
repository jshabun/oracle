import { getSetup } from "@/lib/api";


export default async function Page() {
  let setup: Awaited<ReturnType<typeof getSetup>> | null = null;
  try { setup = await getSetup(); } catch { /* backend may require auth first */ }


  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      {!setup ? (
        <div className="rounded-xl border p-4 bg-card">
          <p className="mb-2">Connect your Yahoo account to load league details.</p>
          <a href={`${process.env.NEXT_PUBLIC_API_BASE}/auth/start`} className="inline-block rounded-md bg-primary text-primary-foreground px-4 py-2">Connect Yahoo</a>
        </div>
      ) : (
        <div className="rounded-xl border p-4 bg-card">
          <div className="text-sm text-muted-foreground">League Key</div>
          <div className="font-mono text-lg">{setup.league_key}</div>
          <div className="mt-2 text-xl font-semibold">{setup.name}</div>
          <div className="mt-4">
            <a href="/draft" className="inline-block rounded-md bg-primary text-primary-foreground px-4 py-2">Go to Draft Board</a>
          </div>
        </div>
      )}
    </div>
  );
}