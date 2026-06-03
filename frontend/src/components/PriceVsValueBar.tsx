import { formatPrice } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface Props {
  price: string | number;
  estimatedValue: string | number;
}

export function PriceVsValueBar({ price, estimatedValue }: Props) {
  const p = typeof price === "string" ? parseFloat(price) : price;
  const ev = typeof estimatedValue === "string" ? parseFloat(estimatedValue) : estimatedValue;

  const min = Math.min(p, ev) * 0.85;
  const max = Math.max(p, ev) * 1.1;
  const range = max - min;

  const pricePos = ((p - min) / range) * 100;
  const evPos = ((ev - min) / range) * 100;

  const discount = ((ev - p) / ev) * 100;
  const isGoodDeal = p < ev;

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">Listed Price</span>
        <span className="font-semibold text-white">{formatPrice(p)}</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">Estimated Value</span>
        <span className="font-semibold text-gray-300">{formatPrice(ev)}</span>
      </div>

      {/* Bar visualization */}
      <div className="relative h-2 bg-gray-800 rounded-full mt-4">
        {/* Fill between the two points */}
        <div
          className={cn(
            "absolute h-2 rounded-full",
            isGoodDeal ? "bg-emerald-500/40" : "bg-red-500/40"
          )}
          style={{
            left: `${Math.min(pricePos, evPos)}%`,
            width: `${Math.abs(pricePos - evPos)}%`,
          }}
        />
        {/* Estimated value marker */}
        <div
          className="absolute w-3 h-3 bg-gray-400 rounded-full -top-0.5 -translate-x-1/2 border-2 border-gray-900"
          style={{ left: `${evPos}%` }}
          title="Estimated value"
        />
        {/* Price marker */}
        <div
          className={cn(
            "absolute w-3 h-3 rounded-full -top-0.5 -translate-x-1/2 border-2 border-gray-900",
            isGoodDeal ? "bg-emerald-400" : "bg-red-400"
          )}
          style={{ left: `${pricePos}%` }}
          title="Listed price"
        />
      </div>

      <div className={cn(
        "text-sm font-medium",
        isGoodDeal ? "text-emerald-400" : "text-red-400"
      )}>
        {isGoodDeal
          ? `${Math.abs(discount).toFixed(1)}% below market value`
          : `${Math.abs(discount).toFixed(1)}% above market value`}
      </div>
    </div>
  );
}