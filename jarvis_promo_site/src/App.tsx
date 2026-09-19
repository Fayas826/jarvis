import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import Canvas4D from './components/Canvas4D'
import { Search, Menu, Globe, ArrowRight } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-black text-white font-sans overflow-x-hidden selection:bg-cyan-500/30">
      
      {/* 4D Background Canvas */}
      <div className="fixed inset-0 z-0 opacity-40 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 6], fov: 75 }}>
          <Suspense fallback={null}>
            <Canvas4D />
          </Suspense>
        </Canvas>
      </div>

      {/* Content Overlay */}
      <div className="relative z-10 flex flex-col min-h-screen">
        
        {/* Navigation */}
        <header className="flex items-center justify-between px-6 py-4 md:px-12 backdrop-blur-md bg-black/50 border-b border-zinc-800/50 sticky top-0">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold tracking-widest uppercase flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]"></div>
              JARVIS AI
            </h1>
            <nav className="hidden md:flex gap-6 text-sm font-medium text-zinc-300">
              <a href="#" className="hover:text-white transition-colors">Research</a>
              <a href="#" className="hover:text-white transition-colors">Products</a>
              <a href="#" className="hover:text-white transition-colors">Safety</a>
              <a href="#" className="hover:text-white transition-colors">Company</a>
            </nav>
          </div>
          <div className="flex items-center gap-4 text-zinc-300">
            <Search className="w-5 h-5 cursor-pointer hover:text-white transition-colors hidden md:block" />
            <button className="hidden md:block text-sm hover:text-white transition-colors">Log in</button>
            <button className="bg-white text-black px-4 py-1.5 rounded-full text-sm font-medium hover:bg-zinc-200 transition-colors">
              Try JARVIS
            </button>
            <Menu className="w-6 h-6 md:hidden cursor-pointer" />
          </div>
        </header>

        {/* Hero Section */}
        <main className="flex-1 flex flex-col justify-center px-6 md:px-24 py-20 max-w-7xl mx-auto w-full">
          <div className="max-w-3xl space-y-8 animate-fade-in-up">
            <h2 className="text-5xl md:text-7xl font-semibold tracking-tight leading-tight">
              Creating <span className="text-cyan-400">Omnipresent AI</span> that benefits all of humanity.
            </h2>
            <p className="text-xl md:text-2xl text-zinc-400 max-w-2xl leading-relaxed">
              We are researching and building safe, autonomous intelligence designed to act as your ubiquitous engineering architect, cybersecurity defender, and creative partner.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button className="bg-cyan-500 text-black px-6 py-3 rounded-full font-medium hover:bg-cyan-400 transition-colors flex items-center justify-center gap-2">
                Discover the 106-Agent Swarm <ArrowRight className="w-4 h-4" />
              </button>
              <button className="px-6 py-3 rounded-full font-medium border border-zinc-700 hover:bg-zinc-900 transition-colors flex items-center justify-center gap-2">
                View Research Index
              </button>
            </div>
          </div>
        </main>

        {/* Featured Grid (OpenAI Style) */}
        <section className="px-6 md:px-24 py-20 border-t border-zinc-800/50 bg-linear-to-b from-transparent to-black">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-4 group cursor-pointer">
              <div className="aspect-video bg-zinc-900 rounded-xl overflow-hidden border border-zinc-800 group-hover:border-zinc-600 transition-colors relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?auto=format&fit=crop&q=80')] bg-cover bg-center opacity-40 group-hover:opacity-60 transition-opacity"></div>
              </div>
              <h3 className="text-lg font-medium">JARVIS Core Engine Update</h3>
              <p className="text-sm text-zinc-400">Read about our transition to a 106-Agent Cryogenic Swarm Architecture.</p>
              <a href="#" className="text-cyan-400 text-sm font-medium flex items-center gap-1">Read more <ArrowRight className="w-3 h-3" /></a>
            </div>
            
            <div className="space-y-4 group cursor-pointer">
              <div className="aspect-video bg-zinc-900 rounded-xl overflow-hidden border border-zinc-800 group-hover:border-zinc-600 transition-colors relative">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&q=80')] bg-cover bg-center opacity-40 group-hover:opacity-60 transition-opacity"></div>
              </div>
              <h3 className="text-lg font-medium">Meta-Architect Auto-Healing</h3>
              <p className="text-sm text-zinc-400">How JARVIS writes its own source patches using advanced linter diagnostics.</p>
              <a href="#" className="text-cyan-400 text-sm font-medium flex items-center gap-1">Read more <ArrowRight className="w-3 h-3" /></a>
            </div>

            <div className="space-y-4 group cursor-pointer">
              <div className="aspect-video bg-zinc-900 rounded-xl overflow-hidden border border-zinc-800 group-hover:border-zinc-600 transition-colors relative">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1639322537228-f710d846310a?auto=format&fit=crop&q=80')] bg-cover bg-center opacity-40 group-hover:opacity-60 transition-opacity"></div>
              </div>
              <h3 className="text-lg font-medium">Hardware & Safety Alignment</h3>
              <p className="text-sm text-zinc-400">Discover how the Swarm optimizes for minimal VRAM constraints.</p>
              <a href="#" className="text-cyan-400 text-sm font-medium flex items-center gap-1">Read more <ArrowRight className="w-3 h-3" /></a>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="px-6 md:px-24 py-12 border-t border-zinc-800 text-zinc-400 text-sm flex flex-col md:flex-row justify-between items-center gap-4 bg-black">
          <div className="flex items-center gap-2 font-medium text-white">
            <Globe className="w-4 h-4" /> JARVIS Research 2026
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-white transition-colors">Twitter</a>
            <a href="#" className="hover:text-white transition-colors">YouTube</a>
            <a href="#" className="hover:text-white transition-colors">GitHub</a>
            <a href="#" className="hover:text-white transition-colors">Discord</a>
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Use</a>
          </div>
        </footer>

      </div>
    </div>
  )
}

export default App
