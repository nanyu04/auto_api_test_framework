"""
framework/isolation — 测试隔离子系统

这是整个框架的第一保障。每个测试运行自动获得一个 Context，
所有数据操作都通过 Context 进行，确保：
  1. 数据可追溯（知道是谁创建的）
  2. 数据可隔离（不同运行不会撞）
  3. 数据可清理（按 identity 批量删除）
  4. 可并行执行（不受共享状态干扰）
"""
import os
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from common.logger import logger


# =============================================================
#  核心：TestIdentity — 每次测试运行的唯一身份
# =============================================================

##只管打标签
@dataclass
class TestIdentity:
    """
    测试身份标识

    每个测试运行（一条用例的一次执行）得到一个唯一的 identity。
    它包括：
      - run_id:      全局唯一 ID，如 "u7f3a_20260925_164200"
      - test_name:   测试方法名
      - timestamp:   启动时间戳
      - tag:         简写标签，用于命名空间

    所有通过 framework 创建的数据都应该带上 tag 前缀，
    这样 cleanup_by_identity 可以批量删除。
    """
    run_id: str
    test_name: str
    timestamp: float
    tag: str

    @classmethod
    def new(cls, test_name: str) -> "TestIdentity":
        """创建新的测试身份"""
        """
        uuid.uuid4()  
              # 生成一个随机 UUID，比如 UUID('a1b2c3d4-e5f6-7890-abcd-ef1234567890')
            .hex         
             # 转成纯十六进制字符串（去掉横线），比如 'a1b2c3d4e5f67890abcdef1234567890'
             [:8]         # 取前 8 个字符，比如 'a1b2c3d4'
        """
        short_id = uuid.uuid4().hex[:8]
        ts = time.time()
        tag = f"t{short_id}"
        return cls(
            run_id=f"{short_id}_{time.strftime('%Y%m%d_%H%M%S')}",
            test_name=test_name,
            timestamp=ts,
            tag=tag,
        )

    def apply_to(self, data: dict, fields: Optional[List[str]] = None) -> dict:
        """
        给数据打上 identity 标记

        用法：
            payload = identity.apply_to({"name": "test_user", "email": "a@b.com"})
            # → {"name": "test_user_t7f3a", "email": "t7f3a_a@b.com"}

        fields 不传时自动处理 name 和 email 字段。
        """
        result = data.copy()
        targets = fields or [k for k in ["name", "username", "email", "order_no"] if k in data]
        for f in targets:
            if f in result and isinstance(result[f], str):
                result[f] = f"{self.tag}_{result[f]}"
        return result

    def marker(self, resource_type: str, resource_id: Any) -> str:
        """生成资源标记，如 'user:123'"""
        return f"{self.tag}:{resource_type}:{resource_id}"


# =============================================================
#  数据生命周期管理
# =============================================================


@dataclass
class CleanupTask:
    """待清理资源"""
    identity: TestIdentity
    resource_type: str
    resource_id: Any
    endpoint: str
    method: str = "DELETE"

##只管"我创建了什么，待会要删"
class DataLifecycle:
    """
    数据生命周期管理器

    和旧版 DataCleaner 的区别：
      - 绑定 TestIdentity，自动知道"这个测试创建了什么"
      - 按 identity.tag 批量清理
      - 支持资源依赖排序（先删 order 再删 user）
    """

    def __init__(self, identity: TestIdentity, http_client):
        self._identity = identity
        self._client = http_client
        self._tasks: List[CleanupTask] = []
        # 清理优先级：数字越大越先清理
        self._type_order = {"order": 100, "payment": 90, "user": 10}

    # ---------- 注册 ----------

    def created(self, resource_type: str, resource_id: Any,
                endpoint: Optional[str] = None) -> "DataLifecycle":
        """
        注册一个已创建的资源（最重要的方法）

        用法：
            lifecycle.created("user", user_id)
            lifecycle.created("order", order_id, endpoint="/api/v1/orders/xxx")
        """
        endpoint = endpoint or f"/api/v1/{resource_type}s/{resource_id}"
        self._tasks.append(CleanupTask(
            identity=self._identity,
            resource_type=resource_type,#它的类型 如 user
            resource_id=resource_id,#它的id
            endpoint=endpoint,#这个就是地址 就是
        ))
        logger.debug(f"  📝 [Lifecycle] 注册: {resource_type}#{resource_id}")
        return self

    # ---------- 清理 ----------

    def cleanup(self):
        """按依赖顺序清理所有资源"""
        if not self._tasks:
            return

        # 按优先级降序（高优先级先清）
        sorted_tasks = sorted(
            self._tasks,
            #这里面的t就相当于是self._tasks对象
            key=lambda t: self._type_order.get(t.resource_type, 50),
            reverse=True,
        )

        errors = []
        for task in sorted_tasks:
            try:
                self._client.delete(task.endpoint)
                logger.debug(f"  🗑️  [Lifecycle] 已清理: {task.resource_type}#{task.resource_id}")
            except Exception as e:
                errors.append((task, str(e)))

        self._tasks.clear()
        if errors:
            for task, err in errors:
                logger.warning(f"  ⚠️  [Lifecycle] 清理失败: {task.resource_type}#{task.resource_id} → {err}")

    # ---------- 查询 ----------

    @property
    def task_count(self) -> int:
        return len(self._tasks)


# =============================================================
#  TestContext — 测试上下文（供 conftest 使用）
# =============================================================


class TestContext:
    """
    测试上下文

    把 identity + lifecycle 组合在一起，
    是 conftest 对外暴露的唯一对象。
    """

    def __init__(self, test_name: str, http_client):
        self.identity = TestIdentity.new(test_name)
        self.lifecycle = DataLifecycle(self.identity, http_client)
        self._start_time = time.time()

    def tag(self, data: dict, fields: Optional[List[str]] = None) -> dict:
        """给数据打标"""
        return self.identity.apply_to(data, fields)

    @property
    def elapsed(self) -> float:
        return time.time() - self._start_time

    def cleanup(self):
        self.lifecycle.cleanup()
