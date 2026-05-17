import { useEffect, useRef } from 'react'
import { Layers, ChevronRight, Database, Cpu, Server, Shield, Box, TestTube, Zap } from 'lucide-react'
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

const layers = [
  {
    id: 'layer1',
    name: 'Layer 1: 接口呈现层',
    icon: Zap,
    color: 'cyan',
    description: '提供多种接入方式，支持CLI、Web API、WebSocket',
    components: ['命令行接口(CLI)', 'RESTful API', 'WebSocket接口', '可视化界面'],
    technologies: ['FastAPI', 'CLI框架', 'WebSocket'],
    responsibilities: ['请求路由', '认证授权', '参数验证', '响应格式化'],
  },
  {
    id: 'layer2',
    name: 'Layer 2: 编排协调层',
    icon: Server,
    color: 'blue',
    description: '协调任务执行和系统组件的正常工作',
    components: ['任务编排器(Orchestrator)', '系统控制器(Controller)', '事件总线'],
    technologies: ['异步任务队列', '事件驱动架构'],
    responsibilities: ['任务调度', '组件协调', '负载均衡', '故障转移'],
  },
  {
    id: 'layer3',
    name: 'Layer 3: 业务服务层',
    icon: Cpu,
    color: 'purple',
    description: '实现核心业务逻辑和服务',
    components: ['任务管理服务', '进化引擎控制器', '知识学习服务', '策略优化服务'],
    technologies: ['业务规则引擎', '优化算法', '机器学习'],
    responsibilities: ['业务逻辑', '数据处理', '服务编排', '业务监控'],
  },
  {
    id: 'layer4',
    name: 'Layer 4: 领域模型层',
    icon: Box,
    color: 'indigo',
    description: '定义核心业务实体和数据模型',
    components: ['任务实体(Task)', 'Agent实体(Agent)', '进化记录实体', '模式实体'],
    technologies: ['Pydantic模型', '枚举类型', '数据校验'],
    responsibilities: ['实体定义', '业务规则', '数据验证', '状态管理'],
  },
  {
    id: 'layer5',
    name: 'Layer 5: 数据访问层',
    icon: Database,
    color: 'green',
    description: '数据持久化和查询管理',
    components: ['任务仓库(TaskRepository)', '知识库(KnowledgeBase)', '模式仓库'],
    technologies: ['SQLAlchemy ORM', 'SQLite', 'Redis'],
    responsibilities: ['数据存储', '数据查询', '数据备份', '事务管理'],
  },
  {
    id: 'layer6',
    name: 'Layer 6: 基础设施抽象层',
    icon: Shield,
    color: 'yellow',
    description: '提供基础设施的抽象和标准化',
    components: ['配置管理抽象', '日志系统抽象', '监控抽象', '告警抽象'],
    technologies: ['配置中心', '结构化日志', 'Prometheus'],
    responsibilities: ['配置管理', '日志记录', '指标收集', '告警通知'],
  },
  {
    id: 'layer7',
    name: 'Layer 7: 基础工具层',
    icon: Layers,
    color: 'orange',
    description: '提供基础工具和公共组件支持',
    components: ['缓存管理器(LRU/LFU)', '并发任务池', '批处理管理器', '依赖注入容器'],
    technologies: ['异步编程', '连接池', '断路器模式'],
    responsibilities: ['性能优化', '资源管理', '错误处理', '工具支持'],
  },
  {
    id: 'layer8',
    name: 'Layer 8: 测试验证层',
    icon: TestTube,
    color: 'red',
    description: '保证系统质量和可靠性',
    components: ['单元测试', '集成测试', 'E2E测试', '混沌工程测试'],
    technologies: ['pytest', '模拟测试', '故障注入'],
    responsibilities: ['质量保证', '回归测试', '性能测试', '混沌测试'],
  },
]

export default function Architecture() {
  const mermaidRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (mermaidRef.current) {
      mermaidRef.current.innerHTML = ''
    }

    const diagram = `
    graph TB
      subgraph L1["Layer 1: 接口呈现层"]
        L1A["命令行接口"]
        L1B["Web API"]
        L1C["WebSocket"]
      end

      subgraph L2["Layer 2: 编排协调层"]
        L2A["任务编排器"]
        L2B["系统控制器"]
      end

      subgraph L3["Layer 3: 业务服务层"]
        L3A["任务管理服务"]
        L3B["进化引擎"]
        L3C["策略优化"]
      end

      subgraph L4["Layer 4: 领域模型层"]
        L4A["任务实体"]
        L4B["Agent实体"]
      end

      subgraph L5["Layer 5: 数据访问层"]
        L5A["任务仓库"]
        L5B["知识库"]
      end

      subgraph L6["Layer 6: 基础设施层"]
        L6A["配置管理"]
        L6B["日志系统"]
      end

      subgraph L7["Layer 7: 基础工具层"]
        L7A["缓存管理"]
        L7B["并发池"]
      end

      subgraph L8["Layer 8: 测试验证层"]
        L8A["单元测试"]
        L8B["集成测试"]
      end

      L1A --> L2A
      L1B --> L2A
      L1C --> L2A
      L2A --> L3A
      L2A --> L3B
      L3A --> L4A
      L3B --> L4A
      L3A --> L5A
      L3B --> L5B
      L5A --> L6A
      L3A --> L7A
      L3B --> L7A
      L8A --> L7A
    `

    mermaid.render('architectureDiagram', diagram).then((svg) => {
      if (mermaidRef.current) {
        mermaidRef.current.innerHTML = svg
      }
    })
  }, [])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">8层架构可视化</h2>
          <p className="text-slate-400">展示Agent永续自进化系统的完整架构层次</p>
        </div>
      </div>

      {/* Architecture Diagram */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-1">系统架构图</h3>
          <p className="text-sm text-slate-400">各层之间的依赖关系和数据流向</p>
        </div>
        <div className="flex justify-center" ref={mermaidRef} />
      </div>

      {/* Layer Cards */}
      <div className="space-y-6">
        <h3 className="text-2xl font-bold text-white">各层详细说明</h3>
        {layers.map((layer) => (
          <div
            key={layer.id}
            className={`bg-slate-800/50 border border-${layer.color}-500/30 rounded-xl p-6 backdrop-blur-sm hover:border-${layer.color}-500/50 transition-all`}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className={`w-12 h-12 bg-${layer.color}-500/20 border border-${layer.color}-500/30 rounded-lg flex items-center justify-center flex-shrink-0`}>
                <layer.icon className={`w-6 h-6 text-${layer.color}-400`} />
              </div>
              <div className="flex-1">
                <h4 className={`text-xl font-semibold text-${layer.color}-400 mb-2`}>{layer.name}</h4>
                <p className="text-slate-300">{layer.description}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-slate-400 mb-2">核心组件</div>
                <div className="space-y-1">
                  {layer.components.map((comp, idx) => (
                    <div key={idx} className="text-sm text-slate-300 flex items-center">
                      <ChevronRight className="w-4 h-4 text-slate-500 mr-1" />
                      {comp}
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-slate-400 mb-2">技术栈</div>
                <div className="flex flex-wrap gap-2">
                  {layer.technologies.map((tech, idx) => (
                    <span
                      key={idx}
                      className={`px-2 py-1 bg-${layer.color}-500/20 text-${layer.color}-400 text-xs rounded`}
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-slate-400 mb-2">主要职责</div>
                <div className="space-y-1">
                  {layer.responsibilities.map((resp, idx) => (
                    <div key={idx} className="text-sm text-slate-300 flex items-center">
                      <ChevronRight className="w-4 h-4 text-slate-500 mr-1" />
                      {resp}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
