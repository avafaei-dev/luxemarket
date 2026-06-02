export function ListingCardSkeleton() {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden animate-pulse">
        <div className="h-48 bg-gray-800" />
        <div className="p-4 space-y-3">
          <div className="flex justify-between">
            <div className="space-y-2">
              <div className="h-3 w-8 bg-gray-800 rounded" />
              <div className="h-4 w-32 bg-gray-800 rounded" />
            </div>
            <div className="h-6 w-20 bg-gray-800 rounded" />
          </div>
          <div className="flex gap-4">
            <div className="h-3 w-16 bg-gray-800 rounded" />
            <div className="h-3 w-24 bg-gray-800 rounded" />
          </div>
        </div>
      </div>
    );
  }