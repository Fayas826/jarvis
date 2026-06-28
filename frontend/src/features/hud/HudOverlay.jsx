export default function HudOverlay() {
  return (
    <div className="absolute inset-0 pointer-events-none z-50 overflow-hidden">
      <div className="w-full h-full border-[1px] border-blue-500/10 m-2 rounded-xl"></div>
      <div className="absolute top-10 left-10 w-32 h-32 border border-blue-400/20 rounded-full"></div>
      <div className="absolute bottom-20 right-20 w-40 h-40 border border-blue-400/20 rounded-full"></div>
      <div className="absolute top-1/2 left-0 w-8 h-[1px] bg-blue-500/50"></div>
      <div className="absolute top-1/2 right-0 w-8 h-[1px] bg-blue-500/50"></div>
    </div>
  );
}
