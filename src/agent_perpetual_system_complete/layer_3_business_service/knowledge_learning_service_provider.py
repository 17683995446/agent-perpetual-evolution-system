"""
Knowledge Learning Service Provider - 知识学习服务提供者（6个单词）

负责成功案例提取、失败模式识别、模式库更新。
"""

import asyncio
import hashlib
import json
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from ..layer_6_infrastructure_abstraction.structured_logging_abstraction import get_structured_logger


class OutcomeCategory(str, Enum):
    """
    结果分类
    """
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class PatternType(str, Enum):
    """
    模式类型
    """
    BEST_PRACTICE = "best_practice"
    FAILURE_PATTERN = "failure_pattern"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"


@dataclass
class CaseStudy:
    """
    案例研究
    """
    case_id: str
    outcome: OutcomeCategory
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    patterns: List[str] = field(default_factory=list)


@dataclass
class Pattern:
    """
    模式
    """
    pattern_id: str
    pattern_type: PatternType
    description: str
    features: Dict[str, Any]
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KnowledgeBase:
    """
    知识库
    """
    patterns: Dict[str, Pattern] = field(default_factory=dict)
    case_studies: Dict[str, CaseStudy] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)


@dataclass
class Recommendation:
    """
    建议
    """
    pattern_id: str
    pattern_type: PatternType
    recommendation_text: str
    confidence: float
    applicable_features: List[str]


class KnowledgeLearningServiceProvider:
    """
    知识学习服务提供者

    核心职责：
    1. 成功案例提取和分析
    2. 失败模式识别和学习
    3. 模式库更新和维护
    4. 智能推荐和建议
    5. 特征重要性分析
    """

    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBase] = None,
    ):
        self.logger = get_structured_logger(__name__)

        self._kb = knowledge_base or KnowledgeBase()
        self._learning_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._case_buffer: List[CaseStudy] = []
        self._buffer_size = 100
        self._learning_interval_seconds = 300

    async def start(self) -> None:
        """
        启动知识学习服务
        """
        if self._is_running:
            self.logger.warning("knowledge_learning_service_already_running")
            return

        self.logger.info("starting_knowledge_learning_service")
        self._is_running = True
        self._learning_task = asyncio.create_task(self._learning_loop())

        self.logger.info("knowledge_learning_service_started")

    async def stop(self) -> None:
        """
        停止知识学习服务
        """
        if not self._is_running:
            self.logger.warning("knowledge_learning_service_not_running")
            return

        self.logger.info("stopping_knowledge_learning_service")
        self._is_running = False

        if self._learning_task:
            self._learning_task.cancel()
            try:
                await self._learning_task
            except asyncio.CancelledError:
                pass

        # 处理剩余的案例
        if self._case_buffer:
            await self._process_buffer()

        self.logger.info("knowledge_learning_service_stopped")

    async def record_case(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        outcome: OutcomeCategory,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        记录案例

        Args:
            input_data: 输入数据
            output_data: 输出数据
            outcome: 结果类别
            metadata: 元数据

        Returns:
            案例ID
        """
        case_id = self._generate_case_id(input_data, output_data)

        case = CaseStudy(
            case_id=case_id,
            outcome=outcome,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        self._case_buffer.append(case)

        if len(self._case_buffer) >= self._buffer_size:
            await self._process_buffer()

        self.logger.debug(
            "case_recorded",
            case_id=case_id,
            outcome=outcome,
        )

        return case_id

    async def extract_patterns(
        self,
        case_id: str,
    ) -> List[Pattern]:
        """
        从案例中提取模式

        Args:
            case_id: 案例ID

        Returns:
            提取的模式列表
        """
        case = self._kb.case_studies.get(case_id)
        if not case:
            self.logger.warning("case_not_found", case_id=case_id)
            return []

        features = self._extract_features(case)
        patterns = []

        # 基于特征创建模式
        if features:
            pattern_id = self._generate_pattern_id(features)

            if pattern_id not in self._kb.patterns:
                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type=PatternType.OPTIMIZATION_OPPORTUNITY
                    if case.outcome == OutcomeCategory.SUCCESS
                    else PatternType.FAILURE_PATTERN,
                    description=f"Pattern from case {case_id}",
                    features=features,
                    created_at=datetime.utcnow(),
                    last_updated_at=datetime.utcnow(),
                )
                self._kb.patterns[pattern_id] = pattern
                patterns.append(pattern)

                self.logger.info("new_pattern_extracted", pattern_id=pattern_id)
            else:
                # 更新现有模式
                pattern = self._kb.patterns[pattern_id]
                if case.outcome == OutcomeCategory.SUCCESS:
                    pattern.success_count += 1
                else:
                    pattern.failure_count += 1
                pattern.confidence = self._calculate_confidence(pattern)
                pattern.last_updated_at = datetime.utcnow()

        return patterns

    async def get_recommendations(
        self,
        input_data: Dict[str, Any],
        top_k: int = 5,
    ) -> List[Recommendation]:
        """
        获取建议

        Args:
            input_data: 输入数据
            top_k: 返回前K个建议

        Returns:
            建议列表
        """
        input_features = self._extract_features_from_data(input_data)

        recommendations = []
        for pattern in self._kb.patterns.values():
            similarity = self._calculate_similarity(input_features, pattern.features)

            if similarity > 0.5:
                recommendations.append(
                    Recommendation(
                        pattern_id=pattern.pattern_id,
                        pattern_type=pattern.pattern_type,
                        recommendation_text=self._generate_recommendation_text(pattern),
                        confidence=pattern.confidence * similarity,
                        applicable_features=list(input_features.keys()),
                    )
                )

        # 按置信度排序并返回前K个
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:top_k]

    async def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        获取模式统计

        Returns:
            统计信息
        """
        total_patterns = len(self._kb.patterns)
        success_patterns = sum(
            1 for p in self._kb.patterns.values()
            if p.pattern_type == PatternType.SUCCESS
        )
        failure_patterns = sum(
            1 for p in self._kb.patterns.values()
            if p.pattern_type == PatternType.FAILURE_PATTERN
        )
        avg_confidence = sum(p.confidence for p in self._kb.patterns.values()) / total_patterns if total_patterns > 0 else 0.0

        return {
            "total_patterns": total_patterns,
            "success_patterns": success_patterns,
            "failure_patterns": failure_patterns,
            "optimization_patterns": total_patterns - success_patterns - failure_patterns,
            "avg_confidence": avg_confidence,
            "total_case_studies": len(self._kb.case_studies),
        }

    async def _learning_loop(self) -> None:
        """
        学习循环
        """
        self.logger.info("learning_loop_started")

        while self._is_running:
            try:
                await asyncio.sleep(self._learning_interval_seconds)

                if self._case_buffer:
                    await self._process_buffer()

                await self._update_feature_importance()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("learning_loop_error", error=str(e))

        self.logger.info("learning_loop_stopped")

    async def _process_buffer(self) -> None:
        """
        处理缓冲中的案例
        """
        if not self._case_buffer:
            return

        self.logger.info(
            "processing_case_buffer",
            count=len(self._case_buffer),
        )

        for case in self._case_buffer:
            self._kb.case_studies[case.case_id] = case
            await self.extract_patterns(case.case_id)

        self._case_buffer = []

    async def _update_feature_importance(self) -> None:
        """
        更新特征重要性
        """
        # 简单的特征重要性计算
        feature_counts = defaultdict(int)
        feature_success = defaultdict(int)

        for pattern in self._kb.patterns.values():
            for feature in pattern.features:
                feature_counts[feature] += 1
                if pattern.pattern_type == PatternType.SUCCESS:
                    feature_success[feature] += 1

        for feature, count in feature_counts.items():
            self._kb.feature_importance[feature] = (
                feature_success.get(feature, 0) / count
            )

    def _extract_features(self, case: CaseStudy) -> Dict[str, Any]:
        """
        从案例中提取特征

        Args:
            case: 案例

        Returns:
            特征字典
        """
        features = {}

        # 从输入数据提取
        for key, value in case.input_data.items():
            if isinstance(value, (str, int, float, bool)):
                features[f"input:{key}"] = value

        # 从元数据提取
        for key, value in case.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                features[f"meta:{key}"] = value

        return features

    def _extract_features_from_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从数据中提取特征

        Args:
            data: 数据

        Returns:
            特征字典
        """
        features = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                features[key] = value
        return features

    def _calculate_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any],
    ) -> float:
        """
        计算特征相似度

        Args:
            features1: 特征1
            features2: 特征2

        Returns:
            相似度（0-1）
        """
        common_keys = set(features1.keys()) & set(features2.keys())

        if not common_keys:
            return 0.0

        matches = sum(
            1 for key in common_keys
            if features1[key] == features2[key]
        )

        return matches / len(common_keys)

    def _calculate_confidence(self, pattern: Pattern) -> float:
        """
        计算模式置信度

        Args:
            pattern: 模式

        Returns:
            置信度
        """
        total = pattern.success_count + pattern.failure_count
        if total == 0:
            return 0.0

        if pattern.pattern_type == PatternType.SUCCESS:
            return pattern.success_count / total
        elif pattern.pattern_type == PatternType.FAILURE_PATTERN:
            return pattern.failure_count / total
        else:
            return 0.5

    def _generate_recommendation_text(self, pattern: Pattern) -> str:
        """
        生成建议文本

        Args:
            pattern: 模式

        Returns:
            建议文本
        """
        if pattern.pattern_type == PatternType.SUCCESS:
            return "This pattern is associated with successful outcomes. Consider applying similar strategies."
        elif pattern.pattern_type == PatternType.FAILURE_PATTERN:
            return "This pattern is associated with failures. Avoid this configuration."
        else:
            return "This pattern suggests an optimization opportunity."

    def _generate_case_id(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
    ) -> str:
        """
        生成案例ID

        Args:
            input_data: 输入数据
            output_data: 输出数据

        Returns:
            案例ID
        """
        combined = json.dumps({"input": input_data, "output": output_data}, sort_keys=True)
        return hashlib.md5(combined.encode()).hexdigest()

    def _generate_pattern_id(self, features: Dict[str, Any]) -> str:
        """
        生成模式ID

        Args:
            features: 特征

        Returns:
            模式ID
        """
        sorted_features = json.dumps(features, sort_keys=True)
        return hashlib.sha256(sorted_features.encode()).hexdigest()

    @property
    def is_running(self) -> bool:
        """
        是否正在运行
        """
        return self._is_running

    @property
    def knowledge_base(self) -> KnowledgeBase:
        """
        知识库
        """
        return self._kb
