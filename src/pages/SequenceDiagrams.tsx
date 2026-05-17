import { useEffect, useRef, useState } from 'react'
import { Activity, Clock, MessageSquare, ArrowRight, RefreshCw, Play, Pause } from 'lucide-react'
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

const sequenceDiagrams = [
  {
    id: 'task-execution-sequence',
    title: '任务执行时序图',
    description: '展示任务从提交到完成的完整时序关系',
    code: `
sequenceDiagram
    participant Client as 客户端
    participant API as API接口
    participant Orch as 任务编排器
    participant Pool as Agent池
    participant Cache as 缓存管理
    participant DB as 数据库
    
    Client->>API: 提交任务请求
    API->>API: 参数验证
    API->>Orch: 创建任务
    Orch->>DB: 保存任务状态
    DB-->>Orch: 确认保存
    
    Orch->>Pool: 分配Agent
    Pool->>Cache: 检查缓存
    Cache-->>Pool: 缓存检查结果
    
    alt 缓存命中
        Pool-->>Orch: 返回缓存结果
    else 缓存未命中
        Pool->>Pool: 执行任务逻辑
        Pool->>Cache: 更新缓存
        Pool-->>Orch: 返回执行结果
    end
    
    Orch->>DB: 更新任务状态
    DB-->>Orch: 确认更新
    Orch-->>API: 返回结果
    API-->>Client: 返回任务结果
    `,
  },
  {
    id: 'evolution-engine-sequence',
    title: '进化引擎时序图',
    description: '展示进化引擎的监控、分析、优化过程',
    code: `
sequenceDiagram
    participant Monitor as 监控系统
    participant Engine as 进化引擎
    participant ML as 机器学习
    participant Storage as 存储层
    participant Optimizer as 优化器
    
    loop 持续监控
        Monitor->>Monitor: 采集指标
        Monitor->>Engine: 发送监控数据
        Engine->>Engine: 数据预处理
    end
    
    Engine->>ML: 请求模式识别
    ML-->>Engine: 返回识别结果
    
    Engine->>Engine: 根因分析
    Engine->>Optimizer: 请求优化建议
    
    alt 存在优化空间
        Optimizer-->>Engine: 返回优化方案
        Engine->>Engine: 评估风险
        alt 风险可接受
            Engine->>Optimizer: 实施优化
            Optimizer-->>Engine: 确认完成
            Engine->>Storage: 记录改进
        else 风险过高
            Engine->>Engine: 放弃本次优化
        end
    else 无需优化
        Optimizer-->>Engine: 保持现状
    end
    
    Engine-->>Monitor: 更新状态
    `,
  },
  {
    id: 'fault-recovery-sequence',
    title: '故障恢复时序图',
    description: '展示故障检测、断路、恢复的时序过程',
    code: `
sequenceDiagram
    participant Client as 客户端
    participant LB as 负载均衡
    participant CB as 断路器
    participant Service as 服务实例
    participant Backup as 备用实例
    participant Monitor as 监控服务
    
    Client->>LB: 发起请求
    LB->>CB: 转发请求
    
    alt 断路器关闭
        CB->>Service: 转发请求
        Service-->>CB: 返回结果
        
        alt 服务正常
            CB-->>LB: 返回结果
            LB-->>Client: 返回响应
        else 服务异常
            CB->>CB: 记录失败
            CB->>Monitor: 上报故障
            Monitor->>Monitor: 触发告警
            
            alt 失败次数超限
                CB->>CB: 打开断路器
                CB-->>Client: 返回降级响应
            else 未超限
                CB-->>LB: 返回错误
                LB-->>Client: 返回错误
            end
        end
    else 断路器打开
        CB-->>Client: 快速返回降级结果
    end
    
    loop 定期探测
        CB->>Backup: 健康检查
        Backup-->>CB: 检查结果
        
        alt 备用实例健康
            CB->>CB: 半开断路器
            CB->>Backup: 测试请求
            alt 测试成功
                CB->>CB: 关闭断路器
                CB->>Service: 恢复正常
            else 测试失败
                CB->>CB: 重新打开断路器
            end
        end
    end
    `,
  },
]

export default function SequenceDiagrams() {
  const [activeDiagram, setActiveDiagram] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const mermaidRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const diagram = sequenceDiagrams[activeDiagram]
    if (mermaidRef.current) {
      mermaidRef.current.innerHTML = ''
    }

    mermaid.render(`sequence-${diagram.id}`, diagram.code).then((svg) => {
      if (mermaidRef.current) {
        mermaidRef.current.innerHTML = svg
      }
    })
  }, [activeDiagram])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">时序图可视化</h2>
          <p className="text-slate-400">展示系统组件之间的交互时序和消息传递</p>
        </div>
      </div>

      {/* Diagram Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {sequenceDiagrams.map((diagram, index) => (
          <button
            key={diagram.id}
            onClick={() => setActiveDiagram(index)}
            className={`p-4 rounded-xl border transition-all ${
              activeDiagram === index
                ? 'bg-purple-500/20 border-purple-500/50 text-purple-400'
                : 'bg-slate-800/50 border-slate-700/50 text-slate-300 hover:border-purple-500/30'
            }`}
          >
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="w-5 h-5" />
              <span className="font-medium">{diagram.title}</span>
            </div>
            <div className="text-sm">{diagram.description}</div>
          </button>
        ))}
      </div>

      {/* Main Diagram Display */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-1">
              {sequenceDiagrams[activeDiagram].title}
            </h3>
            <p className="text-sm text-slate-400">
              {sequenceDiagrams[activeDiagram].description}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30 text-purple-400 hover:bg-purple-500/30 transition-colors"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setActiveDiagram(activeDiagram)}
              className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div ref={mermaidRef} className="flex justify-center overflow-auto" />
      </div>

      {/* Interaction Details */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 className="text-lg font-semibold text-white mb-4">交互说明</h3>
        <div className="space-y-4">
          {activeDiagram === 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">核心交互步骤</div>
                <div className="space-y-2 text-sm text-slate-300">
                  <div className="flex items-start space-x-2">
                    <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-xs text-purple-400">1</div>
                    <div>客户端提交任务请求到API接口</div>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-xs text-purple-400">2</div>
                    <div>API进行参数验证，创建任务</div>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-xs text-purple-400">3</div>
                    <div>任务编排器分配Agent处理任务</div>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-xs text-purple-400">4</div>
                    <div>缓存命中则直接返回，否则执行任务</div>
                  </div>
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">性能优化点</div>
                <div className="space-y-2 text-sm text-slate-300">
                  <div className="flex items-center space-x-2">
                    <ArrowRight className="w-4 h-4 text-purple-400" />
                    <div>缓存机制减少重复计算</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ArrowRight className="w-4 h-4 text-purple-400" />
                    <div>异步处理提升响应速度</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ArrowRight className="w-4 h-4 text-purple-400" />
                    <div>智能Agent选择优化资源利用</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ArrowRight className="w-4 h-4 text-purple-400" />
                    <div>任务状态持久化保证可靠性</div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {activeDiagram === 1 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">持续监控</div>
                <div className="text-sm text-slate-300">
                  实时采集系统指标，包括CPU、内存、响应时间等数据，为进化提供数据基础。
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">智能分析</div>
                <div className="text-sm text-slate-300">
                  基于机器学习进行模式识别和根因分析，自动发现问题模式和优化机会。
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">自动优化</div>
                <div className="text-sm text-slate-300">
                  评估优化方案风险，实施安全改进，验证效果并固化成功经验。
                </div>
              </div>
            </div>
          )}
          {activeDiagram === 2 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">断路器模式</div>
                <div className="text-sm text-slate-300 mb-3">
                  当服务失败次数超过阈值时，断路器打开，快速返回降级响应，避免资源耗尽。
                </div>
                <div className="space-y-1 text-xs text-slate-400">
                  <div>• Closed（关闭）：正常处理请求</div>
                  <div>• Open（打开）：快速失败，不调用服务</div>
                  <div>• Half-Open（半开）：试探性恢复</div>
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm font-medium text-purple-400 mb-3">故障转移</div>
                <div className="text-sm text-slate-300 mb-3">
                  自动切换到备用实例，保证服务高可用，最小化故障影响。
                </div>
                <div className="space-y-1 text-xs text-slate-400">
                  <div>• 健康检查：定期探测实例状态</div>
                  <div>• 自动切换：故障实例自动下线</div>
                  <div>• 快速恢复：故障实例修复后重新加入</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 className="text-lg font-semibold text-white mb-4">图例说明</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-0.5 bg-cyan-500"></div>
            <span className="text-sm text-slate-300">同步消息</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-0.5 bg-cyan-500 border-dashed"></div>
            <span className="text-sm text-slate-300">异步消息</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-0.5 bg-purple-500"></div>
            <span className="text-sm text-slate-300">返回消息</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-0.5 bg-orange-500"></div>
            <span className="text-sm text-slate-300">循环消息</span>
          </div>
        </div>
      </div>
    </div>
  )
}
