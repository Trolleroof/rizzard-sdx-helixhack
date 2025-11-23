export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-zinc-200 dark:border-zinc-700 border-t-blue-600 rounded-full animate-spin"></div>
      </div>
    </div>
  );
}

