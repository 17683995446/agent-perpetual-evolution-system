import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Home, Layers, GitBranch, Activity, Box, BookOpen, Menu, X } from 'lucide-react'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Architecture from './pages/Architecture'
import Flowcharts from './pages/Flowcharts'
import SequenceDiagrams from './pages/SequenceDiagrams'
import ModuleDiagram from './pages/ModuleDiagram'
import Documentation from './pages/Documentation'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: '仪表盘' },
    { path: '/architecture', icon: Layers, label: '架构图' },
    { path: '/flowcharts', icon: GitBranch, label: '流程图' },
    { path: '/sequence', icon: Activity, label: '时序图' },
    { path: '/modules', icon: Box, label: '模块图' },
    { path: '/docs', icon: BookOpen, label: '文档中心' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-lg border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Layers className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Agent永续自进化系统</h1>
                <p className="text-xs text-slate-400">可视化监控平台 v2.0</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    isActive(item.path)
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              ))}
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-300 hover:bg-slate-700"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="md:hidden border-t border-slate-700 bg-slate-900/95 backdrop-blur-lg">
            <div className="px-4 py-3 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMenuOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                    isActive(item.path)
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'text-slate-300 hover:bg-slate-700/50'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              ))}
            </div>
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/flowcharts" element={<Flowcharts />} />
          <Route path="/sequence" element={<SequenceDiagrams />} />
          <Route path="/modules" element={<ModuleDiagram />} />
          <Route path="/docs" element={<Documentation />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="text-center md:text-left">
              <p className="text-sm text-slate-400">
                Agent永续自进化系统可视化平台
              </p>
              <p className="text-xs text-slate-500 mt-1">
                © 2026 8层架构 · 多Agent协作 · 持续进化
              </p>
            </div>
            <div className="flex items-center space-x-6">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                系统运行中
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
