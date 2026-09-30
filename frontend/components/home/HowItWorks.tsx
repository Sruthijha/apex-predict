const STEPS = [
  {
    title: "Ingest",
    body: "Full historical results, qualifying, and standings pulled from the Jolpica-F1 API and cached locally.",
  },
  {
    title: "Engineer",
    body: "Rolling driver/constructor form, circuit history, and grid position - every stat strictly shifted to exclude the race being predicted.",
  },
  {
    title: "Train",
    body: "Linear, Random Forest, and XGBoost models compared on a chronological 2015-2022/2023/2024 train/validation/test split - never a random split.",
  },
  {
    title: "Simulate",
    body: "10,000-race Monte Carlo simulation turns each driver's predicted position and DNF risk into win, podium, and points probabilities.",
  },
];

export function HowItWorks() {
  return (
    <section className="border-y border-white/10 bg-apex-dark-2">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Under the Hood</p>
        <h2 className="mb-10 font-display text-3xl font-bold uppercase">How the Model Works</h2>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <div key={step.title} className="relative border-l-2 border-apex-red/50 pl-5">
              <span className="font-display text-4xl font-bold text-white/10">{String(i + 1).padStart(2, "0")}</span>
              <h3 className="mt-1 font-display text-lg font-semibold uppercase">{step.title}</h3>
              <p className="mt-1 text-sm text-apex-off-white/70">{step.body}</p>
            </div>
          ))}
        </div>
        <a href="/model" className="mt-8 inline-block text-sm font-semibold text-apex-red hover:underline">
          See full methodology and honest evaluation results →
        </a>
      </div>
    </section>
  );
}
