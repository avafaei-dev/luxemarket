import Link from "next/link";
import Image from "next/image";
import { MapPin, Gauge } from "lucide-react";
import { DealScoreBadge } from "./DealScoreBadge";
import { formatPrice, formatMileage, conditionLabel } from "@/lib/utils";
import type { Listing } from "@/lib/api";

interface Props {
  listing: Listing;
}

export function ListingCard({ listing }: Props) {
  const score = listing.deal_score?.score ?? null;
  const imageUrl = listing.images?.[0] ?? null;

  return (
    <Link href={`/listings/${listing.id}`} className="group block">
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden hover:border-gray-600 transition-all duration-200 hover:shadow-lg hover:shadow-black/30 hover:-translate-y-0.5">
        {/* Image */}
        <div className="relative h-48 bg-gray-800 overflow-hidden">
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={`${listing.year} ${listing.make} ${listing.model}`}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-600">
              <span className="text-sm">No image</span>
            </div>
          )}

          {/* Condition badge */}
          <div className="absolute top-3 left-3">
            <span className="bg-gray-950/80 backdrop-blur text-gray-300 text-xs px-2 py-1 rounded-md font-medium">
              {conditionLabel(listing.condition)}
            </span>
          </div>

          {/* Deal score */}
          {score && (
            <div className="absolute top-3 right-3">
              <DealScoreBadge score={score} size="sm" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="flex items-start justify-between gap-2 mb-3">
            <div className="min-w-0">
              <p className="text-xs text-gray-500 mb-0.5">{listing.year}</p>
              <h3 className="font-semibold text-white truncate leading-tight">
                {listing.make} {listing.model}
              </h3>
              {listing.trim && (
                <p className="text-xs text-gray-500 truncate mt-0.5">{listing.trim}</p>
              )}
            </div>
            <div className="text-right shrink-0">
              <p className="font-bold text-white text-lg leading-tight">
                {formatPrice(listing.price)}
              </p>
              {listing.valuation?.estimated_value && (
                <p className="text-xs text-gray-500 leading-tight">
                  est. {formatPrice(listing.valuation.estimated_value)}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs text-gray-500">
            {listing.mileage !== null && (
              <span className="flex items-center gap-1">
                <Gauge className="w-3 h-3" />
                {formatMileage(listing.mileage)}
              </span>
            )}
            {listing.location_city && (
              <span className="flex items-center gap-1 truncate">
                <MapPin className="w-3 h-3 shrink-0" />
                {listing.location_city}, {listing.location_state}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}