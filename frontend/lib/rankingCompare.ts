/** Compares two finishing-order guesses (arrays of driver_id, P1 first). */

export interface RankingComparison {
  exactMatches: number;
  top3Overlap: number;
  meanAbsolutePositionDiff: number;
}

export function compareOrders(a: string[], b: string[]): RankingComparison {
  const rankOfB = new Map(b.map((id, i) => [id, i]));
  let exactMatches = 0;
  let totalDiff = 0;
  let counted = 0;

  a.forEach((driverId, i) => {
    const j = rankOfB.get(driverId);
    if (j === undefined) return;
    if (i === j) exactMatches += 1;
    totalDiff += Math.abs(i - j);
    counted += 1;
  });

  const top3A = new Set(a.slice(0, 3));
  const top3B = new Set(b.slice(0, 3));
  const top3Overlap = [...top3A].filter((id) => top3B.has(id)).length;

  return {
    exactMatches,
    top3Overlap,
    meanAbsolutePositionDiff: counted > 0 ? totalDiff / counted : 0,
  };
}
