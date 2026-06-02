import { Search } from "lucide-react";

interface Props {
  title?: string;
  description?: string;
}

export function EmptyState({
  title = "No listings found",
  description = "Try adjusting your filters or search terms.",
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="bg-gray-800/50 p-4 rounded-full mb-4">
        <Search className="w-8 h-8 text-gray-600" />
      </div>
      <h3 className="text-lg font-medium text-gray-300 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 max-w-xs">{description}</p>
    </div>
  );
}