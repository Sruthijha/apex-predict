"use client";

import { useEffect, useState } from "react";
import clsx from "clsx";

/** Five-light F1-style start sequence. Lights up left-to-right, holds, then
 * "goes out" all at once (calling onLightsOut), just like a real start. */
export function StartingLights({
  running,
  onLightsOut,
}: {
  running: boolean;
  onLightsOut?: () => void;
}) {
  const [litCount, setLitCount] = useState(0);

  useEffect(() => {
    if (!running) return;
    let cancelled = false;
    const sequence = async () => {
      for (let i = 1; i <= 5; i++) {
        await new Promise((r) => setTimeout(r, 350));
        if (cancelled) return;
        setLitCount(i);
      }
      await new Promise((r) => setTimeout(r, 600));
      if (cancelled) return;
      setLitCount(0);
      onLightsOut?.();
    };
    sequence();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  const displayCount = running ? litCount : 0;

  return (
    <div className="flex items-center justify-center gap-3" role="img" aria-label="Starting lights">
      {[1, 2, 3, 4, 5].map((i) => (
        <span
          key={i}
          className={clsx(
            "h-6 w-6 rounded-full border-2 border-apex-red/60 transition-colors duration-150 sm:h-8 sm:w-8",
            i <= displayCount ? "bg-apex-red shadow-[0_0_16px_2px_rgba(225,6,0,0.7)]" : "bg-apex-dark-2",
          )}
        />
      ))}
    </div>
  );
}
