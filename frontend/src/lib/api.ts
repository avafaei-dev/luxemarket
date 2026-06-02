import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

// ── Types ─────────────────────────────────────────────────────────────────────

export interface DealScore {
  id: string;
  listing_id: string;
  score: string;
  discount_pct: string;
  price_delta: string;
  computed_at: string;
}

export interface Valuation {
  id: string;
  listing_id: string;
  estimated_value: string;
  confidence: string;
  comp_count: number;
  method: string;
  computed_at: string;
}

export interface Listing {
  id: string;
  make: string;
  model: string;
  trim: string | null;
  year: number;
  mileage: number | null;
  price: string;
  location_city: string | null;
  location_state: string | null;
  condition: string | null;
  images: string[] | null;
  listed_at: string | null;
  deal_score: DealScore | null;
  valuation: Valuation | null;
}

export interface ListingDetail extends Listing {
  source: string;
  color_exterior: string | null;
  color_interior: string | null;
  body_style: string | null;
  transmission: string | null;
  fuel_type: string | null;
  description: string | null;
  url: string | null;
  currency: string;
  is_active: boolean;
}

export interface ListingsResponse {
  data: Listing[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface MakeCount {
  make: string;
  count: number;
}

export interface ModelCount {
  model: string;
  count: number;
}

export interface MarketSnapshot {
  make: string;
  model: string;
  snapshot_date: string;
  avg_price: number;
  median_price: number;
  listing_count: number;
  avg_mileage: number;
  avg_deal_score: number;
}

export interface TrendsSummary {
  total_listings: number;
  avg_price: number;
  avg_deal_score: number;
  top_make: string;
}

export interface SearchFilters {
  query?: string;
  make?: string[];
  model?: string[];
  year_min?: number;
  year_max?: number;
  price_min?: number;
  price_max?: number;
  mileage_max?: number;
  condition?: string[];
  location_state?: string[];
  min_deal_score?: number;
  sort?: string;
  page?: number;
  limit?: number;
}

// ── API functions ─────────────────────────────────────────────────────────────

export async function getListings(params?: Record<string, string | number>): Promise<ListingsResponse> {
  const { data } = await api.get("/listings", { params });
  return data;
}

export async function getListing(id: string): Promise<ListingDetail> {
  const { data } = await api.get(`/listings/${id}`);
  return data;
}

export async function getTopDeals(limit = 50): Promise<ListingsResponse> {
  const { data } = await api.get("/listings/top-deals", { params: { limit } });
  return data;
}

export async function searchListings(filters: SearchFilters): Promise<ListingsResponse> {
  const { data } = await api.post("/listings/search", filters);
  return data;
}

export async function getMakes(): Promise<MakeCount[]> {
  const { data } = await api.get("/makes");
  return data;
}

export async function getModels(make: string): Promise<ModelCount[]> {
  const { data } = await api.get(`/makes/${make}/models`);
  return data;
}

export async function getTrends(make?: string, model?: string): Promise<{ data: MarketSnapshot[]; total: number }> {
  const { data } = await api.get("/trends", { params: { make, model } });
  return data;
}

export async function getTrendsSummary(): Promise<TrendsSummary> {
  const { data } = await api.get("/trends/summary");
  return data;
}