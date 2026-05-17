
"""
硅基流动API集成模块 - 基于OpenAI兼容协议的大语言模型接口
提供企业级的AI服务集成，支持进化引擎、任务优化、智能建议等功能
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.agent_perpetual_system_complete.layer_6_infrastructure_abstraction.structured_logging_abstraction import (
    get_structured_logger,
)

logger = get_structured_logger(__name__)


class SiliconFlowModel(str, Enum):
    """硅基流动支持的免费模型列表"""
    # DeepSeek系列
    DEEPSEEK_R1_DISTILL_32B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    DEEPSEEK_R1_DISTILL_14B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
    DEEPSEEK_R1_DISTILL_7B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    
    # Qwen系列
    QWEN_QWQ_32B = "Qwen/QwQ-32B"
    QWEN_QWEN3_30B_A3B_THINKING_2507 = "Qwen/Qwen3-30B-A3B-Thinking-2507"
    
    # GLM系列
    THUDM_GLM_Z1_32B_0414 = "THUDM/GLM-Z1-32B-0414"
    THUDM_GLM_4_1V_9B_THINKING = "THUDM/GLM-4.1V-9B-Thinking"
    
    # 默认模型
    DEFAULT = "Qwen/Qwen3-30B-A3B-Thinking-2507"


@dataclass
class SiliconFlowConfig:
    """硅基流动API配置"""
    api_key: str
    base_url: str = "https://api.siliconflow.cn/v1"
    model: SiliconFlowModel = SiliconFlowModel.DEFAULT
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


@dataclass
class SiliconFlowResponse:
    """硅基流动API响应封装"""
    success: bool = True
    content: Optional[str] = None
    error: Optional[str] = None
    response_time: float = 0.0
    token_usage: Optional[int] = None
    model: str = ""


class SiliconFlowClient:
    """
    硅基流动API客户端
    
    核心功能：
    - OpenAI兼容的API协议
    - 多种免费模型支持
    - 智能重试和错误处理
    - 任务优化和生成
    - 进化引擎支持
    """
    
    def __init__(self, config: SiliconFlowConfig):
        self.config = config
        self._client = None
        self._initialized = False
        logger.info("初始化硅基流动API客户端", model=config.model)
    
    async def initialize(self):
        """初始化OpenAI客户端"""
        try:
            from openai import AsyncOpenAI
            
            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
            self._initialized = True
            logger.info("硅基流动API客户端初始化成功")
            return True
            
        except Exception as e:
            logger.error("硅基流动API客户端初始化失败", error=str(e))
            return False
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[SiliconFlowModel] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -&gt; SiliconFlowResponse:
        """
        聊天补全API调用
        
        Args:
            messages: 消息历史列表
            model: 使用的模型（可选，默认使用配置的模型）
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            
        Returns:
            SiliconFlowResponse: API响应
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._client:
            return SiliconFlowResponse(
                success=False,
                error="客户端未初始化"
            )
        
        target_model = model.value if model else self.config.model.value
        target_temperature = temperature if temperature is not None else self.config.temperature
        target_max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        start_time = time.time()
        
        try:
            for attempt in range(self.config.max_retries):
                try:
                    response = await self._client.chat.completions.create(
                        model=target_model,
                        messages=messages,
                        temperature=target_temperature,
                        max_tokens=target_max_tokens,
                    )
                    
                    response_time = time.time() - start_time
                    
                    content = response.choices[0].message.content if response.choices else None
                    
                    token_usage = None
                    if hasattr(response, 'usage') and response.usage:
                        token_usage = response.usage.total_tokens
                    
                    return SiliconFlowResponse(
                        success=True,
                        content=content,
                        response_time=response_time,
                        token_usage=token_usage,
                        model=target_model
                    )
                    
                except Exception as e:
                    logger.warning(
                        "API调用失败，正在重试",
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    
                    if attempt &lt; self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay_seconds * (attempt + 1))
                    else:
                        raise
            
        except Exception as e:
            return SiliconFlowResponse(
                success=False,
                error=str(e),
                response_time=time.time() - start_time
            )


class TaskOptimizer:
    """
    任务优化器 - 基于硅基流动API的智能任务优化
    
    功能：
    - 任务执行策略优化
    - 工作流生成和优化
    - 错误分析和修复建议
    - 性能优化建议
    """
    
    def __init__(self, silicon_flow_client: SiliconFlowClient):
        self.client = silicon_flow_client
        self.logger = get_structured_logger(__name__)
    
    async def optimize_task_execution(
        self,
        task_description: str,
        execution_history: Optional[List[Dict[str, Any]]] = None,
    ) -&gt; Dict[str, Any]:
        """
        优化任务执行策略
        
        Args:
            task_description: 任务描述
            execution_history: 历史执行记录
            
        Returns:
            优化建议
        """
        system_prompt = """
你是一个专业的任务优化顾问，帮助优化任务执行策略。
请分析任务描述，提供：
1. 最佳执行流程
2. 可能的风险和应对措施
3. 性能优化建议
4. 资源分配建议

请以JSON格式输出结果，结构如下：
{
    "optimization_score": 0-100,
    "execution_flow": [...],
    "risk_mitigation": [...],
    "performance_tips": [...],
    "resource_allocation": {...}
}
        """.strip()
        
        user_prompt = f"""
任务描述：{task_description}

执行历史：
{json.dumps(execution_history or [], ensure_ascii=False, indent=2)}

请提供优化建议。
        """.strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        
        if response.success and response.content:
            try:
                result = json.loads(response.content)
                return result
            except Exception:
                return {"raw_response": response.content}
        else:
            return {"error": response.error}
    
    async def generate_workflow(
        self,
        goal: str,
        constraints: Optional[List[str]] = None,
    ) -&gt; Dict[str, Any]:
        """
        生成工作流
        
        Args:
            goal: 目标描述
            constraints: 约束条件
            
        Returns:
            工作流定义
        """
        system_prompt = """
你是一个工作流设计专家。请根据目标设计工作流。

请以JSON格式输出，结构如下：
{
    "workflow_name": "...",
    "nodes": [
        {
            "node_id": "...",
            "name": "...",
            "type": "ACTION|CONDITION|PARALLEL|LOOP",
            "config": {...},
            "dependencies": ["..."]
        }
    ],
    "entry_point": "...",
    "estimated_duration": "...",
    "success_probability": 0.0-1.0
}
        """.strip()
        
        user_prompt = f"""
目标：{goal}

约束条件：
{json.dumps(constraints or [], ensure_ascii=False, indent=2)}

请生成工作流。
        """.strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        
        if response.success and response.content:
            try:
                result = json.loads(response.content)
                return result
            except Exception:
                return {"raw_response": response.content}
        else:
            return {"error": response.error}


class EvolutionEngine:
    """
    AI驱动的进化引擎
    
    功能：
    - 系统性能分析
    - 进化策略生成
    - 智能建议
    - 模式识别
    """
    
    def __init__(self, silicon_flow_client: SiliconFlowClient):
        self.client = silicon_flow_client
        self.logger = get_structured_logger(__name__)
    
    async def analyze_performance(
        self,
        performance_data: Dict[str, Any],
    ) -&gt; Dict[str, Any]:
        """
        分析性能数据
        
        Args:
            performance_data: 性能数据
            
        Returns:
            分析结果
        """
        system_prompt = """
你是一个系统性能分析专家。请分析提供的性能数据，识别瓶颈和优化机会。

请以JSON格式输出：
{
    "overall_score": 0-100,
    "bottlenecks": [...],
    "optimization_suggestions": [...],
    "priority_levels": {...}
}
        """.strip()
        
        user_prompt = f"""
性能数据：
{json.dumps(performance_data, ensure_ascii=False, indent=2)}

请进行分析。
        """.strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        
        if response.success and response.content:
            try:
                result = json.loads(response.content)
                return result
            except Exception:
                return {"raw_response": response.content}
        else:
            return {"error": response.error}
    
    async def get_evolution_suggestions(
        self,
        current_state: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
    ) -&gt; List[Dict[str, Any]]:
        """
        获取进化建议
        
        Args:
            current_state: 当前状态
            historical_data: 历史数据
            
        Returns:
            建议列表
        """
        system_prompt = """
你是一个进化策略顾问。请根据系统状态提供进化建议。

请以JSON格式输出建议列表：
[
    {
        "suggestion_id": "...",
        "type": "PERFORMANCE|STABILITY|SCALABILITY|FEATURE",
        "description": "...",
        "priority": "HIGH|MEDIUM|LOW",
        "expected_improvement": "...",
        "implementation_cost": "...",
        "steps": [...]
    }
]
        """.strip()
        
        user_prompt = f"""
当前状态：
{json.dumps(current_state, ensure_ascii=False, indent=2)}

历史数据：
{json.dumps(historical_data or [], ensure_ascii=False, indent=2)}

请提供进化建议。
        """.strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        
        if response.success and response.content:
            try:
                result = json.loads(response.content)
                return result if isinstance(result, list) else [result]
            except Exception:
                return [{"raw_response": response.content}]
        else:
            return [{"error": response.error}]


class SiliconFlowService:
    """
    硅基流动综合服务
    
    统一管理API客户端、任务优化器和进化引擎
    """
    
    def __init__(self, api_key: str):
        self.config = SiliconFlowConfig(api_key=api_key)
        self.client = SiliconFlowClient(self.config)
        self.task_optimizer = TaskOptimizer(self.client)
        self.evolution_engine = EvolutionEngine(self.client)
        
        self._initialized = False
    
    async def initialize(self):
        """初始化服务"""
        if not self._initialized:
            await self.client.initialize()
            self._initialized = True
    
    async def simple_chat(self, message: str, system_prompt: Optional[str] = None) -&gt; str:
        """简单聊天接口"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat_completion(messages)
        
        if response.success and response.content:
            return response.content
        return f"错误: {response.error}"

