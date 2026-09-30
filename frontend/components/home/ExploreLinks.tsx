import Link from "next/link";

export function ExploreLinks() {
  return (
    <section className="border-t border-white/10 bg-apex-dark-2">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-16 sm:grid-cols-3 sm:px-6 lg:px-8">
        <ExploreCard href="/drivers" title="Explore Drivers" body="Form, reliability, and circuit history for every driver on the grid." />
        <ExploreCard href="/circuits" title="Explore Circuits" body="Historical winners, DNF rates, and track character for every venue." />
        <ExploreCard href="/compare" title="Head to Head" body="Put two drivers side by side across form, pace, and reliability." />
      </div>
    </section>
  );
}

function ExploreCard({ href, title, body }: { href: string; title: string; body: string }) {
  return (
    <Link
      href={href}
      className="group block rounded-sm border border-white/10 bg-apex-dark p-6 transition-colors hover:border-apex-red/50"
    >
      <h3 className="font-display text-xl font-semibold uppercase group-hover:text-apex-red">{title}</h3>
      <p className="mt-2 text-sm text-apex-off-white/70">{body}</p>
    </Link>
  );
}
