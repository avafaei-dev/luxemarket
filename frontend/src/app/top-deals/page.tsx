"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Star, Filter } from "lucide-react";
import { Listing, searchListings } from "@/lib/api";
import { ListingCard } from "@/components/ListingCard";
import { ListingCardSkeleton } from "@/components/ListingCardSkeleton";
import { EmptyState } from "@/components/EmptyState";
import { Pagination } from "@/components/Pagination";
import { cn } from "@/lib/utils";

const SCORE_THRESHOLDS = [
  { label: "All deals", value: 60 },
  { label: "Good (60+)", value: 60 },
  { label: "Great (70+)", value: 70 },
  { label: "Excellent (80+)", value: 80 },
];

const MAKES = [
  "All", "BMW", "Mercedes-Benz", "Porsche", "Audi", "Ferrari",
  "Lamborghini", "Bentley", "Rolls-Royce", "McLaren", "Aston Martin",
  "Maserati", "Lexus",
];

export default function TopDealsPage() {
  const [minScore, setMinScore] = useState(60);
  const [make, setMake] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["top-deals", minScore, make, page],
    queryFn: () =>
      searchListings({
        make: make ? [make] : undefined,
        min_deal_score: minScore,
        sort: "score_desc",
        page,
        limit: 18,
      }),
    placeholderData: (prev) => prev,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-amber-400/10 rounded-lg">
          <Star className="w-5 h-5 text-amber-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Top Deals</h1>
          <p className="text-sm text-gray-500">
            {data?.total ?? "—"} listings priced below market value
          </p>
        </div>
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Filter className="w-4 h-4" />
          Score:
        </div>
        {SCORE_THRESHOLDS.map((t) => (
          <button
            key={t.value + t.label}
            onClick={() => { setMinScore(t.value); setPage(1); }}
            className={cn(
              "px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors",
              minScore === t.value && t.label !== "All deals"
                ? "bg-amber-400/10 border-amber-400/40 text-amber-400"
                : t.label === "All deals" && minScore === 60
                ? "bg-amber-400/10 border-amber-400/40 text-amber-400"
                : "border-gray-700 text-gray-400 hover:border-gray-600 hover:text-white"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Make filter */}
      <div className="flex flex-wrap gap-2">
        {MAKES.map((m) => (
          <button
            key={m}
            onClick={() => { setMake(m === "All" ? "" : m); setPage(1); }}
            className={cn(
              "px-3 py-1 rounded-lg text-xs font-medium border transition-colors",
              (m === "All" && make === "") || make === m
                ? "bg-gray-700 border-gray-600 text-white"
                : "border-gray-800 text-gray-500 hover:border-gray-700 hover:text-gray-300"
            )}
          >
            {m}
          </button>
        ))}
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 18 }).map((_, i) => (
            <ListingCardSkeleton key={i} />
          ))}
        </div>
      ) : data?.data.length === 0 ? (
        <EmptyState
          title="No deals found"
          description="Try lowering the minimum score threshold or selecting a different make."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.data.map((listing: Listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      )}

      {data && data.total_pages > 1 && (
        <Pagination page={page} totalPages={data.total_pages} onChange={setPage} />
      )}
    </div>
  );
}