export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-apex-dark-2">
      <div className="mx-auto max-w-7xl px-4 py-8 text-sm text-apex-gray sm:px-6 lg:px-8">
        <p className="font-display tracking-wide text-apex-off-white">
          APEX <span className="text-apex-red">PREDICT</span>
        </p>
        <p className="mt-2 max-w-2xl">
          An independent motorsport analytics project. Not affiliated with, endorsed by, or
          sponsored by Formula 1, the FIA, or any competing team. Predictions are probabilistic
          model outputs for demonstration purposes, not betting advice or official forecasts.
        </p>
        <p className="mt-2">
          Historical data sourced from the Jolpica-F1 API (Ergast-compatible). Built with FastAPI,
          scikit-learn, XGBoost, and Next.js.
        </p>
      </div>
    </footer>
  );
}
