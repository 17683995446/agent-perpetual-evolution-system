"""
Knowledge Learner - 知识学习器

该模块负责：
- 从各种来源学习新知识
- 知识结构化处理
- 知识与能力映射
- 知识质量评估
- 知识更新和维护
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from ...core.database_manager import get_database_session
from ...core.database_models import KnowledgeDatabaseModel, MemoryDatabaseModel
from ...core.logger_config import get_structured_logger
from ...utils.id_generator import IDGenerator

logger = get_structured_logger(__name__)


class KnowledgeLearner:
    """
    知识学习器

    负责系统的知识获取和学习：
    - 从文档中提取知识
    - 从执行经验中提炼知识
    - 知识结构化和存储
    - 知识与能力关联
    """

    def __init__(self):
        self.learning_sources = [
            "task_execution",
            "manual_documents",
            "user_feedback",
            "best_practices"
        ]

    async def execute_knowledge_learning(self) -> Dict[str, Any]:
        """
        执行知识学习主流程

        Returns:
            Dict: 包含学习结果的字典

        Example:
            >>> learner = KnowledgeLearner()
            >>> result = await learner.execute_knowledge_learning()
            >>> print(f"Learned {result['knowledge_items_learned']} new items")
        """
        logger.info("knowledge_learning_started")

        total_learned = 0
        sources_processed = []

        # 1. 从任务执行中学习
        execution_knowledge = await self._learn_from_execution()
        total_learned += execution_knowledge["items_learned"]
        sources_processed.append("task_execution")

        # 2. 从最佳实践中学习
        best_practices_knowledge = await self._learn_from_best_practices()
        total_learned += best_practices_knowledge["items_learned"]
        sources_processed.append("best_practices")

        # 3. 结构化知识整理
        structured_knowledge = await self._structure_knowledge()
        total_learned += structured_knowledge["items_processed"]

        # 4. 知识与能力映射
        ability_mapping = await self._map_knowledge_to_abilities()
        total_learned += ability_mapping["items_mapped"]

        logger.info(
            "knowledge_learning_completed",
            total_learned=total_learned,
            sources_processed=len(sources_processed)
        )

        return {
            "status": "success",
            "knowledge_items_learned": total_learned,
            "sources_processed": sources_processed,
            "execution_knowledge": execution_knowledge,
            "best_practices_knowledge": best_practices_knowledge,
            "structured_knowledge": structured_knowledge,
        }

    async def _learn_from_execution(self) -> Dict[str, Any]:
        """
        从任务执行经验中学习

        分析成功执行的任务，提炼可复用的经验知识

        Returns:
            Dict: 包含学习结果的字典
        """
        # 模拟从执行经验中学习
        await asyncio.sleep(0.2)

        items_learned = 0

        # 这里可以实现实际的执行经验分析逻辑
        # 例如：分析成功任务的执行路径，提取最佳实践

        logger.info(
            "execution_knowledge_extracted",
            items_learned=items_learned
        )

        return {
            "source": "task_execution",
            "items_learned": items_learned,
            "description": "从任务执行经验中学习"
        }

    async def _learn_from_best_practices(self) -> Dict[str, Any]:
        """
        从最佳实践中学习

        从预设的最佳实践中学习通用知识

        Returns:
            Dict: 包含学习结果的字典
        """
        # 模拟从最佳实践中学习
        await asyncio.sleep(0.2)

        # 定义一些最佳实践
        best_practices = [
            {
                "type": "execution_pattern",
                "content": "先分析任务，再制定计划，最后执行",
                "applicability": "general"
            },
            {
                "type": "error_handling",
                "content": "遇到错误时，记录并重试",
                "applicability": "general"
            },
            {
                "type": "optimization",
                "content": "批量处理类似任务以提高效率",
                "applicability": "specific"
            }
        ]

        items_learned = len(best_practices)

        # 存储最佳实践知识
        for practice in best_practices:
            await self._store_knowledge(
                content=practice,
                source="best_practices",
                ability_tags=["execution", "optimization"]
            )

        logger.info(
            "best_practices_knowledge_extracted",
            items_learned=items_learned
        )

        return {
            "source": "best_practices",
            "items_learned": items_learned,
            "practices_stored": best_practices
        }

    async def _structure_knowledge(self) -> Dict[str, Any]:
        """
        结构化知识整理

        对已学习的知识进行结构化整理，便于检索和使用

        Returns:
            Dict: 包含整理结果的字典
        """
        async with get_database_session() as session:
            # 获取未结构化的知识
            result = await session.execute(
                select(KnowledgeDatabaseModel).where(
                    KnowledgeDatabaseModel.struct_result == None
                )
            )
            unstructured_knowledge = list(result.scalars().all())

        items_processed = 0

        for knowledge in unstructured_knowledge:
            # 结构化处理
            structured = await self._structure_single_knowledge(knowledge)

            # 更新知识记录
            async with get_database_session() as session:
                result = await session.execute(
                    select(KnowledgeDatabaseModel).where(
                        KnowledgeDatabaseModel.id == knowledge.id
                    )
                )
                k = result.scalar_one_or_none()
                if k:
                    k.struct_result = structured
                    await session.commit()

            items_processed += 1

        logger.info(
            "knowledge_structured",
            items_processed=items_processed
        )

        return {
            "operation": "structure_knowledge",
            "items_processed": items_processed
        }

    async def _structure_single_knowledge(
        self, knowledge: KnowledgeDatabaseModel
    ) -> Dict[str, Any]:
        """
        结构化单条知识

        Args:
            knowledge: 知识对象

        Returns:
            Dict: 结构化后的知识
        """
        # 简化的结构化逻辑
        return {
            "summary": str(knowledge.content)[:100],
            "category": knowledge.source,
            "keywords": [],
            "confidence": 0.8
        }

    async def _map_knowledge_to_abilities(self) -> Dict[str, Any]:
        """
        知识与能力映射

        将知识与系统能力进行关联，便于能力检索

        Returns:
            Dict: 包含映射结果的字典
        """
        # 模拟知识与能力映射
        await asyncio.sleep(0.2)

        items_mapped = 0

        logger.info(
            "knowledge_ability_mapping_completed",
            items_mapped=items_mapped
        )

        return {
            "operation": "map_knowledge_to_abilities",
            "items_mapped": items_mapped
        }

    async def _store_knowledge(
        self,
        content: Dict[str, Any],
        source: str,
        ability_tags: Optional[List[str]] = None
    ) -> KnowledgeDatabaseModel:
        """
        存储知识到数据库

        Args:
            content: 知识内容
            source: 知识来源
            ability_tags: 能力标签

        Returns:
            KnowledgeDatabaseModel: 存储的知识对象
        """
        knowledge_id = IDGenerator.generate_knowledge_id()

        async with get_database_session() as session:
            knowledge = KnowledgeDatabaseModel(
                content=content,
                source=source,
                learn_status="learned",
                ability_tags=ability_tags or []
            )
            session.add(knowledge)
            await session.commit()
            await session.refresh(knowledge)

        logger.info(
            "knowledge_stored",
            knowledge_id=knowledge_id,
            source=source
        )

        return knowledge

    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """
        获取知识统计信息

        Returns:
            Dict: 包含统计信息的字典

        Example:
            >>> stats = await learner.get_knowledge_statistics()
            >>> print(f"Total knowledge: {stats['total_count']}")
        """
        async with get_database_session() as session:
            # 获取总知识数
            result = await session.execute(
                select(KnowledgeDatabaseModel)
            )
            all_knowledge = list(result.scalars().all())

            total_count = len(all_knowledge)

            # 按来源统计
            source_counts = {}
            for k in all_knowledge:
                source = k.source or "unknown"
                source_counts[source] = source_counts.get(source, 0) + 1

            # 按能力标签统计
            ability_tag_counts = {}
            for k in all_knowledge:
                if k.ability_tags:
                    for tag in k.ability_tags:
                        ability_tag_counts[tag] = ability_tag_counts.get(tag, 0) + 1

        return {
            "total_count": total_count,
            "source_distribution": source_counts,
            "ability_tag_distribution": ability_tag_counts,
            "top_abilities": sorted(
                ability_tag_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
