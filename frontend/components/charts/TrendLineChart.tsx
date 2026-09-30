"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export interface TrendPoint {
  label: string;
  value: number;
}

/** Single-series time trend. Y axis inverted when `invert` is set (useful for
 * finishing position, where lower = better and "up" should read as improving). */
export function TrendLineChart({ data, invert = false, height = 260 }: { data: TrendPoint[]; invert?: boolean; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ left: 4, right: 16, top: 8, bottom: 4 }}>
        <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.08)" />
        <XAxis dataKey="label" tick={{ fill: "#8A8A8A", fontSize: 11 }} axisLine={{ stroke: "rgba(255,255,255,0.15)" }} tickLine={false} />
        <YAxis
          reversed={invert}
          tick={{ fill: "#8A8A8A", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={28}
          allowDecimals={false}
        />
        <Tooltip
          cursor={{ stroke: "rgba(255,255,255,0.2)" }}
          contentStyle={{ background: "#181818", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 2, fontSize: 12 }}
        />
        <Line type="monotone" dataKey="value" stroke="#E10600" strokeWidth={2} dot={{ r: 3, fill: "#E10600" }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
