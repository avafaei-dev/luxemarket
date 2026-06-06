import Link from "next/link";
import { Car } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <Car className="w-12 h-12 text-gray-700 mb-4" />
      <h2 className="text-xl font-semibold text-white mb-2">Page not found</h2>
      <p className="text-gray-500 mb-6">The page you are looking for does not exist.</p>
      <Link
        href="/"
        className="px-4 py-2 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-lg text-sm hover:bg-amber-400/20 transition-colors"
      >
        Back to Browse
      </Link>
    </div>
  );
}