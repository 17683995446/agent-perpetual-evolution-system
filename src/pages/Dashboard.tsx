import { Cpu, MemoryStick, Activity, Clock, CheckCircle, AlertCircle, TrendingUp, Zap } from 'lucide-react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const cpuData = {
  labels: ['0s', '10s', '20s', '30s', '40s', '50s', '60s'],
  datasets: [
    {
      label: 'CPU使用率',
      data: [35, 42, 38, 45, 40, 48, 42],
      borderColor: 'rgb(34, 211, 238)',
      backgroundColor: 'rgba(34, 211, 238, 0.1)',
      fill: true,
      tension: 0.4,
    },
  ],
}

const memoryData = {
  labels: ['0s', '10s', '20s', '30s', '40s', '50s', '60s'],
  datasets: [
    {
      label: '内存使用',
      data: [256, 280, 275, 290, 285, 300, 295],
      borderColor: 'rgb(168, 85, 247)',
      backgroundColor: 'rgba(168, 85, 247, 0.1)',
      fill: true,
      tension: 0.4,
    },
  ],
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(148, 163, 184, 0.1)',
      },
      ticks: {
        color: 'rgba(148, 163, 184, 0.8)',
      },
    },
    x: {
      grid: {
        color: 'rgba(148, 163, 184, 0.1)',
      },
      ticks: {
        color: 'rgba(148, 163, 184, 0.8)',
      },
    },
  },
}

export default function Dashboard() {
  const stats = [
    {
      title: 'CPU使用率',
      value: '42%',
      icon: Cpu,
      color: 'cyan',
      trend: '+7%',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/30',
    },
    {
      title: '内存使用',
      value: '295 MB',
      icon: MemoryStick,
      color: 'purple',
      trend: '+15%',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30',
    },
    {
      title: '活跃任务',
      value: '12',
      icon: Activity,
      color: 'green',
      trend: '+3',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
    },
    {
      title: '运行时间',
      value: '2小时15分',
      icon: Clock,
      color: 'blue',
      trend: '稳定',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
    },
  ]

  const agents = [
    { name: 'ContentAgent-1', status: 'running', tasks: 12, success: 98 },
    { name: 'CodeAgent-1', status: 'running', tasks: 9, success: 100 },
    { name: 'ProjectAgent-1', status: 'running', tasks: 9, success: 100 },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">系统仪表盘</h2>
          <p className="text-slate-400">实时监控Agent永续自进化系统的运行状态</p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-green-500/20 text-green-400 border border-green-500/30">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
            系统健康
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div
            key={stat.title}
            className={`${stat.bgColor} border ${stat.borderColor} rounded-xl p-6 backdrop-blur-sm hover:scale-105 transition-transform duration-200`}
          >
            <div className="flex items-center justify-between mb-4">
              <stat.icon className={`w-8 h-8 text-${stat.color}-400`} />
              <span className={`text-xs font-medium px-2 py-1 rounded-full bg-${stat.color}-500/20 text-${stat.color}-400`}>
                {stat.trend}
              </span>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
            <div className="text-sm text-slate-400">{stat.title}</div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Chart */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">CPU使用率趋势</h3>
              <p className="text-sm text-slate-400 mt-1">最近60秒数据</p>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-cyan-400" />
              <span className="text-cyan-400 font-medium">42%</span>
            </div>
          </div>
          <div className="h-64">
            <Line data={cpuData} options={chartOptions} />
          </div>
        </div>

        {/* Memory Chart */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">内存使用趋势</h3>
              <p className="text-sm text-slate-400 mt-1">最近60秒数据</p>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              <span className="text-purple-400 font-medium">295 MB</span>
            </div>
          </div>
          <div className="h-64">
            <Line data={memoryData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Agents Status */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-1">Agent状态</h3>
          <p className="text-sm text-slate-400">多Agent协作运行状态监控</p>
        </div>
        <div className="space-y-4">
          {agents.map((agent) => (
            <div
              key={agent.name}
              className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4 hover:border-cyan-500/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
                    <Activity className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-white font-medium">{agent.name}</div>
                    <div className="text-xs text-slate-400">多Agent协作系统</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-sm text-white font-medium">{agent.tasks} 任务</div>
                    <div className="text-xs text-slate-400">已完成</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-green-400 font-medium">{agent.success}%</div>
                    <div className="text-xs text-slate-400">成功率</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {agent.status === 'running' ? (
                      <>
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <span className="text-sm text-green-400">运行中</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-5 h-5 text-red-400" />
                        <span className="text-sm text-red-400">异常</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${agent.success}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-xl p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">快速操作</h3>
            <p className="text-sm text-slate-400">常用的系统管理和监控功能</p>
          </div>
          <div className="flex space-x-3">
            <button className="px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors">
              查看详细监控
            </button>
            <button className="px-4 py-2 bg-purple-500/20 border border-purple-500/30 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors">
              生成报告
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
