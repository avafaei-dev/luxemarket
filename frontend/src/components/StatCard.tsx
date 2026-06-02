import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface Props {
  label: string;
  value: string | number;
  subValue?: string;
  icon?: LucideIcon;
  accent?: "amber" | "emerald" | "blue" | "purple";
}

const accentMap = {
  amber: "text-amber-400 bg-amber-400/10",
  emerald: "text-emerald-400 bg-emerald-400/10",
  blue: "text-blue-400 bg-blue-400/10",
  purple: "text-purple-400 bg-purple-400/10",
};

export function StatCard({ label, value, subValue, icon: Icon, accent = "amber" }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{label}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subValue && <p className="text-xs text-gray-500 mt-1">{subValue}</p>}
        </div>
        {Icon && (
          <div className={cn("p-2 rounded-lg", accentMap[accent])}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
}