
"""
Lightweight Dependency Injection Container - 轻量级依赖注入容器（10个单词）
实现解耦、模块化、可测试的依赖注入框架
"""

import asyncio
import inspect
from typing import Dict, Any, Optional, List, Set, Callable, Type, TypeVar, Generic, get_type_hints
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps, partial
from abc import ABC, abstractmethod


T = TypeVar('T')
S = TypeVar('S')


class ServiceLifetime(Enum):
    """服务生命周期"""
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"


class ServiceStatus(Enum):
    """服务状态"""
    UNRESOLVED = "unresolved"
    RESOLVING = "resolving"
    RESOLVED = "resolved"


@dataclass
class ServiceDescriptor(Generic[T]):
    """服务描述符"""
    service_type: Type[T]
    implementation_type: Optional[Type[T]]
    lifetime: ServiceLifetime
    instance: Optional[T] = None
    factory: Optional[Callable[[], T]] = None
    status: ServiceStatus = ServiceStatus.UNRESOLVED
    dependencies: List[Type] = field(default_factory=list)


class CircularDependencyError(Exception):
    """循环依赖错误"""
    pass


class ServiceResolutionError(Exception):
    """服务解析错误"""
    pass


class ServiceContainer:
    """
    依赖注入容器
    支持多种生命周期、循环依赖检测、自动构造函数注入
    """
    
    def __init__(self):
        self._descriptors: Dict[Type, ServiceDescriptor] = {}
        self._resolving: Set[Type] = set()
        self._scoped_services: Dict[Type, Any] = {}
        self._singleton_services: Dict[Type, Any] = {}
        
    def register_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        instance: Optional[T] = None
    ) -&gt; None:
        """注册单例服务"""
        if instance is not None:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=type(instance),
                lifetime=ServiceLifetime.SINGLETON,
                instance=instance,
                status=ServiceStatus.RESOLVED
            )
        else:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_type or service_type,
                lifetime=ServiceLifetime.SINGLETON
            )
            
        self._descriptors[service_type] = descriptor
        
    def register_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ) -&gt; None:
        """注册瞬时服务"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type or service_type,
            lifetime=ServiceLifetime.TRANSIENT,
            factory=factory
        )
        
        self._descriptors[service_type] = descriptor
        
    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None
    ) -&gt; None:
        """注册作用域服务"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type or service_type,
            lifetime=ServiceLifetime.SCOPED
        )
        
        self._descriptors[service_type] = descriptor
        
    def register_instance(
        self,
        service_type: Type[T],
        instance: T
    ) -&gt; None:
        """直接注册实例"""
        self.register_singleton(service_type, instance=instance)
        
    def resolve(self, service_type: Type[T]) -&gt; T:
        """解析服务"""
        return self._resolve(service_type)
        
    def _resolve(self, service_type: Type[T]) -&gt; T:
        """内部解析方法"""
        descriptor = self._descriptors.get(service_type)
        
        if descriptor is None:
            raise ServiceResolutionError(f"Service not registered: {service_type}")
            
        if service_type in self._resolving:
            raise CircularDependencyError(
                f"Circular dependency detected: {service_type}"
            )
            
        if descriptor.status == ServiceStatus.RESOLVED and descriptor.instance is not None:
            return descriptor.instance
            
        self._resolving.add(service_type)
        
        try:
            if descriptor.status == ServiceStatus.RESOLVED:
                if descriptor.instance is not None:
                    return descriptor.instance
                    
            implementation_type = descriptor.implementation_type
            
            if implementation_type is None:
                raise ServiceResolutionError(f"Implementation not provided for {service_type}")
                
            if descriptor.factory:
                instance = descriptor.factory()
            else:
                instance = self._create_instance(implementation_type)
                
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                descriptor.instance = instance
                descriptor.status = ServiceStatus.RESOLVED
                
            return instance
            
        finally:
            self._resolving.remove(service_type)
            
    def _create_instance(self, implementation_type: Type[T]) -&gt; T:
        """创建服务实例"""
        init_signature = inspect.signature(implementation_type.__init__)
        
        if len(init_signature.parameters) == 1):
            return implementation_type()
            
        dependencies = {}
        
        for param_name, param in init_signature.parameters.items():
            if param_name == 'self':
                continue
                
            if param.annotation == inspect.Parameter.empty:
                    raise ServiceResolutionError(
                        f"Parameter {param_name} of {implementation_type} has no type annotation"
                    )
                    
            dependency_type = param.annotation
            dependencies[param_name] = self._resolve(dependency_type)
            
        return implementation_type(**dependencies)
        
    def get(self, service_type: Type[T]) -&gt; Optional[T]:
        """获取服务（不抛异常"""
        try:
            return self.resolve(service_type)
        except Exception:
            return None
            
    def create_scope(self) -&gt; 'ServiceScope':
        """创建作用域"""
        return ServiceScope(self)


class ServiceScope:
    """
    服务作用域
    提供作用域内的服务解析
    """
    
    def __init__(self, container: ServiceContainer):
        self._container = container
        self._scoped_instances: Dict[Type, Any] = {}
        self._is_disposed = False
        
    def resolve(self, service_type: Type[T]) -&gt; T:
        """在作用域内解析服务"""
        if self._is_disposed:
            raise RuntimeError("Scope is disposed")
            
        descriptor = self._container._descriptors.get(service_type)
        
        if descriptor and descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
                
        instance = self._container._resolve(service_type)
        
        if descriptor and descriptor.lifetime == ServiceLifetime.SCOPED:
            self._scoped_instances[service_type] = instance
            
        return instance
        
    def __enter__(self) -&gt; 'ServiceScope':
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -&gt; None:
        self.dispose()
        
    def dispose(self) -&gt; None:
        """释放作用域"""
        self._is_disposed = True
        self._scoped_instances.clear()


def inject(container: ServiceContainer):
    """
    注入装饰器
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            resolved_kwargs = {}
            
            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    resolved_kwargs[param_name] = kwargs[param_name]
                elif param.annotation != inspect.Parameter.empty:
                    try:
                        resolved_kwargs[param_name] = container.resolve(param.annotation)
                    except Exception:
                        pass
                        
            return await func(*args, **resolved_kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            resolved_kwargs = {}
            
            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    resolved_kwargs[param_name] = kwargs[param_name]
                elif param.annotation != inspect.Parameter.empty:
                    try:
                        resolved_kwargs[param_name] = container.resolve(param.annotation)
                    except Exception:
                        pass
                        
            return func(*args, **resolved_kwargs)
            
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


class EventBus:
    """
    事件总线 - 实现模块间解耦通信
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._async_handlers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, handler: Callable) -&gt; None:
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def subscribe_async(self, event_type: str, handler: Callable) -&gt; None:
        """订阅异步事件"""
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)
        
    def publish(self, event_type: str, *args, **kwargs) -&gt; List[Any]:
        """发布同步事件"""
        results = []
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception:
                pass
                
        return results
        
    async def publish_async(self, event_type: str, *args, **kwargs) -&gt; List[Any]:
        """发布异步事件"""
        results = []
        handlers = self._async_handlers.get(event_type, [])
        
        tasks = []
        for handler in handlers:
            try:
                task = handler(*args, **kwargs)
                tasks.append(task)
            except Exception:
                pass
                
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        return results
        
    def unsubscribe(self, event_type: str, handler: Callable) -&gt; None:
        """取消订阅"""
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)


class MessageQueue:
    """
    消息队列 - 实现生产者消费者模式
    """
    
    def __init__(self, max_size: int = 10000):
        self._queue = asyncio.Queue(maxsize=max_size)
        self._handlers: Dict[str, List[Callable]] = {}
        self._is_running = False
        self._consumer_tasks: List[asyncio.Task] = []
        
    def send(self, topic: str, message: Any) -&gt; None:
        """发送消息"""
        self._queue.put_nowait((topic, message))
        
    async def send_async(self, topic: str, message: Any) -&gt; None:
        """异步发送消息"""
        await self._queue.put((topic, message))
        
    def subscribe(self, topic: str, handler: Callable) -&gt; None:
        """订阅主题"""
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)
        
    async def start(self, consumer_count: int = 1) -&gt; None:
        """启动消费者"""
        self._is_running = True
        
        for i in range(consumer_count):
            task = asyncio.create_task(self._consumer_worker())
            self._consumer_tasks.append(task)
            
    async def shutdown(self) -&gt; None:
        """关闭消息队列"""
        self._is_running = False
        
        for task in self._consumer_tasks:
            task.cancel()
            
        await asyncio.gather(*self._consumer_tasks, return_exceptions=True)
        
    async def _consumer_worker(self) -&gt; None:
        """消费者工作器"""
        while self._is_running:
            try:
                topic, message = await self._queue.get()
                
                handlers = self._handlers.get(topic, [])
                for handler in handlers:
                    try:
                        if inspect.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception:
                        pass
                        
                self._queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception:
                pass


class ModuleBase(ABC):
    """
    模块基类 - 模块化架构的基础
    """
    
    @abstractmethod
    async def initialize(self, container: ServiceContainer) -&gt; None:
        """初始化模块"""
        pass
        
    @abstractmethod
    async def shutdown(self) -&gt; None:
        """关闭模块"""
        pass


class Application:
    """
    应用程序容器 - 集成DI容器和事件总线
    """
    
    def __init__(self):
        self.container = ServiceContainer()
        self.event_bus = EventBus()
        self.modules: List[ModuleBase] = []
        self._is_initialized = False
        
    def register_module(self, module: ModuleBase) -&gt; None:
        """注册模块"""
        self.modules.append(module)
        
    async def initialize(self) -&gt; None:
        """初始化应用"""
        for module in self.modules:
            await module.initialize(self.container)
            
        self._is_initialized = True
        
    async def shutdown(self) -&gt; None:
        """关闭应用"""
        for module in reversed(self.modules):
            await module.shutdown()
            
        self._is_initialized = False

