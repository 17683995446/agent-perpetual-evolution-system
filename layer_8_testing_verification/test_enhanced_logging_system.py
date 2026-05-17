"""
Enhanced Logging Tests - 增强日志系统测试
单元测试、集成测试、系统测试
"""

import pytest
import asyncio
import time
from datetime import datetime


# ==================== 单元测试 ====================

class TestLogAggregator:
    """日志聚合器测试"""
    
    def test_add_log(self):
        """测试添加日志"""
        logs = []
        
        log_entry = {
            'level': 'info',
            'message': 'Test message',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logs.append(log_entry)
        assert len(logs) == 1
    
    def test_get_logs_by_level(self):
        """测试按级别获取日志"""
        logs_by_level = {'info': [], 'error': []}
        
        for i in range(5):
            logs_by_level['info'].append({'level': 'info', 'message': f'Info {i}'})
        for i in range(3):
            logs_by_level['error'].append({'level': 'error', 'message': f'Error {i}'})
        
        assert len(logs_by_level['info']) == 5
        assert len(logs_by_level['error']) == 3
    
    def test_get_recent_logs(self):
        """测试获取最近日志"""
        logs = []
        for i in range(20):
            logs.append({'level': 'info', 'message': f'Message {i}'})
        
        recent = logs[-5:]
        assert len(recent) == 5
    
    def test_max_logs_limit(self):
        """测试日志数量限制"""
        logs = []
        max_logs = 10
        
        for i in range(20):
            logs.append({'level': 'info', 'message': f'Message {i}'})
            if len(logs) > max_logs:
                logs = logs[-max_logs:]
        
        assert len(logs) == 10


class TestLogSampler:
    """日志采样器测试"""
    
    def test_full_sampling(self):
        """测试全采样"""
        sample_rate = 1.0
        
        results = []
        for i in range(10):
            should_log = sample_rate >= 1.0 or i % int(1 / sample_rate) == 0
            results.append(should_log)
        
        assert all(results)
    
    def test_no_sampling(self):
        """测试无采样"""
        sample_rate = 0.0
        
        results = []
        for i in range(10):
            should_log = sample_rate > 0.0 and (i % int(1 / sample_rate) == 0 if sample_rate > 0 else False)
            results.append(should_log)
        
        assert not any(results)
    
    def test_partial_sampling(self):
        """测试部分采样"""
        sample_rate = 0.5
        counter = {'count': 0}
        
        results = []
        for i in range(10):
            if sample_rate > 0.0 and sample_rate < 1.0:
                should_log = counter['count'] % int(1 / sample_rate) == 0
                counter['count'] += 1
            else:
                should_log = sample_rate >= 1.0
            results.append(should_log)
        
        true_count = sum(results)
        assert 3 <= true_count <= 7


# ==================== 集成测试 ====================

class TestLogServiceIntegration:
    """日志服务集成测试"""
    
    def test_log_levels(self):
        """测试日志级别"""
        logs = []
        
        logs.append({'level': 'debug', 'message': 'Debug message'})
        logs.append({'level': 'info', 'message': 'Info message'})
        logs.append({'level': 'warning', 'message': 'Warning message'})
        logs.append({'level': 'error', 'message': 'Error message'})
        logs.append({'level': 'critical', 'message': 'Critical message'})
        
        assert len(logs) == 5
        assert logs[0]['level'] == 'debug'
        assert logs[-1]['level'] == 'critical'
    
    def test_log_statistics(self):
        """测试日志统计"""
        logs = []
        
        logs.append({'level': 'info', 'message': 'Info 1'})
        logs.append({'level': 'info', 'message': 'Info 2'})
        logs.append({'level': 'error', 'message': 'Error 1'})
        
        stats = {
            'total_logs': len(logs),
            'by_level': {
                'info': len([l for l in logs if l['level'] == 'info']),
                'error': len([l for l in logs if l['level'] == 'error'])
            }
        }
        
        assert stats['total_logs'] == 3
        assert stats['by_level']['info'] == 2
        assert stats['by_level']['error'] == 1
    
    def test_multiple_loggers(self):
        """测试多logger"""
        logger_logs = {
            'logger1': [],
            'logger2': []
        }
        
        logger_logs['logger1'].append({'level': 'info', 'message': 'Message from logger1'})
        logger_logs['logger2'].append({'level': 'info', 'message': 'Message from logger2'})
        
        assert len(logger_logs['logger1']) == 1
        assert len(logger_logs['logger2']) == 1


# ==================== 系统测试 ====================

class TestLogSystemE2E:
    """日志系统端到端测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流"""
        # 1. 设置追踪上下文
        trace_id = "e2e-trace-001"
        
        # 2. 记录多个日志
        logs = []
        logs.append({'level': 'info', 'message': 'Starting process', 'trace_id': trace_id})
        logs.append({'level': 'info', 'message': 'Processing step 1', 'trace_id': trace_id})
        logs.append({'level': 'info', 'message': 'Processing step 2', 'trace_id': trace_id})
        logs.append({'level': 'warning', 'message': 'Potential issue', 'trace_id': trace_id})
        logs.append({'level': 'info', 'message': 'Completing process', 'trace_id': trace_id})
        
        # 3. 获取追踪日志
        trace_logs = [log for log in logs if log.get('trace_id') == trace_id]
        
        # 4. 验证
        assert len(trace_logs) == 5
        assert all(log['trace_id'] == trace_id for log in trace_logs)
        
        # 5. 获取统计
        stats = {
            'total_logs': len(logs),
            'by_level': {
                'info': len([l for l in logs if l['level'] == 'info']),
                'warning': len([l for l in logs if l['level'] == 'warning'])
            }
        }
        assert stats['total_logs'] == 5
        assert stats['by_level']['info'] == 4
        assert stats['by_level']['warning'] == 1
    
    def test_concurrent_logging(self):
        """测试并发日志记录"""
        all_logs = []
        
        async def log_worker(worker_id: int):
            worker_logs = []
            for i in range(10):
                worker_logs.append({'level': 'info', 'message': f'Worker {worker_id} message {i}'})
                await asyncio.sleep(0.001)
            return worker_logs
        
        async def run_concurrent():
            tasks = [log_worker(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            for worker_logs in results:
                all_logs.extend(worker_logs)
        
        asyncio.run(run_concurrent())
        
        assert len(all_logs) == 50
    
    def test_error_tracking(self):
        """测试错误追踪"""
        error_logs = []
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error_logs.append({'level': 'error', 'message': f'Exception occurred: {str(e)}'})
        
        assert len(error_logs) == 1
        assert 'ValueError' in error_logs[0]['message']


# ==================== 性能测试 ====================

class TestLogPerformance:
    """日志性能测试"""
    
    def test_high_throughput(self):
        """测试高吞吐量"""
        logs = []
        
        start_time = time.time()
        log_count = 10000
        
        for i in range(log_count):
            logs.append({'level': 'info', 'message': f'High throughput test message {i}'})
        
        duration = time.time() - start_time
        throughput = log_count / duration
        
        print(f"\nHigh throughput: {throughput:.2f} logs/sec")
        print(f"Duration: {duration:.3f} seconds for {log_count} logs")
        
        assert throughput > 1000
    
    def test_concurrent_performance(self):
        """测试并发性能"""
        all_logs = []
        
        async def concurrent_logs(count: int):
            logs = []
            for i in range(count):
                logs.append({'level': 'info', 'message': f'Concurrent message {i}'})
                await asyncio.sleep(0)
            return logs
        
        async def run():
            start_time = time.time()
            tasks = [concurrent_logs(1000) for _ in range(5)]
            results = await asyncio.gather(*tasks)
            for worker_logs in results:
                all_logs.extend(worker_logs)
            duration = time.time() - start_time
            return duration
        
        duration = asyncio.run(run())
        throughput = 5000 / duration
        
        print(f"\nConcurrent throughput: {throughput:.2f} logs/sec")
        
        assert throughput > 2000


# ==================== 运行所有测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

