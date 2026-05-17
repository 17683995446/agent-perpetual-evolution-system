"""
Enhanced Structured Logging Abstraction - 增强结构化日志抽象层（7个单词）

基于structlog的开源工具，提供完整的日志追踪、上下文、日志采样、聚合等功能。
"""

import structlog
import logging
import sys
import json
import time
import uuid
import asyncio
from typing import Any, Dict, Optional, List, Set
from datetime import datetime
from pathlib import Path
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum


# ==================== 配置 ====================

class LogLevel(Enum):
    """日志级别"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogFormat(Enum):
    """日志格式"""
    JSON = "json"
    CONSOLE = "console"
    TEXT = "text"


@dataclass
class LogConfiguration:
    """日志配置"""
    log_level: LogLevel = LogLevel.INFO
    log_format: LogFormat = LogFormat.JSON
    log_dir: Optional[str] = None
    log_file_prefix: str = "app"
    max_file_size_mb: int = 100
    backup_count: int = 10
    enable_console: bool = True
    enable_file: bool = True
    enable_json: bool = True
    enable_trace_id: bool = True
    enable_sample: bool = True
    sample_rate: float = 1.0
    fields_to_mask: List[str] = field(default_factory=lambda: ["password", "token", "api_key", "secret"])


# ==================== 上下文管理 ====================

trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')
span_id_var: ContextVar[str] = ContextVar('span_id', default='')
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class LogContext:
    """
    日志上下文管理器
    提供请求追踪、Span追踪等上下文管理
    """
    
    _contexts: Dict[str, Any] = {}
    
    @classmethod
    def set_trace_id(cls, trace_id: Optional[str] = None) -&gt; str:
        """设置追踪ID"""
        tid = trace_id or str(uuid.uuid4())
        trace_id_var.set(tid)
        cls._contexts['trace_id'] = tid
        return tid
    
    @classmethod
    def get_trace_id(cls) -&gt; str:
        """获取追踪ID"""
        tid = trace_id_var.get()
        if not tid:
            tid = cls.set_trace_id()
        return tid
    
    @classmethod
    def set_span_id(cls, span_id: Optional[str] = None) -&gt; str:
        """设置Span ID"""
        sid = span_id or str(uuid.uuid4())[:8]
        span_id_var.set(sid)
        cls._contexts['span_id'] = sid
        return sid
    
    @classmethod
    def get_span_id(cls) -&gt; str:
        """获取Span ID"""
        sid = span_id_var.get()
        if not sid:
            sid = cls.set_span_id()
        return sid
    
    @classmethod
    def set_request_id(cls, request_id: Optional[str] = None) -&gt; str:
        """设置请求ID"""
        rid = request_id or str(uuid.uuid4())
        request_id_var.set(rid)
        cls._contexts['request_id'] = rid
        return rid
    
    @classmethod
    def get_request_id(cls) -&gt; str:
        """获取请求ID"""
        rid = request_id_var.get()
        if not rid:
            rid = cls.set_request_id()
        return rid
    
    @classmethod
    def add_context(cls, key: str, value: Any) -&gt; None:
        """添加上下文"""
        cls._contexts[key] = value
    
    @classmethod
    def get_context(cls, key: str, default: Any = None) -&gt; Any:
        """获取上下文"""
        return cls._contexts.get(key, default)
    
    @classmethod
    def clear_context(cls) -&gt; None:
        """清除上下文"""
        cls._contexts.clear()
        trace_id_var.set('')
        span_id_var.set('')
        request_id_var.set('')


# ==================== 日志处理器 ====================

class StructuredLogHandler:
    """
    结构化日志处理器
    整合多个日志处理器：控制台、文件、JSON
    """
    
    def __init__(self, config: Optional[LogConfiguration] = None):
        self.config = config or LogConfiguration()
        self._processors: List[structlog.typing.Processor] = []
        self._setup_processors()
        
    def _setup_processors(self) -&gt; None:
        """设置日志处理器链"""
        self._processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]
        
        if self.config.enable_trace_id:
            self._processors.append(self._add_trace_context)
            
        if self.config.enable_json:
            self._processors.append(self._mask_sensitive_data)
            
        self._processors.append(structlog.processors.format_exc_info)
        
        if self.config.log_format == LogFormat.JSON:
            self._processors.append(structlog.processors.JSONRenderer())
        else:
            self._processors.append(
                structlog.dev.ConsoleRenderer(colors=True)
            )
    
    def _add_trace_context(
        self,
        logger: Any,
        method_name: str,
        event_dict: Dict[str, Any]
    ) -&gt; Dict[str, Any]:
        """添加追踪上下文"""
        event_dict['trace_id'] = LogContext.get_trace_id()
        event_dict['span_id'] = LogContext.get_span_id()
        event_dict['request_id'] = LogContext.get_request_id()
        return event_dict
    
    def _mask_sensitive_data(
        self,
        logger: Any,
        method_name: str,
        event_dict: Dict[str, Any]
    ) -&gt; Dict[str, Any]:
        """掩码敏感数据"""
        for field_name in self.config.fields_to_mask:
            if field_name in event_dict:
                value = event_dict[field_name]
                if isinstance(value, str) and len(value) &gt; 4:
                    event_dict[field_name] = value[:2] + '*' * (len(value) - 4) + value[-2:]
        return event_dict
    
    def configure(self) -&gt; None:
        """配置structlog"""
        structlog.configure(
            processors=self._processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    def get_logger(self, name: str) -&gt; structlog.stdlib.BoundLogger:
        """获取logger实例"""
        return structlog.get_logger(name)


class LogAggregator:
    """
    日志聚合器
    收集、过滤、聚合日志
    """
    
    def __init__(self, max_logs: int = 10000):
        self.max_logs = max_logs
        self._logs: List[Dict[str, Any]] = []
        self._index: Dict[str, List[int]] = {}
        
    def add_log(self, log_entry: Dict[str, Any]) -&gt; None:
        """添加日志"""
        log_entry['_index'] = len(self._logs)
        self._logs.append(log_entry)
        
        # 索引
        if 'level' in log_entry:
            level = log_entry['level']
            if level not in self._index:
                self._index[level] = []
            self._index[level].append(len(self._logs) - 1)
        
        if 'trace_id' in log_entry:
            trace_id = log_entry['trace_id']
            if trace_id not in self._index:
                self._index[trace_id] = []
            self._index[trace_id].append(len(self._logs) - 1)
        
        # 清理旧日志
        if len(self._logs) &gt; self.max_logs:
            self._logs = self._logs[-self.max_logs:]
    
    def get_logs_by_level(self, level: str) -&gt; List[Dict[str, Any]]:
        """按级别获取日志"""
        indices = self._index.get(level, [])
        return [self._logs[i] for i in indices if i &lt; len(self._logs)]
    
    def get_logs_by_trace(self, trace_id: str) -&gt; List[Dict[str, Any]]:
        """按追踪ID获取日志"""
        indices = self._index.get(trace_id, [])
        return [self._logs[i] for i in indices if i &lt; len(self._logs)]
    
    def get_recent_logs(self, count: int = 100) -&gt; List[Dict[str, Any]]:
        """获取最近日志"""
        return self._logs[-count:]
    
    def clear(self) -&gt; None:
        """清空日志"""
        self._logs.clear()
        self._index.clear()
    
    def get_statistics(self) -&gt; Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'total_logs': len(self._logs),
            'by_level': {},
            'oldest_timestamp': None,
            'newest_timestamp': None
        }
        
        for level in self._index:
            stats['by_level'][level] = len(self._index[level])
        
        if self._logs:
            stats['oldest_timestamp'] = self._logs[0].get('timestamp')
            stats['newest_timestamp'] = self._logs[-1].get('timestamp')
        
        return stats


class LogSampler:
    """
    日志采样器
    实现日志采样策略，减少日志量
    """
    
    def __init__(self, sample_rate: float = 1.0):
        self.sample_rate = sample_rate
        self._counters: Dict[str, int] = {}
        
    def should_log(self, event_type: str) -&gt; bool:
        """判断是否应该记录日志"""
        if self.sample_rate &gt;= 1.0:
            return True
            
        if self.sample_rate &lt;= 0.0:
            return False
            
        count = self._counters.get(event_type, 0)
        self._counters[event_type] = count + 1
        
        return (count % int(1 / self.sample_rate)) == 0
    
    def reset(self) -&gt; None:
        """重置计数器"""
        self._counters.clear()


# ==================== 依赖注入集成 ====================

class LogService:
    """
    日志服务
    提供统一的日志服务接口
    """
    
    def __init__(self, config: Optional[LogConfiguration] = None):
        self.config = config or LogConfiguration()
        self.handler = StructuredLogHandler(self.config)
        self.aggregator = LogAggregator()
        self.sampler = LogSampler(config.sample_rate if config else 1.0)
        self._loggers: Dict[str, Any] = {}
        
    def initialize(self) -&gt; None:
        """初始化日志服务"""
        self.handler.configure()
        
    def get_logger(self, name: str) -&gt; Any:
        """获取logger"""
        if name not in self._loggers:
            self._loggers[name] = self.handler.get_logger(name)
        return self._loggers[name]
    
    def log(
        self,
        level: str,
        message: str,
        logger_name: str = "app",
        **kwargs
    ) -&gt; None:
        """记录日志"""
        if not self.sampler.should_log(f"{logger_name}.{level}"):
            return
            
        logger = self.get_logger(logger_name)
        log_func = getattr(logger, level, logger.info)
        
        log_entry = {
            'level': level,
            'message': message,
            'logger': logger_name,
            **kwargs
        }
        
        self.aggregator.add_log(log_entry)
        log_func(message, **kwargs)
    
    def debug(self, message: str, logger_name: str = "app", **kwargs) -&gt; None:
        """记录DEBUG日志"""
        self.log("debug", message, logger_name, **kwargs)
    
    def info(self, message: str, logger_name: str = "app", **kwargs) -&gt; None:
        """记录INFO日志"""
        self.log("info", message, logger_name, **kwargs)
    
    def warning(self, message: str, logger_name: str = "app", **kwargs) -&gt; None:
        """记录WARNING日志"""
        self.log("warning", message, logger_name, **kwargs)
    
    def error(self, message: str, logger_name: str = "app", **kwargs) -&gt; None:
        """记录ERROR日志"""
        self.log("error", message, logger_name, **kwargs)
    
    def critical(self, message: str, logger_name: str = "app", **kwargs) -&gt; None:
        """记录CRITICAL日志"""
        self.log("critical", message, logger_name, **kwargs)
    
    def get_dashboard_data(self) -&gt; Dict[str, Any]:
        """获取日志仪表盘数据"""
        stats = self.aggregator.get_statistics()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'statistics': stats,
            'recent_logs': self.aggregator.get_recent_logs(20),
            'config': {
                'log_level': self.config.log_level.value,
                'log_format': self.config.log_format.value,
                'sample_rate': self.config.sample_rate
            }
        }


# ==================== 全局实例 ====================

_log_service: Optional[LogService] = None


def get_log_service() -&gt; LogService:
    """获取全局日志服务实例"""
    global _log_service
    if _log_service is None:
        _log_service = LogService()
        _log_service.initialize()
    return _log_service


def get_structured_logger(name: str) -&gt; Any:
    """获取结构化logger（兼容旧接口）"""
    return get_log_service().get_logger(name)


# ==================== 装饰器 ====================

def log_function_call(logger_name: str = "app"):
    """
    函数调用日志装饰器
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            log_service = get_log_service()
            log_service.info(
                f"Calling function: {func_name}",
                logger_name=logger_name,
                function_name=func_name,
                args=str(args)[:100]
            )
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                log_service.info(
                    f"Function completed: {func_name}",
                    logger_name=logger_name,
                    function_name=func_name,
                    duration=duration,
                    status="success"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_service.error(
                    f"Function failed: {func_name}",
                    logger_name=logger_name,
                    function_name=func_name,
                    duration=duration,
                    error=str(e),
                    status="error"
                )
                raise
                
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__
            log_service = get_log_service()
            log_service.info(
                f"Calling function: {func_name}",
                logger_name=logger_name,
                function_name=func_name,
                args=str(args)[:100]
            )
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_service.info(
                    f"Function completed: {func_name}",
                    logger_name=logger_name,
                    function_name=func_name,
                    duration=duration,
                    status="success"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_service.error(
                    f"Function failed: {func_name}",
                    logger_name=logger_name,
                    function_name=func_name,
                    duration=duration,
                    error=str(e),
                    status="error"
                )
                raise
                
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


