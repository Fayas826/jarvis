export default function GlowCard({ title, desc }) {
  return (
    <div className="relative p-5 rounded-xl bg-white/5 backdrop-blur-xl border border-blue-500/20 hover:shadow-[0_0_30px_#00bfff] transition duration-300">
      <h3 className="text-lg font-bold text-blue-400">{title}</h3>
      <p className="text-sm text-gray-300 mt-2">{desc}</p>
    </div>
  );
}
