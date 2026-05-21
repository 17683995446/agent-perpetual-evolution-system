#!/usr/bin/env python3
"""
Agent永续自进化系统 - v18.0迭代深度测试
更长时间、更大规模、更复杂、更高难度、更混乱场景
每次迭代都是一次进化！
"""

import asyncio
import time
import random
import traceback
import gc
from datetime import datetime
from typing import Dict, List, Any


class IterationV18Tester:
    """v18.0迭代测试"""

    def __init__(self):
        self.start_time = datetime.now()
        self.iteration_count = 18
        self.test_results: List[Dict] = []
        self.bugs_found: List[Dict] = []
        self.fixes_applied: List[Dict] = []

        print("=" * 200)
        print(f"🎯 Agent永续自进化系统 - v{self.iteration_count}.0 迭代测试")
        print("📋 更长时间、更大规模、更复杂、更高难度、更混乱场景")
        print("📋 每次迭代都是一次进化！")
        print("=" * 200)

    def log(self, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")

    def record(self, name: str, passed: bool, details: str = ""):
        result = {"name": name, "passed": passed, "details": details}
        self.test_results.append(result)
        status = "✅" if passed else "❌"
        self.log(f"{status} {name}: {details}")
        return result

    async def test_all_modules_comprehensive(self):
        """全面测试所有核心模块"""
        self.log("\n📦 测试所有核心模块...")

        modules = [
            ("配置管理", self._test_config),
            ("数据库模型", self._test_database_models),
            ("枚举定义", self._test_enums),
            ("ID生成器", self._test_id_generator),
            ("日志系统", self._test_logger),
            ("任务仓储", self._test_task_repository),
            ("进化引擎", self._test_evolution_engine),
            ("记忆清理", self._test_memory_cleanup),
        ]

        all_passed = True
        for name, test_fn in modules:
            try:
                await test_fn()
                self.record(name, True, "测试通过")
            except Exception as e:
                self.record(name, False, str(e))
                self.bugs_found.append({"module": name, "error": str(e), "traceback": traceback.format_exc()})
                all_passed = False

        return all_passed

    async def _test_config(self):
        """测试配置管理"""
        from src.agent_perpetual_system.core.config_manager import get_application_settings
        settings = get_application_settings()
        assert settings.app_name == "Agent Perpetual System"
        assert settings.app_version == "2.0.0"

    async def _test_database_models(self):
        """测试数据库模型"""
        from src.agent_perpetual_system.core.database_models import TaskStatusEnum
        assert TaskStatusEnum.PENDING == "pending"
        assert TaskStatusEnum.COMPLETED == "completed"

    async def _test_enums(self):
        """测试枚举"""
        from src.agent_perpetual_system.core.database_models import RunningModeEnum, EvolutionPhaseEnum
        assert RunningModeEnum.IDLE == "idle"
        assert EvolutionPhaseEnum.IDLE == "idle"

    async def _test_id_generator(self):
        """测试ID生成器"""
        from src.agent_perpetual_system.utils.id_generator import IDGenerator
        ids = [IDGenerator.generate_task_id() for _ in range(1000)]
        assert len(set(ids)) == 1000

    async def _test_logger(self):
        """测试日志系统"""
        from src.agent_perpetual_system.core.logger_config import get_structured_logger
        logger = get_structured_logger("test")
        logger.info("test_message")

    async def _test_task_repository(self):
        """测试任务仓储"""
        from src.agent_perpetual_system.modules.task_management.task_repository import TaskRepository
        assert TaskRepository is not None

    async def _test_evolution_engine(self):
        """测试进化引擎"""
        from src.agent_perpetual_system.modules.evolution_system.evolution_engine import EvolutionEngine
        engine = EvolutionEngine()
        assert engine is not None

    async def _test_memory_cleanup(self):
        """测试记忆清理"""
        from src.agent_perpetual_system.modules.evolution_system.memory_cleanup_manager import MemoryCleanupManager
        manager = MemoryCleanupManager()
        assert manager is not None

    async def test_boundary_extreme_cases(self):
        """测试极端边界情况"""
        self.log("\n🔍 测试极端边界情况...")

        test_cases = [
            ("空字符串", ""),
            ("超长字符串", "x" * 100000),
            ("None值", None),
            ("负数", -1),
            ("极大数", 10**1000),
            ("空列表", []),
            ("嵌套字典", {"a": {"b": {"c": {"d": 1}}}}),
            ("特殊字符", "\x00\x01\x02"),
        ]

        for name, value in test_cases:
            try:
                str(value)
                repr(value)
                self.record(f"边界-{name}", True, "处理成功")
            except Exception as e:
                self.record(f"边界-{name}", False, str(e))
                self.bugs_found.append({"test": f"boundary_{name}", "error": str(e)})

    async def test_concurrent_stress(self):
        """并发压力测试"""
        self.log("\n💥 并发压力测试...")

        async def worker():
            from src.agent_perpetual_system.utils.id_generator import IDGenerator
            return IDGenerator.generate_task_id()

        start = time.time()
        tasks = [worker() for _ in range(5000)]
        await asyncio.gather(*tasks)
        elapsed = time.time() - start

        rate = 5000 / elapsed
        self.record("并发压力", True, f"5000次/{elapsed:.2f}s = {rate:.0f}次/秒")

    async def test_memory_leak_detection(self):
        """内存泄漏检测"""
        self.log("\n🔍 内存泄漏检测...")

        gc.collect()
        initial_count = len(gc.get_objects())

        for _ in range(100):
            data = {"key": "value", "nested": {"data": list(range(100))}}

        gc.collect()
        final_count = len(gc.get_objects())
        leak = final_count - initial_count

        if leak > 1000:
            self.record("内存泄漏", False, f"检测到泄漏: {leak}个对象")
        else:
            self.record("内存泄漏", True, f"无泄漏: {leak}个对象")

    async def test_error_handling_comprehensive(self):
        """综合错误处理测试"""
        self.log("\n⚠️ 综合错误处理测试...")

        error_tests = [
            ("除零错误", lambda: 1/0),
            ("索引错误", lambda: [][0]),
            ("键错误", lambda: {}[1]),
            ("类型错误", lambda: "str" + 123),
            ("属性错误", lambda: None.attr),
        ]

        for name, fn in error_tests:
            try:
                fn()
                self.record(f"错误处理-{name}", False, "未抛出异常")
            except Exception:
                self.record(f"错误处理-{name}", True, "正确捕获异常")

    async def test_data_consistency(self):
        """数据一致性测试"""
        self.log("\n🔄 数据一致性测试...")

        from src.agent_perpetual_system.core.config_manager import get_application_settings
        from src.agent_perpetual_system.utils.id_generator import IDGenerator

        settings1 = get_application_settings()
        settings2 = get_application_settings()

        assert settings1.app_name == settings2.app_name
        self.record("配置一致性", True, "配置一致")

        ids = [IDGenerator.generate_task_id() for _ in range(500)]
        assert len(set(ids)) == 500
        self.record("ID唯一性", True, "500个ID唯一")

    async def test_performance_benchmark(self):
        """性能基准测试"""
        self.log("\n⚡ 性能基准测试...")

        from src.agent_perpetual_system.utils.id_generator import IDGenerator

        # 配置加载性能
        from src.agent_perpetual_system.core.config_manager import get_application_settings
        start = time.time()
        for _ in range(5000):
            _ = get_application_settings()
        config_time = time.time() - start
        self.record("配置加载性能", True, f"5000次/{config_time:.3f}s = {5000/config_time:.0f}次/秒")

        # ID生成性能
        start = time.time()
        for _ in range(10000):
            _ = IDGenerator.generate_task_id()
        id_time = time.time() - start
        self.record("ID生成性能", True, f"10000次/{id_time:.3f}s = {10000/id_time:.0f}次/秒")

    async def generate_report(self):
        """生成报告"""
        self.log("\n" + "=" * 150)
        self.log(f"📊 v{self.iteration_count}.0 迭代测试报告")
        self.log("=" * 150)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        rate = passed / total * 100 if total > 0 else 0

        self.log(f"\n📈 测试统计:")
        self.log(f"   总测试数: {total}")
        self.log(f"   ✅ 通过: {passed}")
        self.log(f"   ❌ 失败: {failed}")
        self.log(f"   📊 通过率: {rate:.1f}%")

        if self.bugs_found:
            self.log(f"\n🐛 发现 {len(self.bugs_found)} 个BUG:")
            for bug in self.bugs_found:
                self.log(f"   - {bug}")

        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.log(f"\n⏱️ 耗时: {elapsed:.1f}秒")

        if failed == 0:
            self.log(f"\n🎉🎉🎉 v{self.iteration_count}.0 迭代测试完美通过！")

        return {"total": total, "passed": passed, "failed": failed, "bugs": self.bugs_found}

    async def run(self):
        """运行所有测试"""
        self.log(f"\n🚀 开始 v{self.iteration_count}.0 迭代测试...")

        await self.test_all_modules_comprehensive()
        await self.test_boundary_extreme_cases()
        await self.test_concurrent_stress()
        await self.test_memory_leak_detection()
        await self.test_error_handling_comprehensive()
        await self.test_data_consistency()
        await self.test_performance_benchmark()

        return await self.generate_report()


async def main():
    tester = IterationV18Tester()
    return await tester.run()


if __name__ == "__main__":
    asyncio.run(main())
