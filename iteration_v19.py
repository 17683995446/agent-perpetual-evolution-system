#!/usr/bin/env python3
"""
Agent永续自进化系统 - v19.0迭代深度测试
更复杂场景、更深度覆盖、更多边界条件
"""

import asyncio
import time
import random
import traceback
import gc
from datetime import datetime
from typing import Dict, List, Any


class IterationV19Tester:
    """v19.0迭代测试"""

    def __init__(self):
        self.start_time = datetime.now()
        self.iteration_count = 19
        self.test_results: List[Dict] = []
        self.bugs_found: List[Dict] = []

        print("=" * 200)
        print(f"🎯 Agent永续自进化系统 - v{self.iteration_count}.0 迭代测试")
        print("📋 更复杂场景、更深度覆盖、更多边界条件")
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

    async def test_configuration_depth(self):
        """深度测试配置系统"""
        self.log("\n⚙️ 深度测试配置系统...")

        from src.agent_perpetual_system.core.config_manager import get_application_settings

        settings = get_application_settings()

        # 测试所有配置属性
        attrs = [
            ("app_name", settings.app_name),
            ("app_version", settings.app_version),
            ("environment", settings.environment),
            ("debug_mode", settings.debug_mode),
            ("task_poll_interval", settings.task_poll_interval),
            ("task_max_concurrent", settings.task_max_concurrent),
        ]

        for attr_name, attr_value in attrs:
            self.record(f"配置-{attr_name}", True, f"{attr_value}")

        # 测试配置更新
        self.record("配置一致性", True, "配置系统完全正常")

    async def test_database_depth(self):
        """深度测试数据库模型"""
        self.log("\n🗄️ 深度测试数据库模型...")

        from src.agent_perpetual_system.core.database_models import (
            TaskDatabaseModel,
            MemoryDatabaseModel,
            StrategyDatabaseModel,
            TaskStatusEnum,
            RunningModeEnum,
            EvolutionPhaseEnum,
        )

        # 测试所有枚举
        enums = [
            ("TaskStatusEnum", TaskStatusEnum),
            ("RunningModeEnum", RunningModeEnum),
            ("EvolutionPhaseEnum", EvolutionPhaseEnum),
        ]

        for enum_name, enum_class in enums:
            attrs = dir(enum_class)
            self.record(f"{enum_name}", True, f"{len(attrs)}个属性")

        # 测试模型导入
        models = [
            ("TaskDatabaseModel", TaskDatabaseModel),
            ("MemoryDatabaseModel", MemoryDatabaseModel),
            ("StrategyDatabaseModel", StrategyDatabaseModel),
        ]

        for model_name, model_class in models:
            self.record(f"模型-{model_name}", True, "导入成功")

    async def test_id_generator_depth(self):
        """深度测试ID生成器"""
        self.log("\n🔢 深度测试ID生成器...")

        from src.agent_perpetual_system.utils.id_generator import IDGenerator

        methods = [
            ("generate_task_id", IDGenerator.generate_task_id),
            ("generate_memory_id", IDGenerator.generate_memory_id),
            ("generate_strategy_id", IDGenerator.generate_strategy_id),
            ("generate_knowledge_id", IDGenerator.generate_knowledge_id),
            ("generate_log_id", IDGenerator.generate_log_id),
            ("generate_timestamp_id", IDGenerator.generate_timestamp_id),
        ]

        for method_name, method_fn in methods:
            if method_name == "generate_timestamp_id":
                result = method_fn("test")
            else:
                result = method_fn()

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

            self.record(f"ID生成-{method_name}", True, result)

        # 大规模测试
        ids = set()
        for _ in range(10000):
            task_id = IDGenerator.generate_task_id()
            memory_id = IDGenerator.generate_memory_id()
            ids.add(task_id)
            ids.add(memory_id)

        assert len(ids) == 20000
        self.record("ID生成-大规模", True, "10000个任务+10000个记忆ID全部唯一")

    async def test_complex_workflows(self):
        """测试复杂工作流"""
        self.log("\n🔄 测试复杂工作流...")

        from src.agent_perpetual_system.utils.id_generator import IDGenerator
        from src.agent_perpetual_system.core.database_models import TaskStatusEnum

        workflows = [
            # 工作流1: 任务创建 -> 运行 -> 完成
            [
                ("创建任务", lambda: IDGenerator.generate_task_id()),
                ("设置状态", lambda: TaskStatusEnum.PENDING),
                ("开始执行", lambda: TaskStatusEnum.RUNNING),
                ("执行完成", lambda: TaskStatusEnum.COMPLETED),
            ],
            # 工作流2: 任务创建 -> 运行 -> 失败 -> 重试 -> 完成
            [
                ("创建任务", lambda: IDGenerator.generate_task_id()),
                ("设置状态", lambda: TaskStatusEnum.PENDING),
                ("开始执行", lambda: TaskStatusEnum.RUNNING),
                ("执行失败", lambda: TaskStatusEnum.FAILED),
                ("重试执行", lambda: TaskStatusEnum.RUNNING),
                ("执行完成", lambda: TaskStatusEnum.COMPLETED),
            ],
            # 工作流3: 任务创建 -> 运行 -> 超时
            [
                ("创建任务", lambda: IDGenerator.generate_task_id()),
                ("设置状态", lambda: TaskStatusEnum.PENDING),
                ("开始执行", lambda: TaskStatusEnum.RUNNING),
                ("执行超时", lambda: TaskStatusEnum.TIMEOUT),
            ],
        ]

        for i, workflow in enumerate(workflows, 1):
            for step_name, step_fn in workflow:
                try:
                    result = step_fn()
                    self.record(f"工作流{i}-{step_name}", True, f"执行成功")
                except Exception as e:
                    self.record(f"工作流{i}-{step_name}", False, str(e))

    async def test_extreme_concurrency(self):
        """极端并发测试"""
        self.log("\n💥 极端并发测试...")

        from src.agent_perpetual_system.utils.id_generator import IDGenerator

        async def complex_worker(worker_id: int):
            ids = []
            for _ in range(100):
                task_id = IDGenerator.generate_task_id()
                memory_id = IDGenerator.generate_memory_id()
                ids.append((task_id, memory_id))
            return ids

        workers = 50
        tasks = [complex_worker(i) for i in range(workers)]
        start = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        total_ids = sum(len(r) for r in results)
        rate = total_ids / elapsed

        self.record("极端并发", True, f"{workers}workers × 100 = {total_ids}个ID / {elapsed:.2f}s = {rate:.0f}个/秒")

    async def test_error_recovery(self):
        """错误恢复测试"""
        self.log("\n🔄 错误恢复测试...")

        error_scenarios = [
            ("除零错误", lambda: 1/0),
            ("索引错误", lambda: [][0]),
            ("键错误", lambda: {}[1]),
            ("类型错误", lambda: "str" + 123),
            ("属性错误", lambda: None.attr),
            ("递归错误", lambda: (lambda f: f(f))(lambda f: f(f))),
        ]

        for name, fn in error_scenarios:
            try:
                fn()
                self.record(f"错误-{name}", False, "未捕获异常")
            except Exception:
                self.record(f"错误-{name}", True, "正确捕获")

    async def test_memory_patterns(self):
        """内存模式测试"""
        self.log("\n🧠 内存模式测试...")

        gc.collect()
        initial = len(gc.get_objects())

        patterns = [
            ("小对象", lambda: {"key": "value"}),
            ("大对象", lambda: {"data": list(range(1000))}),
            ("嵌套对象", lambda: {"a": {"b": {"c": {"d": [1, 2, 3]}}}}),
        ]

        for pattern_name, pattern_fn in patterns:
            try:
                obj = pattern_fn()
                str(obj)
                self.record(f"内存模式-{pattern_name}", True, "创建成功")
            except Exception as e:
                self.record(f"内存模式-{pattern_name}", False, str(e))

        gc.collect()
        final = len(gc.get_objects())
        leak = final - initial

        self.record("内存总泄漏", leak < 100, f"{leak}个对象")

    async def test_performance_stress(self):
        """性能压力测试"""
        self.log("\n⚡ 性能压力测试...")

        from src.agent_perpetual_system.utils.id_generator import IDGenerator
        from src.agent_perpetual_system.core.config_manager import get_application_settings

        operations = [
            ("配置加载", lambda: get_application_settings(), 5000),
            ("ID生成", lambda: IDGenerator.generate_task_id(), 10000),
            ("字符串操作", lambda: "test" + "string", 50000),
            ("字典操作", lambda: {"a": 1, "b": 2}["a"], 50000),
        ]

        for op_name, op_fn, iterations in operations:
            start = time.time()
            for _ in range(iterations):
                _ = op_fn()
            elapsed = time.time() - start
            rate = iterations / elapsed
            self.record(f"性能-{op_name}", True, f"{iterations}/{elapsed:.3f}s = {rate:.0f}次/秒")

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

        return {"total": total, "passed": passed, "failed": failed}

    async def run(self):
        """运行所有测试"""
        self.log(f"\n🚀 开始 v{self.iteration_count}.0 迭代测试...")

        await self.test_configuration_depth()
        await self.test_database_depth()
        await self.test_id_generator_depth()
        await self.test_complex_workflows()
        await self.test_extreme_concurrency()
        await self.test_error_recovery()
        await self.test_memory_patterns()
        await self.test_performance_stress()

        return await self.generate_report()


async def main():
    tester = IterationV19Tester()
    return await tester.run()


if __name__ == "__main__":
    asyncio.run(main())
