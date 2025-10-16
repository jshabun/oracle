import ConnectYahoo from "@/components/ConnectYahoo";
import Nav from "@/components/Nav";

export default function Home() {
  return (
    <main className="max-w-5xl mx-auto p-6 space-y-6">
      <Nav />
      <section className="grid gap-4">
        <h1 className="text-3xl font-bold">Fantasy NBA Assistant</h1>
        <p className="text-muted-foreground">Draft smarter. Stream better. Win more.</p>
        <ConnectYahoo />
      </section>
    </main>
  );
}