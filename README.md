# API 接口自动化测试框架

> SDET 视角 · 数据隔离 · Mock 策略 · 契约校验

---

## 三个核心保障（框架级自动生效）

### 1️⃣ 数据隔离 → `framework/isolation/`

**每个测试运行自动获得唯一身份**，创建的数据带上身份标签，互不干扰、自动清理。

```python
# 测试代码 — 框架自动做的事情你不需要手动写
def test_create_user(context):
    # context.tag() 自动给数据加上唯一前缀
    payload = context.tag(factory.create_user_payload())
    # → {"name": "t7f3a_alice", "email": "t7f3a_alice@test.com"}

    resp = user_api.create(payload)
    user_id = AssertionEngine(resp).extract("data.id")

    # 注册清理 → 测试结束自动删除
    context.lifecycle.created("user", user_id)
```

框架保障了什么：

| 场景 | 没有隔离 | 有隔离 |
|------|---------|--------|
| 并行跑测试 | 数据互相覆盖 | 前缀不同，互不干扰 |
| 重复跑测试 | 第二次可能"已存在" | 每次数据不同 |
| 测试失败 | 数据残留 | teardown 自动清理 |
| 查问题 | "这是谁创建的？" | 标签可追溯 |

### 2️⃣ Mock 策略 → `framework/mock/`

**声明式 Mock Profile**，同一套测试在 mock/live 下无感切换。

```bash
pytest                     # live 模式（调真实服务）
TEST_MODE=mock pytest      # mock 模式（不依赖外部）
pytest --mode=hybrid       # 混合模式
```

```python
# 定义 Mock Profile（声明式）
from framework.mock import MockProfile, MockResponse

profile = MockProfile("user")
profile.get("/api/v1/users/{id}", MockResponse(200, user_response))
profile.post("/api/v1/users", MockResponse(201, create_response))
```

### 3️⃣ 契约校验 → `framework/contract/`

**在 models/ 中注册 Schema 后，所有通过 HttpClient 的请求自动校验响应结构。**

```python
# models/__init__.py — 定义模型 + 注册契约
registry.register("POST", "/api/v1/users",
                  response_schema=API_RESPONSE_SCHEMA)

# 之后任何测试调用 user_api.create()，响应自动做 Schema 校验
# 不符合契约 → 控制台输出 ⚠️ 告警
# 测试仍然继续（契约违规不阻断业务测试）
```

---

## 📂 目录结构

```
├── framework/                  ← 框架核心（新增）
│   ├── isolation/              测试隔离 + 数据生命周期
│   ├── mock/                   Mock Profile + 模式切换
│   └── contract/               Schema 注册 + 自动校验
│
├── common/                     ← 公共组件
│   ├── http_client.py           HTTP 客户端（注入契约校验）
│   ├── assertion.py             断言引擎
│   └── logger.py                日志系统
│
├── models/                     ← 数据模型 + Schema 注册入口
├── apis/                       接口封装
├── config/                     配置中心
├── data/                       测试数据工厂
│
├── tests/
│   ├── fixtures/               共享 fixture 工厂
│   ├── scenarios/              场景测试（P0/P1/P2）
│   └── contracts/              契约测试（Schema 合法性）
│
├── conftest.py                 ← 框架级配置（加载注册 + 注入 context）
└── pytest.ini
```

---

## 🚀 运行

```bash
pytest -m smoke                  # 冒烟测试
pytest -m P0                     # 核心功能
pytest --mode=mock               # Mock 模式（不依赖外部服务）
pytest tests/contracts/          # 契约测试（不改协议不会挂）
python run.py --report           # 运行 + Allure 报告
```