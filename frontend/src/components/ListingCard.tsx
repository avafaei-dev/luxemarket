import Link from "next/link";
import { MapPin, Gauge, ArrowUpRight } from "lucide-react";
import { DealScoreBadge } from "./DealScoreBadge";
import { formatPrice, formatMileage, conditionLabel, conditionStyle } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Listing } from "@/lib/api";

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

interface Props {
  listing: Listing;
}

export function ListingCard({ listing }: Props) {
  const score = listing.deal_score?.score ?? null;
  const discountPct = listing.deal_score?.discount_pct
    ? parseFloat(listing.deal_score.discount_pct)
    : null;

  return (
    <Link href={`/listings/${listing.id}`} className="group block">
      <article className="bg-white rounded-2xl border border-surface-border shadow-card hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-200 overflow-hidden">

        {/* Make placeholder */}
        <div
          className="relative h-44 overflow-hidden"
          style={{ backgroundColor: MAKE_COLORS[listing.make] ?? "#2D2D2D" }}
        >
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-black/30" />

          {/* Make + model text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center px-4">
            <span className="text-5xl font-bold text-white/20 tracking-tighter select-none text-center leading-none">
              {listing.make.split("-")[0].toUpperCase()}
            </span>
            <span className="text-xs font-semibold text-white/40 uppercase tracking-[0.2em] mt-2 text-center truncate w-full text-center">
              {listing.model}
            </span>
          </div>

          {/* Condition + deal score badges */}
          <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
            <span className={cn(
              "inline-flex items-center px-2 py-0.5 rounded-full text-2xs font-semibold border bg-white/90",
              conditionStyle(listing.condition)
            )}>
              {conditionLabel(listing.condition)}
            </span>
            {score && <DealScoreBadge score={score} size="sm" />}
          </div>

          {/* Discount pill */}
          {discountPct && discountPct > 5 && (
            <div className="absolute bottom-3 left-3">
              <span className="bg-deal-great text-white text-2xs font-semibold px-2.5 py-1 rounded-full">
                {discountPct.toFixed(0)}% below market
              </span>
            </div>
          )}
        </div>

        {/* Card content */}
        <div className="p-4">
          <div className="mb-3">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="text-2xs font-medium text-ink-muted uppercase tracking-wider mb-0.5">
                  {listing.year}
                </p>
                <h3 className="font-semibold text-ink text-base leading-tight truncate group-hover:text-accent transition-colors duration-150">
                  {listing.make} {listing.model}
                </h3>
              </div>
              <ArrowUpRight className="w-4 h-4 text-ink-disabled group-hover:text-accent shrink-0 mt-0.5 transition-colors duration-150" />
            </div>
          </div>

          {/* Price */}
          <div className="mb-3 pb-3 border-b border-surface-border">
            <p className="text-xl font-bold text-ink tracking-tight">
              {formatPrice(listing.price)}
            </p>
            {listing.valuation?.estimated_value && (
              <p className="text-xs text-ink-muted mt-0.5">
                est. <span className="text-ink-tertiary font-medium">{formatPrice(listing.valuation.estimated_value)}</span>
              </p>
            )}
          </div>

          {/* Metadata */}
          <div className="flex items-center gap-3 text-xs text-ink-muted">
            {listing.mileage !== null && (
              <span className="flex items-center gap-1">
                <Gauge className="w-3 h-3 shrink-0" />
                {formatMileage(listing.mileage)}
              </span>
            )}
            {listing.location_city && (
              <span className="flex items-center gap-1 truncate">
                <MapPin className="w-3 h-3 shrink-0" />
                <span className="truncate">{listing.location_city}, {listing.location_state}</span>
              </span>
            )}
          </div>
        </div>
      </article>
    </Link>
  );
}