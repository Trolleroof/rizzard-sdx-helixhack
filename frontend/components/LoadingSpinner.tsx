export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="relative">
        <div
          className="w-12 h-12 border-4 rounded-full animate-spin"
          style={{
            borderColor: '#FFCD00',
            borderTopColor: '#FF69A6',
          }}
        ></div>
      </div>
    </div>
  );
}

