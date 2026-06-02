import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatPrice(price: string | number): string {
  const num = typeof price === "string" ? parseFloat(price) : price;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(num);
}

export function formatMileage(mileage: number | null): string {
  if (mileage === null || mileage === undefined) return "N/A";
  if (mileage === 0) return "New";
  return new Intl.NumberFormat("en-US").format(mileage) + " mi";
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-US").format(Math.round(n));
}

export function scoreColor(score: number): string {
  if (score >= 70) return "text-emerald-400";
  if (score >= 40) return "text-amber-400";
  return "text-red-400";
}

export function scoreBg(score: number): string {
  if (score >= 70) return "bg-emerald-400/10 border-emerald-400/30";
  if (score >= 40) return "bg-amber-400/10 border-amber-400/30";
  return "bg-red-400/10 border-red-400/30";
}

export function scoreLabel(score: number): string {
  if (score >= 80) return "Great Deal";
  if (score >= 60) return "Good Deal";
  if (score >= 40) return "Fair Price";
  if (score >= 20) return "Above Market";
  return "Overpriced";
}

export function conditionLabel(condition: string | null): string {
  switch (condition) {
    case "new": return "New";
    case "cpo": return "CPO";
    case "used": return "Used";
    default: return condition ?? "Unknown";
  }
}