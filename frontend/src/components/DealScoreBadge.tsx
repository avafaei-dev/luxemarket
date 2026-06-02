import { cn, scoreColor, scoreBg, scoreLabel } from "@/lib/utils";

interface Props {
  score: string | number | null;
  size?: "sm" | "md" | "lg";
}

export function DealScoreBadge({ score, size = "md" }: Props) {
  if (!score) return null;
  const num = typeof score === "string" ? parseFloat(score) : score;

  return (
    <div
      className={cn(
        "inline-flex flex-col items-center justify-center rounded-lg border font-semibold",
        scoreBg(num),
        size === "sm" && "px-2 py-1 min-w-[52px]",
        size === "md" && "px-3 py-2 min-w-[64px]",
        size === "lg" && "px-4 py-3 min-w-[80px]"
      )}
    >
      <span
        className={cn(
          scoreColor(num),
          size === "sm" && "text-sm",
          size === "md" && "text-lg",
          size === "lg" && "text-3xl"
        )}
      >
        {Math.round(num)}
      </span>
      <span className="text-gray-500 text-xs leading-tight">{scoreLabel(num)}</span>
    </div>
  );
}