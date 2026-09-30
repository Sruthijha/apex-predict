"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export interface BarDatum {
  label: string;
  value: number; // 0..1
  sub?: string;
}

/** Single-series horizontal magnitude chart: one hue, direct value labels,
 * recessive gridlines. No legend needed - there's only one series and the
 * title names it. */
export function ProbabilityBarChart({
  data,
  height = 320,
  labelWidth = 90,
}: {
  data: BarDatum[];
  height?: number;
  labelWidth?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.08)" />
        <XAxis
          type="number"
          domain={[0, (max: number) => Math.max(0.1, max * 1.15)]}
          tickFormatter={(v) => `${Math.round(v * 100)}%`}
          tick={{ fill: "#8A8A8A", fontSize: 11 }}
          axisLine={{ stroke: "rgba(255,255,255,0.15)" }}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="label"
          width={labelWidth}
          tick={{ fill: "#F5F3EE", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: "rgba(255,255,255,0.04)" }}
          contentStyle={{
            background: "#181818",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: 2,
            fontSize: 12,
          }}
          formatter={(value) => [`${(Number(value) * 100).toFixed(1)}%`, "Probability"]}
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
          {data.map((d, i) => (
            <Cell key={d.label} fill="#E10600" fillOpacity={i === 0 ? 1 : 0.65} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
