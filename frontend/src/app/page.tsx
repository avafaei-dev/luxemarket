import { ListingCardSkeleton } from "@/components/ListingCardSkeleton";
import { DealScoreBadge } from "@/components/DealScoreBadge";
import { StatCard } from "@/components/StatCard";
import { Car } from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Listings" value="1,500" icon={Car} accent="amber" />
        <StatCard label="Avg Deal Score" value="48.7" accent="emerald" />
        <StatCard label="Avg Price" value="$147,820" accent="blue" />
        <StatCard label="Top Make" value="Audi" accent="purple" />
      </div>
      <div className="flex gap-3">
        <DealScoreBadge score={85} size="lg" />
        <DealScoreBadge score={55} size="lg" />
        <DealScoreBadge score={22} size="lg" />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <ListingCardSkeleton />
        <ListingCardSkeleton />
        <ListingCardSkeleton />
      </div>
    </div>
  );
}