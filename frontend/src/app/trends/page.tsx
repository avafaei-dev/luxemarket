"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { TrendingUp, BarChart2, DollarSign } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
  PieChart, Pie,
} from "recharts";
import { getTrends, getTrendsSummary } from "@/lib/api";
import { StatCard } from "@/components/StatCard";
import { formatPrice, formatNumber } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { MarketSnapshot } from "@/lib/api";

const MAKE_COLORS: Record<string, string> = {
  BMW: "#3b82f6",
  "Mercedes-Benz": "#8b5cf6",
  Porsche: "#f59e0b",
  Audi: "#10b981",
  Ferrari: "#ef4444",
  Lamborghini: "#f97316",
  Bentley: "#6366f1",
  "Rolls-Royce": "#ec4899",
  McLaren: "#14b8a6",
  "Aston Martin": "#84cc16",
  Maserati: "#06b6d4",
  Lexus: "#a855f7",
};

const DEFAULT_COLOR = "#6b7280";

const MAKES = [
  "BMW", "Mercedes-Benz", "Porsche", "Audi", "Ferrari",
  "Lamborghini", "Bentley", "Rolls-Royce", "McLaren",
  "Aston Martin", "Maserati", "Lexus",
];

interface TooltipPayloadItem {
    name: string;
    value: number;
    color?: string;
    fill?: string;
  }
  
  interface CustomTooltipProps {
    active?: boolean;
    payload?: TooltipPayloadItem[];
    label?: string;
  }
  
  function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-white border border-surface-border rounded-xl p-3 text-sm shadow-card-hover">
        <p className="font-medium text-ink mb-1">{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ color: p.color ?? p.fill }}>
            {p.name}:{" "}
            {p.name.toLowerCase().includes("price")
              ? formatPrice(p.value)
              : p.name.toLowerCase().includes("score")
              ? p.value?.toFixed(1)
              : formatNumber(p.value)}
          </p>
        ))}
      </div>
    );
  }

export default function TrendsPage() {
  const [selectedMake, setSelectedMake] = useState<string>("");

  const { data: summary } = useQuery({
    queryKey: ["trends-summary"],
    queryFn: getTrendsSummary,
  });

  const { data: trends } = useQuery({
    queryKey: ["trends", selectedMake],
    queryFn: () => getTrends(selectedMake || undefined),
    select: (d) => d.data,
  });

  // Aggregate by make for the overview charts
  const byMake = MAKES.map((make) => {
    const makeSnapshots: MarketSnapshot[] = trends?.filter((t: MarketSnapshot) => t.make === make) ?? [];
if (makeSnapshots.length === 0) return null;
const avgPrice =
  makeSnapshots.reduce((s: number, t: MarketSnapshot) => s + t.avg_price, 0) / makeSnapshots.length;
const avgScore =
  makeSnapshots.reduce((s: number, t: MarketSnapshot) => s + (t.avg_deal_score ?? 0), 0) /
  makeSnapshots.length;
const totalListings = makeSnapshots.reduce((s: number, t: MarketSnapshot) => s + t.listing_count, 0);
    return { make, avgPrice, avgScore, totalListings };
  }).filter(Boolean) as { make: string; avgPrice: number; avgScore: number; totalListings: number }[];

  // Model-level data for selected make
  const modelData = selectedMake && trends
    ? trends
        .filter((t: { make: string; }) => t.make === selectedMake)
        .sort((a: { avg_price: number; }, b: { avg_price: number; }) => b.avg_price - a.avg_price)
    : [];



  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-400/10 rounded-lg">
          <TrendingUp className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Market Trends</h1>
          <p className="text-sm text-gray-500">
            Aggregated market data across {summary?.total_listings?.toLocaleString() ?? "—"} listings
          </p>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard
          label="Avg Market Price"
          value={summary ? formatPrice(summary.avg_price) : "—"}
          icon={DollarSign}
          accent="blue"
        />
        <StatCard
          label="Avg Deal Score"
          value={summary ? summary.avg_deal_score.toFixed(1) : "—"}
          icon={BarChart2}
          accent="emerald"
        />
        <StatCard
          label="Most Listed Make"
          value={summary?.top_make ?? "—"}
          icon={TrendingUp}
          accent="amber"
        />
      </div>

      {/* Make filter */}
      <div>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
          Filter by make
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedMake("")}
            className={cn(
              "px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors",
              selectedMake === ""
                ? "bg-gray-700 border-gray-600 text-white"
                : "border-gray-800 text-gray-500 hover:border-gray-700 hover:text-white"
            )}
          >
            All Makes
          </button>
          {MAKES.map((m) => (
            <button
              key={m}
              onClick={() => setSelectedMake(m === selectedMake ? "" : m)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors",
                selectedMake === m
                  ? "border-gray-600 text-white"
                  : "border-gray-800 text-gray-500 hover:border-gray-700 hover:text-white"
              )}
              style={
                selectedMake === m
                  ? { backgroundColor: `${MAKE_COLORS[m]}20`, borderColor: `${MAKE_COLORS[m]}60`, color: MAKE_COLORS[m] }
                  : {}
              }
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Chart 1 — Avg price by make */}
      {!selectedMake && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="font-semibold text-white mb-6">Average Price by Make</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byMake} margin={{ top: 0, right: 0, bottom: 60, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="make"
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                angle={-40}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avgPrice" name="Avg Price" radius={[4, 4, 0, 0]}>
                {byMake.map((entry) => (
                  <Cell
                    key={entry.make}
                    fill={MAKE_COLORS[entry.make] ?? DEFAULT_COLOR}
                    fillOpacity={0.8}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Chart 2 — Deal score by make */}
      {!selectedMake && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="font-semibold text-white mb-6">Average Deal Score by Make</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byMake} margin={{ top: 0, right: 0, bottom: 60, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="make"
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                angle={-40}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avgScore" name="Avg Score" radius={[4, 4, 0, 0]}>
                {byMake.map((entry) => (
                  <Cell
                    key={entry.make}
                    fill={
                      entry.avgScore >= 70
                        ? "#10b981"
                        : entry.avgScore >= 40
                        ? "#f59e0b"
                        : "#ef4444"
                    }
                    fillOpacity={0.8}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Chart 3 — Listing count (pie) */}
      {!selectedMake && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="font-semibold text-white mb-6">Listings by Make</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={byMake}
                dataKey="totalListings"
                nameKey="make"
                cx="50%"
                cy="50%"
                outerRadius={110}
                label={({ name, percent }: { name?: string; percent?: number }) =>
                    (percent ?? 0) > 0.05 ? `${name ?? ""} ${((percent ?? 0) * 100).toFixed(0)}%` : ""
                }
                labelLine={false}
              >
                {byMake.map((entry) => (
                  <Cell
                    key={entry.make}
                    fill={MAKE_COLORS[entry.make] ?? DEFAULT_COLOR}
                    fillOpacity={0.85}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Model detail for selected make */}
      {selectedMake && modelData.length > 0 && (
        <>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="font-semibold text-white mb-6">
              {selectedMake} — Avg Price by Model
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={modelData}
                layout="vertical"
                margin={{ top: 0, right: 40, bottom: 0, left: 140 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis
                  type="number"
                  tick={{ fill: "#9ca3af", fontSize: 11 }}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                />
                <YAxis
                  type="category"
                  dataKey="model"
                  tick={{ fill: "#9ca3af", fontSize: 11 }}
                  width={135}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="avg_price"
                  name="Avg Price"
                  fill={MAKE_COLORS[selectedMake] ?? DEFAULT_COLOR}
                  fillOpacity={0.8}
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Model deal scores */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="font-semibold text-white mb-4">
              {selectedMake} — Model Summary
            </h2>
            <div className="divide-y divide-gray-800">
              {modelData.map((row: MarketSnapshot) => (
                <div key={row.model} className="flex items-center justify-between py-3">
                  <span className="text-sm font-medium text-white">{row.model}</span>
                  <div className="flex items-center gap-6 text-sm text-gray-400">
                    <span>{row.listing_count} listings</span>
                    <span>{formatPrice(row.avg_price)} avg</span>
                    <span
                      className={cn(
                        "font-medium",
                        row.avg_deal_score >= 70
                          ? "text-emerald-400"
                          : row.avg_deal_score >= 40
                          ? "text-amber-400"
                          : "text-red-400"
                      )}
                    >
                      Score {row.avg_deal_score?.toFixed(1)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}