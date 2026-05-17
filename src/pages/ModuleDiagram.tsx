import { useEffect, useRef, useState } from 'react'
import { Box, GitBranch, ZoomIn, ZoomOut, RotateCcw, Info } from 'lucide-react'
import mermaid from 'mermaid'

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#06b6d4',
    primaryTextColor: '#fff',
    primaryBorderColor: '#0891b2',
    lineColor: '#64748b',
    secondaryColor: '#8b5cf6',
  },
})

const moduleGroups = [
  {
    id: 'core-modules',
    title: '核心模块',
    modules: [
      { id: 'orchestrator', name: 'TaskOrchestrator', description: '任务编排器', layer: 'L2' },
      { id: 'evolution', name: 'EvolutionEngine', description: '进化引擎', layer: 'L3' },
      { id: 'agentpool', name: 'AgentPool', description: 'Agent池管理', layer: 'L3' },
    ],
  },
  {
    id: 'service-modules',
    title: '服务模块',
    modules: [
      { id: 'task-service', name: 'TaskService', description: '任务管理服务', layer: 'L3' },
      { id: 'knowledge', name: 'KnowledgeService', description: '知识学习服务', layer: 'L3' },
      { id: 'strategy', name: 'StrategyService', description: '策略优化服务', layer: 'L3' },
    ],
  },
  {
    id: 'infrastructure',
    title: '基础设施',
    modules: [
      { id: 'cache', name: 'CacheManager', description: '缓存管理器', layer: 'L7' },
      { id: 'concurrency', name: 'ConcurrencyPool', description: '并发任务池', layer: 'L7' },
      { id: 'batch', name: 'BatchProcessor', description: '批处理管理器', layer: 'L7' },
    ],
  },
  {
    id: 'data-layer',
    title: '数据层',
    modules: [
      { id: 'repository', name: 'TaskRepository', description: '任务仓库', layer: 'L5' },
      { id: 'knowledgebase', name: 'KnowledgeBase', description: '知识库', layer: 'L5' },
    ],
  },
]

const dependencies = `
graph TD
    subgraph Core["核心模块"]
        A[TaskOrchestrator]
        B[EvolutionEngine]
        C[AgentPool]
    end

    subgraph Service["服务模块"]
        D[TaskService]
        E[KnowledgeService]
        F[StrategyService]
    end

    subgraph Infrastructure["基础设施"]
        G[CacheManager]
        H[ConcurrencyPool]
        I[BatchProcessor]
    end

    subgraph Data["数据层"]
        J[TaskRepository]
        K[KnowledgeBase]
    end

    A --> D
    A --> C
    B --> E
    B --> F
    C --> G
    D --> J
    E --> K
    F --> G
    G --> H
    H --> I
    D --> G
    E --> G
`

export default function ModuleDiagram() {
  const [selectedModule, setSelectedModule] = useState<any>(null)
  const [zoom, setZoom] = useState(1)
  const mermaidRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (mermaidRef.current) {
      mermaidRef.current.innerHTML = ''
    }

    mermaid.render('moduleDependency', dependencies).then((svg) => {
      if (mermaidRef.current) {
        mermaidRef.current.innerHTML = svg
      }
    })
  }, [])

  const handleModuleClick = (module: any) => {
    setSelectedModule(module)
  }

  const handleZoomIn = () => setZoom(Math.min(zoom + 0.2, 1.5))
  const handleZoomOut = () => setZoom(Math.max(zoom - 0.2, 0.5))
  const handleReset = () => setZoom(1)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">模块依赖图</h2>
          <p className="text-slate-400">展示系统核心模块之间的依赖关系</p>
        </div>
      </div>

      {/* Module Groups */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {moduleGroups.map((group) => (
          <div
            key={group.id}
            className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm"
          >
            <h3 className="text-lg font-semibold text-cyan-400 mb-3">{group.title}</h3>
            <div className="space-y-2">
              {group.modules.map((module) => (
                <button
                  key={module.id}
                  onClick={() => handleModuleClick(module)}
                  className={`w-full p-3 rounded-lg border transition-all text-left ${
                    selectedModule?.id === module.id
                      ? 'bg-cyan-500/20 border-cyan-500/50'
                      : 'bg-slate-900/50 border-slate-700/50 hover:border-cyan-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{module.name}</span>
                    <span className="text-xs px-2 py-0.5 bg-slate-700 rounded text-slate-300">
                      {module.layer}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">{module.description}</div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Dependency Diagram */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-1">模块依赖关系图</h3>
            <p className="text-sm text-slate-400">点击模块查看详情，点击节点可查看更多信息</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleZoomOut}
              className="p-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700 transition-colors"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <button
              onClick={handleReset}
              className="p-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700 transition-colors"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
            <button
              onClick={handleZoomIn}
              className="p-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700 transition-colors"
            >
              <ZoomIn className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div
          ref={mermaidRef}
          className="flex justify-center overflow-auto"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}
        />
      </div>

      {/* Module Details */}
      {selectedModule && (
        <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-start space-x-4 mb-4">
            <div className="w-12 h-12 bg-cyan-500/20 border border-cyan-500/30 rounded-lg flex items-center justify-center flex-shrink-0">
              <Box className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="text-xl font-semibold text-white">{selectedModule.name}</h3>
                <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 text-xs rounded">
                  {selectedModule.layer}
                </span>
              </div>
              <p className="text-slate-400">{selectedModule.description}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-sm font-medium text-slate-400 mb-2">模块职责</div>
              <div className="text-sm text-slate-300">
                负责系统的核心业务逻辑和协调工作
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-sm font-medium text-slate-400 mb-2">依赖模块</div>
              <div className="text-sm text-slate-300">
                {selectedModule.id === 'orchestrator' && 'TaskService, AgentPool, CacheManager'}
                {selectedModule.id === 'evolution' && 'KnowledgeService, StrategyService'}
                {selectedModule.id === 'agentpool' && 'CacheManager'}
                {selectedModule.id === 'task-service' && 'TaskRepository, CacheManager'}
                {selectedModule.id === 'knowledge' && 'KnowledgeBase, CacheManager'}
                {selectedModule.id === 'strategy' && 'CacheManager'}
                {selectedModule.id === 'cache' && 'ConcurrencyPool'}
                {selectedModule.id === 'concurrency' && 'BatchProcessor'}
                {selectedModule.id === 'batch' && '无'}
                {selectedModule.id === 'repository' && '无'}
                {selectedModule.id === 'knowledgebase' && '无'}
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-sm font-medium text-slate-400 mb-2">被依赖模块</div>
              <div className="text-sm text-slate-300">
                {selectedModule.id === 'orchestrator' && '被TaskService调用'}
                {selectedModule.id === 'evolution' && '被API接口调用'}
                {selectedModule.id === 'agentpool' && '被Orchestrator调用'}
                {selectedModule.id === 'task-service' && '被Orchestrator调用'}
                {selectedModule.id === 'knowledge' && '被EvolutionEngine调用'}
                {selectedModule.id === 'strategy' && '被EvolutionEngine调用'}
                {selectedModule.id === 'cache' && '被AgentPool, TaskService等调用'}
                {selectedModule.id === 'concurrency' && '被CacheManager调用'}
                {selectedModule.id === 'batch' && '被ConcurrencyPool调用'}
                {selectedModule.id === 'repository' && '被TaskService调用'}
                {selectedModule.id === 'knowledgebase' && '被KnowledgeService调用'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dependency Matrix */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Info className="w-5 h-5 text-cyan-400" />
          <span>依赖关系说明</span>
        </h3>
        <div className="space-y-3 text-sm text-slate-300">
          <div className="flex items-start space-x-2">
            <GitBranch className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-medium text-white">TaskOrchestrator</span>
              <span className="text-slate-400"> 是核心协调器，依赖 TaskService、AgentPool 和 CacheManager</span>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <GitBranch className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-medium text-white">EvolutionEngine</span>
              <span className="text-slate-400"> 负责系统自我进化，依赖 KnowledgeService 和 StrategyService</span>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <GitBranch className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-medium text-white">CacheManager</span>
              <span className="text-slate-400"> 是性能优化的关键组件，被多个模块依赖</span>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <GitBranch className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-medium text-white">ConcurrencyPool</span>
              <span className="text-slate-400"> 提供并发处理能力，依赖 BatchProcessor</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
