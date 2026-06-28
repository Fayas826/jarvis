export default function ArcReactor() {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
      <div className="w-64 h-64 rounded-full border-4 border-blue-400/50 animate-pulse shadow-[0_0_40px_#00bfff]">
        <div className="w-full h-full rounded-full border-2 border-blue-300/30 animate-spin"></div>
      </div>
    </div>
  );
}
