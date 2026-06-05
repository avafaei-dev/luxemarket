"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ExternalLink, MapPin, Calendar, Gauge } from "lucide-react";
import { Listing, getListing, searchListings } from "@/lib/api";
import { DealScoreBadge } from "@/components/DealScoreBadge";
import { PriceVsValueBar } from "@/components/PriceVsValueBar";
import { SpecTable } from "@/components/SpecTable";
import { ListingCard } from "@/components/ListingCard";
import { ListingCardSkeleton } from "@/components/ListingCardSkeleton";
import { formatPrice, formatMileage, conditionLabel } from "@/lib/utils";

const MAKE_COLORS: Record<string, string> = {
    "BMW": "#1C3557",
    "Mercedes-Benz": "#222222",
    "Porsche": "#8B0000",
    "Audi": "#CC0000",
    "Ferrari": "#CC0000",
    "Lamborghini": "#1A1A2E",
    "Bentley": "#1B4332",
    "Rolls-Royce": "#2C2C54",
    "McLaren": "#FF4700",
    "Aston Martin": "#1A3A2A",
    "Maserati": "#00274D",
    "Lexus": "#2D2D2D",
  };

export default function ListingDetailPage() {
    const params = useParams();
    const id = params.id as string;
    const router = useRouter();

  const { data: listing, isLoading, error } = useQuery({
    queryKey: ["listing", id],
    queryFn: () => getListing(id),
    enabled: !!id,
  });

  // Load comparable listings (same make/model)
  const { data: comps } = useQuery({
    queryKey: ["comps", listing?.make, listing?.model],
    queryFn: () =>
      searchListings({
        make: listing ? [listing.make] : [],
        model: listing ? [listing.model] : [],
        sort: "score_desc",
        limit: 4,
      }),
    enabled: !!listing,
    select: (data) => data.data.filter((l) => l.id !== id).slice(0, 3),
  });

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto space-y-6 animate-pulse">
        <div className="h-8 w-32 bg-gray-800 rounded" />
        <div className="h-80 bg-gray-800 rounded-xl" />
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 h-64 bg-gray-800 rounded-xl" />
          <div className="h-64 bg-gray-800 rounded-xl" />
        </div>
      </div>
    );
  }

  if (error || !listing) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-400 mb-4">Listing not found.</p>
        <button onClick={() => router.back()} className="text-amber-400 hover:underline">
          Go back
        </button>
      </div>
    );
  }

  const score = listing.deal_score?.score ? parseFloat(listing.deal_score.score) : null;
  const hasValuation = listing.valuation?.estimated_value != null;

  const specs = [
    { label: "Year", value: listing.year.toString() },
    { label: "Condition", value: conditionLabel(listing.condition) },
    { label: "Mileage", value: formatMileage(listing.mileage) },
    { label: "Body Style", value: listing.body_style },
    { label: "Transmission", value: listing.transmission },
    { label: "Fuel Type", value: listing.fuel_type },
    { label: "Exterior Color", value: listing.color_exterior },
    { label: "Interior Color", value: listing.color_interior },
    { label: "VIN", value: listing.vin },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to listings
      </button>

      {/* Hero image */}
{/* Hero — branded make placeholder */}
<div
  className="relative h-80 md:h-96 rounded-2xl overflow-hidden"
  style={{ backgroundColor: MAKE_COLORS[listing.make] ?? "#2D2D2D" }}
>
  <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-black/40" />
  <div className="absolute inset-0 flex flex-col items-center justify-center">
    <span className="text-8xl font-bold text-white/15 tracking-tighter select-none">
      {listing.make.split("-")[0].toUpperCase()}
    </span>
    <span className="text-sm font-semibold text-white/40 uppercase tracking-[0.25em] mt-3">
      {listing.model}
    </span>
  </div>
</div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left — main info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title and price */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <p className="text-gray-500 text-sm mb-1">{listing.year}</p>
                <h1 className="text-2xl font-bold text-white">
                  {listing.make} {listing.model}
                </h1>
                {listing.trim && (
                  <p className="text-gray-400 mt-1">{listing.trim}</p>
                )}
              </div>
              {score !== null && <DealScoreBadge score={score} size="lg" />}
            </div>

            <div className="text-3xl font-bold text-white mb-4">
              {formatPrice(listing.price)}
            </div>

            <div className="flex flex-wrap gap-4 text-sm text-gray-400">
              {listing.mileage !== null && (
                <span className="flex items-center gap-1.5">
                  <Gauge className="w-4 h-4" />
                  {formatMileage(listing.mileage)}
                </span>
              )}
              {listing.location_city && (
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  {listing.location_city}, {listing.location_state}
                </span>
              )}
              {listing.listed_at && (
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  {new Date(listing.listed_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </span>
              )}
            </div>

            {listing.url && (
              <a
                href={listing.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-sm text-amber-400 hover:text-amber-300"
              >
                View original listing <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>

          {/* Description */}
          {listing.description && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold text-white mb-3">Description</h2>
              <p className="text-gray-400 text-sm leading-relaxed">{listing.description}</p>
            </div>
          )}

          {/* Specs */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="font-semibold text-white mb-4">Specifications</h2>
            <SpecTable specs={specs} />
          </div>
        </div>

        {/* Right — deal analysis */}
        <div className="space-y-4">
          {/* Valuation card */}
          {hasValuation && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold text-white mb-4">Deal Analysis</h2>
              <PriceVsValueBar
                price={listing.price}
                estimatedValue={listing.valuation!.estimated_value!}
              />
              <div className="mt-4 pt-4 border-t border-gray-800 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Model version</span>
                  <span className="text-gray-400">{listing.valuation!.method}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Confidence</span>
                  <span className="text-gray-400">
                    {listing.valuation!.confidence
                      ? `${(parseFloat(listing.valuation!.confidence) * 100).toFixed(0)}%`
                      : "N/A"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Comparable listings</span>
                  <span className="text-gray-400">{listing.valuation!.comp_count}</span>
                </div>
              </div>
            </div>
          )}

          {/* Quick specs summary */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="font-semibold text-white mb-4">At a Glance</h2>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "Condition", value: conditionLabel(listing.condition) },
                { label: "Body", value: listing.body_style ?? "—" },
                { label: "Fuel", value: listing.fuel_type ?? "—" },
                { label: "Transmission", value: listing.transmission?.split(" ")[0] ?? "—" },
              ].map((item) => (
                <div key={item.label} className="bg-gray-800/50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                  <p className="text-sm font-medium text-white truncate">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Comparable listings */}
      {comps && comps.length > 0 && (
        <div>
          <h2 className="font-semibold text-white mb-4">
            Similar {listing.make} {listing.model} Listings
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {comps.map((comp: Listing) => (
              <ListingCard key={comp.id} listing={comp} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}