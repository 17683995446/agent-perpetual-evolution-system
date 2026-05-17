import { useEffect, useRef, useState } from 'react'
import { GitBranch, Play, Pause, RefreshCw, ZoomIn, ZoomOut, Download } from 'lucide-react'
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
    tertiaryColor: '#1e293b',
  },
})

const flowcharts = [
  {
    id: 'task-execution',
    title: '任务执行流程',
    description: '展示任务从提交到完成的完整流程',
    type: '任务执行',
    code: `
flowchart TD
    A[接收任务请求] --> B{验证参数}
    B -->|无效| C[返回错误]
    B -->|有效| D[创建任务实例]
    D --> E[分配优先级]
    E --> F[加入任务队列]
    F --> G{检查缓存}
    G -->|命中| H[返回缓存结果]
    G -->|未命中| I[选择Agent]
    I --> J[执行任务]
    J --> K{执行成功?}
    K -->|失败| L[重试机制]
    L -->|可重试| I
    L -->|不可重试| M[记录错误]
    K -->|成功| N[更新缓存]
    N --> O[返回结果]
    C --> P[结束]
    H --> P
    M --> P
    O --> P
    `,
  },
  {
    id: 'evolution-cycle',
    title: '进化循环流程',
    description: '系统自我发现、自我优化、持续进化的循环过程',
    type: '进化循环',
    code: `
flowchart TD
    A[系统启动] --> B[初始化组件]
    B --> C[加载配置]
    C --> D[启动监控]
    D --> E{检测到问题?}
    E -->|否| F[继续运行]
    F --> D
    E -->|是| G[记录问题详情]
    G --> H[根因分析]
    H --> I[生成改进方案]
    I --> J[评估改进风险]
    J --> K{风险可接受?}
    K -->|否| L[放弃改进]
    L --> D
    K -->|是| M[实施改进]
    M --> N[验证效果]
    N --> O{改进有效?}
    O -->|是| P[固化改进]
    O -->|否| Q[回滚改进]
    P --> R[记录经验]
    Q --> D
    R --> D
    `,
  },
  {
    id: 'multi-agent',
    title: '多Agent协作流程',
    description: '多个Agent协同工作、负载均衡、结果聚合',
    type: '多Agent',
    code: `
flowchart LR
    subgraph Init["初始化阶段"]
        A1[创建Agent池] --> A2[初始化Agent]
        A2 --> A3[建立通信通道]
        A3 --> A4[等待任务]
    end

    subgraph Task["任务处理"]
        B1[接收任务] --> B2{任务类型}
        B2 -->|简单| B3[单个Agent处理]
        B2 -->|复杂| B4[任务分解]
        B4 --> B5[并行执行]
        B3 --> B6[结果处理]
        B5 --> B7[等待完成]
        B7 --> B6
        B6 --> B8[结果聚合]
    end

    subgraph Monitor["监控协调"]
        C1[负载监控] --> C2{负载过高?}
        C2 -->|是| C3[增加Agent]
        C2 -->|否| C4{负载过低?}
        C4 -->|是| C5[减少Agent]
        C3 --> A4
        C5 --> A4
        C1 --> A4
    end

    Init --> Task
    Task --> Monitor
    Monitor --> Task
    `,
  },
  {
    id: 'fault-recovery',
    title: '故障恢复流程',
    description: '故障检测、断路、恢复的完整流程',
    type: '故障恢复',
    code: `
flowchart TD
    A[系统运行] --> B{健康检查}
    B -->|正常| A
    B -->|异常| C[记录故障]
    C --> D[触发断路器]
    D --> E{故障类型}
    E -->|超时| F[重试机制]
    E -->|错误| G[降级处理]
    E -->|崩溃| H[故障转移]
    F --> I{重试成功?}
    I -->|是| J[恢复运行]
    I -->|否| G
    G --> K[返回降级结果]
    H --> L[切换备用实例]
    L --> J
    J --> M[关闭断路器]
    K --> A
    M --> A
    `,
  },
]

export default function Flowcharts() {
  const [activeFlowchart, setActiveFlowchart] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [zoom, setZoom] = useState(1)
  const diagramRef = useRef<HTMLDivElement>(null)
  const mermaidRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const diagram = flowcharts[activeFlowchart]
    if (mermaidRef.current) {
      mermaidRef.current.innerHTML = ''
    }

    mermaid.render(`flowchart-${diagram.id}`, diagram.code).then((svg) => {
      if (mermaidRef.current) {
        mermaidRef.current.innerHTML = svg
      }
    })
  }, [activeFlowchart])

  const handleZoomIn = () => setZoom(Math.min(zoom + 0.2, 2))
  const handleZoomOut = () => setZoom(Math.max(zoom - 0.2, 0.5))

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">流程图可视化</h2>
          <p className="text-slate-400">展示系统核心业务流程和决策逻辑</p>
        </div>
      </div>

      {/* Flowchart Selector */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {flowcharts.map((flowchart, index) => (
          <button
            key={flowchart.id}
            onClick={() => setActiveFlowchart(index)}
            className={`p-4 rounded-xl border transition-all ${
              activeFlowchart === index
                ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                : 'bg-slate-800/50 border-slate-700/50 text-slate-300 hover:border-cyan-500/30'
            }`}
          >
            <div className="flex items-center space-x-2 mb-2">
              <GitBranch className="w-5 h-5" />
              <span className="font-medium">{flowchart.type}</span>
            </div>
            <div className="text-sm">{flowchart.title}</div>
          </button>
        ))}
      </div>

      {/* Main Flowchart Display */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-1">
              {flowcharts[activeFlowchart].title}
            </h3>
            <p className="text-sm text-slate-400">
              {flowcharts[activeFlowchart].description}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 transition-colors"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setActiveFlowchart(activeFlowchart)}
              className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30 text-purple-400 hover:bg-purple-500/30 transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={handleZoomOut}
              className="p-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700 transition-colors"
            >
              <ZoomOut className="w-5 h-5" />
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

      {/* Flowchart Details */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 className="text-lg font-semibold text-white mb-4">流程说明</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {flowcharts[activeFlowchart].id === 'task-execution' && (
            <>
              <div className="space-y-3">
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <div className="text-sm font-medium text-cyan-400 mb-2">主要流程</div>
                  <div className="text-sm text-slate-300 space-y-1">
                    <div>1. 接收并验证任务请求</div>
                    <div>2. 创建任务实例并分配优先级</div>
                    <div>3. 检查缓存是否命中</div>
                    <div>4. 选择合适的Agent执行任务</div>
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <div className="text-sm font-medium text-cyan-400 mb-2">错误处理</div>
                  <div className="text-sm text-slate-300 space-y-1">
                    <div>• 参数验证失败返回错误</div>
                    <div>• 执行失败时触发重试机制</div>
                    <div>• 不可重试错误记录详情</div>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <div className="text-sm font-medium text-cyan-400 mb-2">优化策略</div>
                  <div className="text-sm text-slate-300 space-y-1">
                    <div>• 缓存机制提升响应速度</div>
                    <div>• 智能Agent选择算法</div>
                    <div>• 多级重试机制</div>
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <div className="text-sm font-medium text-cyan-400 mb-2">性能指标</div>
                  <div className="text-sm text-slate-300 space-y-1">
                    <div>• 平均响应时间: &lt;100ms</div>
                    <div>• 缓存命中率: &gt;80%</div>
                    <div>• 任务成功率: &gt;99%</div>
                  </div>
                </div>
              </div>
            </>
          )}
          {flowcharts[activeFlowchart].id === 'evolution-cycle' && (
            <div className="space-y-3 md:col-span-2">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-cyan-400 mb-2">进化循环核心要素</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-300">
                  <div>
                    <div className="font-medium text-white mb-2">持续监控</div>
                    <div>实时监控系统状态，自动检测异常和性能瓶颈</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">智能分析</div>
                    <div>基于历史数据和机器学习，进行根因分析和趋势预测</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">自动优化</div>
                    <div>实施改进方案，验证效果，固化成功经验</div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {flowcharts[activeFlowchart].id === 'multi-agent' && (
            <div className="space-y-3 md:col-span-2">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-cyan-400 mb-2">多Agent协作机制</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-300">
                  <div>
                    <div className="font-medium text-white mb-2">任务分解</div>
                    <div>复杂任务自动分解为多个子任务，并行处理提升效率</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">动态负载均衡</div>
                    <div>根据系统负载动态调整Agent数量，优化资源利用</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">结果聚合</div>
                    <div>多Agent结果智能合并，保证数据一致性</div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {flowcharts[activeFlowchart].id === 'fault-recovery' && (
            <div className="space-y-3 md:col-span-2">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-cyan-400 mb-2">故障恢复策略</div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-slate-300">
                  <div>
                    <div className="font-medium text-white mb-2">快速检测</div>
                    <div>健康检查机制，毫秒级故障发现</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">断路保护</div>
                    <div>防止故障蔓延，保护系统整体</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">智能降级</div>
                    <div>优雅降级，保证核心功能可用</div>
                  </div>
                  <div>
                    <div className="font-medium text-white mb-2">自动恢复</div>
                    <div>故障转移和自动重启，快速恢复服务</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
