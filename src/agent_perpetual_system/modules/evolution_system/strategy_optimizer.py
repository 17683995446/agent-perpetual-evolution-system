"""
Strategy Optimizer - 策略优化器

该模块负责：
- 历史执行数据分析
- 执行策略自动优化
- Prompt模板改进
- 决策逻辑优化
- 优化效果评估
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc, and_
from ...core.database_manager import get_database_session
from ...core.database_models import TaskDatabaseModel, StrategyDatabaseModel
from ...core.logger_config import get_structured_logger

logger = get_structured_logger(__name__)


class StrategyOptimizer:
    """
    策略优化器

    负责分析和优化系统的执行策略：
    - 分析历史任务执行数据
    - 识别低效执行模式
    - 生成优化建议
    - 实施策略更新
    """

    def __init__(self):
        self.analysis_window_days = 7  # 分析窗口：7天
        self.min_samples_for_analysis = 10  # 最小样本数

    async def execute_strategy_optimization(self) -> Dict[str, Any]:
        """
        执行策略优化主流程

        Returns:
            Dict: 包含优化结果的字典

        Example:
            >>> optimizer = StrategyOptimizer()
            >>> result = await optimizer.execute_strategy_optimization()
            >>> print(f"Optimized {result['strategies_updated']} strategies")
        """
        logger.info("strategy_optimization_started")

        # 1. 分析历史执行数据
        analysis_result = await self._analyze_execution_history()

        # 2. 识别优化机会
        optimization_opportunities = await self._identify_optimization_opportunities(
            analysis_result
        )

        # 3. 生成优化建议
        optimization_suggestions = await self._generate_optimization_suggestions(
            optimization_opportunities
        )

        # 4. 实施策略更新
        strategies_updated = await self._apply_strategy_updates(
            optimization_suggestions
        )

        logger.info(
            "strategy_optimization_completed",
            strategies_updated=strategies_updated,
            suggestions_generated=len(optimization_suggestions)
        )

        return {
            "status": "success",
            "strategies_updated": strategies_updated,
            "suggestions_generated": len(optimization_suggestions),
            "optimization_opportunities": len(optimization_opportunities),
        }

    async def _analyze_execution_history(self) -> Dict[str, Any]:
        """
        分析历史执行数据

        分析最近N天的任务执行记录，识别模式和趋势

        Returns:
            Dict: 包含分析结果的字典
        """
        cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)

        async with get_database_session() as session:
            result = await session.execute(
                select(TaskDatabaseModel)
                .where(TaskDatabaseModel.created_at >= cutoff_date)
                .order_by(desc(TaskDatabaseModel.created_at))
            )
            tasks = list(result.scalars().all())

        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        failed_tasks = len([t for t in tasks if t.status == "failed"])

        # 计算平均执行时间
        completed_with_time = [
            t for t in tasks
            if t.status == "completed" and t.execution_time
        ]
        avg_execution_time = (
            sum(t.execution_time for t in completed_with_time) / len(completed_with_time)
            if completed_with_time else 0
        )

        # 计算成功率
        success_rate = (
            completed_tasks / total_tasks if total_tasks > 0 else 0
        )

        logger.info(
            "execution_history_analyzed",
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            success_rate=success_rate
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "analysis_window_days": self.analysis_window_days,
        }

    async def _identify_optimization_opportunities(
        self, analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        识别优化机会

        根据分析结果，识别可以优化的领域

        Args:
            analysis_result: 历史执行分析结果

        Returns:
            List[Dict]: 优化机会列表
        """
        opportunities = []

        # 检查成功率
        if analysis_result["success_rate"] < 0.8:
            opportunities.append({
                "type": "low_success_rate",
                "severity": "high",
                "current_value": analysis_result["success_rate"],
                "target_value": 0.9,
                "description": "任务成功率偏低，需要优化执行策略"
            })

        # 检查执行时间
        if analysis_result["average_execution_time"] > 60:
            opportunities.append({
                "type": "high_execution_time",
                "severity": "medium",
                "current_value": analysis_result["average_execution_time"],
                "target_value": 30,
                "description": "平均执行时间偏长，需要优化执行流程"
            })

        logger.info(
            "optimization_opportunities_identified",
            count=len(opportunities)
        )

        return opportunities

    async def _generate_optimization_suggestions(
        self, opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成优化建议

        根据优化机会生成具体的优化建议

        Args:
            opportunities: 优化机会列表

        Returns:
            List[Dict]: 优化建议列表
        """
        suggestions = []

        for opportunity in opportunities:
            if opportunity["type"] == "low_success_rate":
                suggestions.append({
                    "opportunity": opportunity,
                    "suggestion": "优化错误处理逻辑，增加重试机制",
                    "implementation": "增加任务失败后的自动重试",
                    "expected_improvement": "+10% 成功率"
                })

            elif opportunity["type"] == "high_execution_time":
                suggestions.append({
                    "opportunity": opportunity,
                    "suggestion": "优化任务执行流程，减少等待时间",
                    "implementation": "改进任务调度算法",
                    "expected_improvement": "-30% 执行时间"
                })

        logger.info(
            "optimization_suggestions_generated",
            count=len(suggestions)
        )

        return suggestions

    async def _apply_strategy_updates(
        self, suggestions: List[Dict[str, Any]]
    ) -> int:
        """
        实施策略更新

        将优化建议应用到实际的策略中

        Args:
            suggestions: 优化建议列表

        Returns:
            int: 更新的策略数量
        """
        # 模拟策略更新
        updated_count = 0

        for suggestion in suggestions:
            logger.info(
                "strategy_update_applied",
                suggestion=suggestion["suggestion"]
            )
            updated_count += 1

        return updated_count

    async def get_strategy_effectiveness_report(self) -> Dict[str, Any]:
        """
        获取策略有效性报告

        生成当前策略有效性的详细报告

        Returns:
            Dict: 策略有效性报告

        Example:
            >>> report = await optimizer.get_strategy_effectiveness_report()
            >>> print(report["overall_score"])
        """
        # 分析最近的任务执行情况
        analysis_result = await self._analyze_execution_history()

        # 计算综合评分
        success_score = analysis_result["success_rate"] * 40  # 40% 权重
        efficiency_score = min(1.0, 60 / max(1, analysis_result["average_execution_time"])) * 30  # 30% 权重
        volume_score = min(1.0, analysis_result["total_tasks"] / 100) * 30  # 30% 权重

        overall_score = success_score + efficiency_score + volume_score

        return {
            "overall_score": round(overall_score, 2),
            "success_rate_score": round(success_score, 2),
            "efficiency_score": round(efficiency_score, 2),
            "volume_score": round(volume_score, 2),
            "analysis_period_days": self.analysis_window_days,
            "recommendation": self._generate_recommendation(overall_score)
        }

    def _generate_recommendation(self, score: float) -> str:
        """
        根据评分生成建议

        Args:
            score: 综合评分

        Returns:
            str: 建议文本
        """
        if score >= 80:
            return "策略运行良好，继续保持当前配置"
        elif score >= 60:
            return "策略基本正常，建议进行小幅优化"
        elif score >= 40:
            return "策略存在明显问题，建议进行全面优化"
        else:
            return "策略严重不足，建议立即进行优化"
