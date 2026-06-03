"use client";

import { useState, useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Car, TrendingUp, DollarSign, Award } from "lucide-react";
import { searchListings, getTrendsSummary, Listing } from "@/lib/api";
import { ListingCard } from "@/components/ListingCard";
import { ListingCardSkeleton } from "@/components/ListingCardSkeleton";
import { FilterSidebar, Filters, DEFAULT_FILTERS } from "@/components/FilterSidebar";
import { SearchBar } from "@/components/SearchBar";
import { Pagination } from "@/components/Pagination";
import { StatCard } from "@/components/StatCard";
import { EmptyState } from "@/components/EmptyState";
import { formatPrice } from "@/lib/utils";

export default function Home() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [debouncedQuery, setDebouncedQuery] = useState("");

  // Debounce search query
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQuery(query), 400);
    return () => clearTimeout(t);
  }, [query]);

  // Reset to page 1 when filters change
  useEffect(() => { setPage(1); }, [filters, debouncedQuery]);

  const { data: summary } = useQuery({
    queryKey: ["trends-summary"],
    queryFn: getTrendsSummary,
    staleTime: 2 * 60 * 1000,
  });

  const { data: listings, isLoading } = useQuery({
    queryKey: ["listings", filters, debouncedQuery, page],
    queryFn: () =>
      searchListings({
        query: debouncedQuery || undefined,
        make: filters.make ? [filters.make] : undefined,
        model: filters.model ? [filters.model] : undefined,
        year_min: filters.year_min ? parseInt(filters.year_min) : undefined,
        year_max: filters.year_max ? parseInt(filters.year_max) : undefined,
        price_min: filters.price_min ? parseFloat(filters.price_min) : undefined,
        price_max: filters.price_max ? parseFloat(filters.price_max) : undefined,
        mileage_max: filters.mileage_max ? parseInt(filters.mileage_max) : undefined,
        condition: filters.condition ? [filters.condition] : undefined,
        location_state: filters.location_state ? [filters.location_state] : undefined,
        sort: filters.sort,
        page,
        limit: 18,
      }),
    placeholderData: (prev) => prev,
  });

  return (
    <div className="space-y-6">
      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Listings"
          value={summary ? summary.total_listings.toLocaleString() : "—"}
          icon={Car}
          accent="amber"
        />
        <StatCard
          label="Avg Deal Score"
          value={summary ? summary.avg_deal_score.toFixed(1) : "—"}
          icon={Award}
          accent="emerald"
        />
        <StatCard
          label="Avg Market Price"
          value={summary ? formatPrice(summary.avg_price) : "—"}
          icon={DollarSign}
          accent="blue"
        />
        <StatCard
          label="Top Make"
          value={summary?.top_make ?? "—"}
          icon={TrendingUp}
          accent="purple"
        />
      </div>

      {/* Search bar */}
      <SearchBar value={query} onChange={setQuery} />

      {/* Main content */}
      <div className="flex gap-6">
        <FilterSidebar
          filters={filters}
          onChange={setFilters}
          totalResults={listings?.total ?? 0}
        />

        <div className="flex-1 min-w-0">
          {/* Listing grid */}
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 18 }).map((_, i) => (
                <ListingCardSkeleton key={i} />
              ))}
            </div>
          ) : listings?.data.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {listings?.data.map((listing: Listing) => (
                <ListingCard key={listing.id} listing={listing} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {listings && listings.total_pages > 1 && (
            <Pagination
              page={page}
              totalPages={listings.total_pages}
              onChange={setPage}
            />
          )}
        </div>
      </div>
    </div>
  );
}