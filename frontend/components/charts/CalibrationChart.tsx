"use client";

import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CalibrationPoint } from "@/lib/types";

export function CalibrationChart({ points }: { points: CalibrationPoint[] }) {
  const data = points.map((p) => ({
    predicted: p.predicted_mean,
    observed: p.observed_rate,
    reference: p.predicted_mean,
    label: `${Math.round(p.bin_start * 100)}-${Math.round(p.bin_end * 100)}%`,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ left: 4, right: 16, top: 8, bottom: 4 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.08)" />
        <XAxis
          dataKey="predicted"
          type="number"
          domain={[0, 1]}
          tickFormatter={(v) => `${Math.round(v * 100)}%`}
          tick={{ fill: "#8A8A8A", fontSize: 11 }}
          axisLine={{ stroke: "rgba(255,255,255,0.15)" }}
          tickLine={false}
          label={{ value: "Predicted probability", position: "insideBottom", offset: -2, fill: "#8A8A8A", fontSize: 11 }}
        />
        <YAxis
          domain={[0, 1]}
          tickFormatter={(v) => `${Math.round(v * 100)}%`}
          tick={{ fill: "#8A8A8A", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={40}
          label={{ value: "Observed rate", angle: -90, position: "insideLeft", fill: "#8A8A8A", fontSize: 11 }}
        />
        <Tooltip
          contentStyle={{ background: "#181818", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 2, fontSize: 12 }}
          formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line type="linear" dataKey="reference" name="Perfect calibration" stroke="#8A8A8A" strokeDasharray="4 4" dot={false} />
        <Line type="monotone" dataKey="observed" name="Model" stroke="#E10600" strokeWidth={2} dot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
