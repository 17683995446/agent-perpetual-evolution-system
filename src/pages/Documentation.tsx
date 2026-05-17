import { useState } from 'react'
import { BookOpen, Code, Server, Shield, Rocket, Layers, FileText, ChevronRight, ExternalLink } from 'lucide-react'

const docs = [
  {
    id: 'introduction',
    title: '系统介绍',
    icon: BookOpen,
    color: 'cyan',
    content: {
      overview: 'Agent永续自进化系统是一个企业级的AI Agent自进化运行平台，集成混沌工程、压力测试、故障恢复、持续改进等能力。',
      features: [
        '多Agent协作：支持多个AI Agent协同工作，智能分配任务',
        '自动进化：根据系统表现自动优化策略，持续改进',
        '混沌工程：主动注入故障，验证系统韧性',
        '压力测试：支持高并发、大数据量测试',
        '故障恢复：自动检测和恢复，确保服务连续性',
      ],
      useCases: [
        '电商大促：处理双十一等流量峰值',
        '金融系统：7x24小时高可用运行',
        '微服务架构：分布式系统协调',
        'AI应用平台：智能任务执行',
      ],
    },
  },
  {
    id: 'architecture',
    title: '架构设计',
    icon: Layers,
    color: 'purple',
    content: {
      layers: [
        { name: 'Layer 1', desc: '接口呈现层', components: 'CLI、Web API、WebSocket' },
        { name: 'Layer 2', desc: '编排协调层', components: '任务编排器、系统控制器' },
        { name: 'Layer 3', desc: '业务服务层', components: '任务管理、进化引擎、策略优化' },
        { name: 'Layer 4', desc: '领域模型层', components: '任务实体、Agent实体' },
        { name: 'Layer 5', desc: '数据访问层', components: '任务仓库、知识库' },
        { name: 'Layer 6', desc: '基础设施层', components: '配置管理、日志系统' },
        { name: 'Layer 7', desc: '基础工具层', components: '缓存管理、并发池、批处理' },
        { name: 'Layer 8', desc: '测试验证层', components: '单元测试、集成测试、E2E测试' },
      ],
      patterns: [
        '依赖注入：提高模块可测试性',
        '事件驱动：松耦合、高扩展',
        '断路器模式：防止故障蔓延',
        '缓存策略：LRU/LFU多级缓存',
      ],
    },
  },
  {
    id: 'api',
    title: 'API文档',
    icon: Code,
    color: 'blue',
    content: {
      endpoints: [
        { method: 'GET', path: '/api/v1/system/status', desc: '获取系统状态' },
        { method: 'GET', path: '/api/v1/system/metrics', desc: '获取系统指标' },
        { method: 'GET', path: '/api/v1/tasks', desc: '列出任务' },
        { method: 'POST', path: '/api/v1/tasks/submit', desc: '提交任务' },
        { method: 'GET', path: '/api/v1/evolution/dashboard', desc: '进化仪表盘' },
        { method: 'GET', path: '/api/v1/memory/status', desc: '内存状态' },
        { method: 'GET', path: '/health', desc: '健康检查' },
        { method: 'GET', path: '/metrics', desc: 'Prometheus指标' },
      ],
      examples: {
        submitTask: {
          request: 'POST /api/v1/tasks/submit',
          body: {
            content: { task: '执行数据分析' },
            priority: 'high',
            timeout_seconds: 300,
          },
        },
        getStatus: {
          request: 'GET /api/v1/system/status',
          response: {
            status: 'running',
            evolution_stage: 'learning',
            uptime_seconds: 3600,
            health_status: true,
          },
        },
      },
    },
  },
  {
    id: 'deployment',
    title: '部署指南',
    icon: Rocket,
    color: 'green',
    content: {
      requirements: {
        hardware: ['CPU: 4核以上', '内存: 8GB以上', '磁盘: 50GB以上'],
        software: ['Python 3.10+', 'Node.js 18+', 'SQLite 3.x'],
        network: ['需要访问硅基流动API', '端口: 3001 (API), 5173 (前端)'],
      },
      steps: [
        '克隆代码仓库',
        '安装依赖：pip install -r requirements.txt',
        '配置API密钥：export SILICONFLOW_API_KEY=your_key',
        '初始化数据库：python init_db.py',
        '启动后端服务：python api_server.py',
        '启动前端：npm run dev',
      ],
      config: {
        api_key: '硅基流动API密钥（必需）',
        api_base_url: 'API基础URL（可选，默认使用硅基流动）',
        max_workers: '最大并发数（默认4）',
        cache_enabled: '是否启用缓存（默认true）',
      },
    },
  },
  {
    id: 'security',
    title: '安全建议',
    icon: Shield,
    color: 'red',
    content: {
      authentication: [
        'API密钥定期轮换',
        '使用环境变量存储敏感信息',
        '生产环境启用JWT认证',
      ],
      dataProtection: [
        '敏感数据加密存储',
        '日志脱敏处理',
        '数据库备份加密',
      ],
      networkSecurity: [
        '配置CORS白名单',
        '请求限流防止DDoS',
        'SQL注入防护',
      ],
      monitoring: [
        '实时监控异常访问',
        '安全事件告警',
        '定期安全审计',
      ],
    },
  },
]

export default function Documentation() {
  const [activeDoc, setActiveDoc] = useState('introduction')

  const currentDoc = docs.find((doc) => doc.id === activeDoc) || docs[0]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">技术文档中心</h2>
          <p className="text-slate-400">完整的技术文档、最佳实践和部署指南</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm sticky top-24">
            <h3 className="text-lg font-semibold text-white mb-4">文档目录</h3>
            <div className="space-y-2">
              {docs.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => setActiveDoc(doc.id)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                    activeDoc === doc.id
                      ? `bg-${doc.color}-500/20 border-${doc.color}-500/50 text-${doc.color}-400`
                      : 'bg-slate-900/50 border-slate-700/50 text-slate-300 hover:border-slate-600'
                  }`}
                >
                  <doc.icon className={`w-5 h-5`} />
                  <span className="font-medium">{doc.title}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Doc Header */}
          <div
            className={`bg-slate-800/50 border border-${currentDoc.color}-500/30 rounded-xl p-6 backdrop-blur-sm`}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div
                className={`w-12 h-12 bg-${currentDoc.color}-500/20 border border-${currentDoc.color}-500/30 rounded-lg flex items-center justify-center`}
              >
                <currentDoc.icon className={`w-6 h-6 text-${currentDoc.color}-400`} />
              </div>
              <div>
                <h3 className={`text-2xl font-semibold text-${currentDoc.color}-400`}>
                  {currentDoc.title}
                </h3>
              </div>
            </div>
          </div>

          {/* Doc Content */}
          {currentDoc.id === 'introduction' && (
            <div className="space-y-6">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-3">系统概述</h4>
                <p className="text-slate-300 leading-relaxed">{currentDoc.content.overview}</p>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">核心特性</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentDoc.content.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <ChevronRight className="w-4 h-4 text-cyan-400" />
                      </div>
                      <span className="text-slate-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">适用场景</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentDoc.content.useCases.map((useCase, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50"
                    >
                      <span className="text-slate-300">{useCase}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentDoc.id === 'architecture' && (
            <div className="space-y-6">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">8层架构详解</h4>
                <div className="space-y-3">
                  {currentDoc.content.layers.map((layer, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50 flex items-center justify-between"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-16 h-8 bg-purple-500/20 rounded flex items-center justify-center text-sm font-medium text-purple-400">
                          {layer.name}
                        </div>
                        <div>
                          <div className="text-white font-medium">{layer.desc}</div>
                          <div className="text-xs text-slate-400">{layer.components}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">设计模式</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentDoc.content.patterns.map((pattern, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50"
                    >
                      <span className="text-slate-300">{pattern}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentDoc.id === 'api' && (
            <div className="space-y-6">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">API端点</h4>
                <div className="space-y-2">
                  {currentDoc.content.endpoints.map((endpoint, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 flex items-center space-x-3"
                    >
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          endpoint.method === 'GET'
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}
                      >
                        {endpoint.method}
                      </span>
                      <code className="text-sm text-cyan-400 flex-1">{endpoint.path}</code>
                      <span className="text-sm text-slate-400">{endpoint.desc}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">使用示例</h4>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-cyan-400 mb-2">提交任务</div>
                    <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm">
                      <div className="text-slate-500 mb-2">// POST /api/v1/tasks/submit</div>
                      <div className="text-slate-300">
                        {JSON.stringify(currentDoc.content.examples.submitTask.body, null, 2)}
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-cyan-400 mb-2">获取状态</div>
                    <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm">
                      <div className="text-slate-500 mb-2">// GET /api/v1/system/status</div>
                      <div className="text-slate-300">
                        {JSON.stringify(currentDoc.content.examples.getStatus.response, null, 2)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentDoc.id === 'deployment' && (
            <div className="space-y-6">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">环境要求</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <div className="text-sm font-medium text-green-400 mb-2">硬件要求</div>
                    <div className="space-y-1 text-sm text-slate-300">
                      {currentDoc.content.requirements.hardware.map((req, idx) => (
                        <div key={idx}>{req}</div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <div className="text-sm font-medium text-green-400 mb-2">软件要求</div>
                    <div className="space-y-1 text-sm text-slate-300">
                      {currentDoc.content.requirements.software.map((req, idx) => (
                        <div key={idx}>{req}</div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <div className="text-sm font-medium text-green-400 mb-2">网络要求</div>
                    <div className="space-y-1 text-sm text-slate-300">
                      {currentDoc.content.requirements.network.map((req, idx) => (
                        <div key={idx}>{req}</div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">部署步骤</h4>
                <div className="space-y-2">
                  {currentDoc.content.steps.map((step, idx) => (
                    <div key={idx} className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-xs text-green-400">
                        {idx + 1}
                      </div>
                      <code className="text-sm text-slate-300">{step}</code>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-4">配置项说明</h4>
                <div className="space-y-3">
                  {Object.entries(currentDoc.content.config).map(([key, value]) => (
                    <div
                      key={key}
                      className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between"
                    >
                      <code className="text-sm text-cyan-400">{key}</code>
                      <span className="text-sm text-slate-400">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentDoc.id === 'security' && (
            <div className="space-y-6">
              {Object.entries(currentDoc.content).map(([category, items]) => (
                <div
                  key={category}
                  className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
                >
                  <h4 className="text-lg font-semibold text-red-400 mb-4 capitalize">
                    {category === 'authentication' && '认证授权'}
                    {category === 'dataProtection' && '数据保护'}
                    {category === 'networkSecurity' && '网络安全'}
                    {category === 'monitoring' && '监控告警'}
                  </h4>
                  <div className="space-y-2">
                    {(items as string[]).map((item, idx) => (
                      <div key={idx} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-slate-300">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
