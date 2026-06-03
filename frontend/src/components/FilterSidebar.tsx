"use client";

import { useState, useEffect } from "react";
import { getMakes, getModels } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ChevronDown, X } from "lucide-react";

export interface Filters {
  make: string;
  model: string;
  year_min: string;
  year_max: string;
  price_min: string;
  price_max: string;
  mileage_max: string;
  condition: string;
  location_state: string;
  sort: string;
}

export const DEFAULT_FILTERS: Filters = {
  make: "",
  model: "",
  year_min: "",
  year_max: "",
  price_min: "",
  price_max: "",
  mileage_max: "",
  condition: "",
  location_state: "",
  sort: "listed_at_desc",
};

interface Props {
  filters: Filters;
  onChange: (filters: Filters) => void;
  totalResults: number;
}

const CONDITIONS = ["new", "used", "cpo"];
const SORT_OPTIONS = [
  { value: "listed_at_desc", label: "Newest first" },
  { value: "score_desc", label: "Best deals first" },
  { value: "price_asc", label: "Price: low to high" },
  { value: "price_desc", label: "Price: high to low" },
];

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
  "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
  "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
  "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
];

export function FilterSidebar({ filters, onChange, totalResults }: Props) {
  const [makes, setMakes] = useState<string[]>([]);
  const [models, setModels] = useState<string[]>([]);

  useEffect(() => {
    getMakes().then((data) => setMakes(data.map((m) => m.make)));
  }, []);

  useEffect(() => {
    if (filters.make) {
      getModels(filters.make).then((data) =>
        setModels(data.map((m) => m.model))
      );
    } else {
      setModels([]);
    }
  }, [filters.make]);

  const set = (key: keyof Filters, value: string) => {
    const next = { ...filters, [key]: value };
    if (key === "make") next.model = "";
    onChange(next);
  };

  const hasActiveFilters = Object.entries(filters).some(
    ([k, v]) => k !== "sort" && v !== ""
  );

  const reset = () => onChange(DEFAULT_FILTERS);

  return (
    <aside className="w-64 shrink-0">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 sticky top-24">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-semibold text-white">Filters</h2>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">{totalResults} results</span>
            {hasActiveFilters && (
              <button
                onClick={reset}
                className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-0.5"
              >
                <X className="w-3 h-3" /> Clear
              </button>
            )}
          </div>
        </div>

        <div className="space-y-5">
          {/* Sort */}
          <FilterSection label="Sort by">
            <Select
              value={filters.sort}
              onChange={(v) => set("sort", v)}
              options={SORT_OPTIONS}
            />
          </FilterSection>

          {/* Make */}
          <FilterSection label="Make">
            <Select
              value={filters.make}
              onChange={(v) => set("make", v)}
              options={[
                { value: "", label: "All makes" },
                ...makes.map((m) => ({ value: m, label: m })),
              ]}
            />
          </FilterSection>

          {/* Model */}
          {models.length > 0 && (
            <FilterSection label="Model">
              <Select
                value={filters.model}
                onChange={(v) => set("model", v)}
                options={[
                  { value: "", label: "All models" },
                  ...models.map((m) => ({ value: m, label: m })),
                ]}
              />
            </FilterSection>
          )}

          {/* Condition */}
          <FilterSection label="Condition">
            <div className="flex gap-2 flex-wrap">
              {CONDITIONS.map((c) => (
                <button
                  key={c}
                  onClick={() => set("condition", filters.condition === c ? "" : c)}
                  className={cn(
                    "px-3 py-1 rounded-lg text-xs font-medium border transition-colors",
                    filters.condition === c
                      ? "bg-amber-400/10 border-amber-400/40 text-amber-400"
                      : "border-gray-700 text-gray-400 hover:border-gray-600"
                  )}
                >
                  {c === "cpo" ? "CPO" : c.charAt(0).toUpperCase() + c.slice(1)}
                </button>
              ))}
            </div>
          </FilterSection>

          {/* Year */}
          <FilterSection label="Year">
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="From"
                value={filters.year_min}
                onChange={(e) => set("year_min", e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-400/50"
                min={1990}
                max={2030}
              />
              <input
                type="number"
                placeholder="To"
                value={filters.year_max}
                onChange={(e) => set("year_max", e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-400/50"
                min={1990}
                max={2030}
              />
            </div>
          </FilterSection>

          {/* Price */}
          <FilterSection label="Price (USD)">
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="Min"
                value={filters.price_min}
                onChange={(e) => set("price_min", e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-400/50"
              />
              <input
                type="number"
                placeholder="Max"
                value={filters.price_max}
                onChange={(e) => set("price_max", e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-400/50"
              />
            </div>
          </FilterSection>

          {/* Mileage */}
          <FilterSection label="Max Mileage">
            <input
              type="number"
              placeholder="e.g. 50000"
              value={filters.mileage_max}
              onChange={(e) => set("mileage_max", e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-400/50"
            />
          </FilterSection>

          {/* State */}
          <FilterSection label="State">
            <Select
              value={filters.location_state}
              onChange={(v) => set("location_state", v)}
              options={[
                { value: "", label: "All states" },
                ...US_STATES.map((s) => ({ value: s, label: s })),
              ]}
            />
          </FilterSection>
        </div>
      </div>
    </aside>
  );
}

function FilterSection({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wider">
        {label}
      </label>
      {children}
    </div>
  );
}

function Select({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full appearance-none bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-400/50 pr-8"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
    </div>
  );
}