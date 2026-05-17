# Phase 1: 应用基础与认证骨架 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-17
**Phase:** 1-应用基础与认证骨架
**Areas discussed:** 认证页面与接口边界, JWT 会话策略, 工程脚手架形态, 开发与演示数据, 前端首屏形态

---

## 认证页面与接口边界

| Option | Description | Selected |
|--------|-------------|----------|
| 最小闭环 | 注册、登录、当前用户、退出；不做真实邮箱验证和密码找回，只保留后续扩展位置。 | ✓ |
| 带邮箱验证占位 | 注册后生成“未验证”状态，但不接真实邮件；页面提示后续会补验证流程。 | |
| 带密码找回占位 | 登录页显示“忘记密码”，但先只做不可用/敬请期待状态，不实现重置链路。 | |
| 更完整认证首版 | 注册、登录、当前用户、退出、邮箱验证占位、密码找回占位都做进 Phase 1。 | |

**User's choice:** 1  
**Notes:** Phase 1 锁定为最小认证闭环，不做邮箱验证、密码找回或相关占位页面。

---

## JWT 会话策略

| Option | Description | Selected |
|--------|-------------|----------|
| Access token only + localStorage | 登录后把 JWT 存到 `localStorage`，Axios 自动带 Bearer Token；退出时删除。实现最快，适合课程/demo MVP。 | |
| Access token only + httpOnly cookie | 后端设置 httpOnly cookie，前端不直接读 token。更安全，但 FastAPI CORS/cookie 配置和本地开发会复杂一点。 | |
| Access + refresh token | access token 短期有效，refresh token 用于续期。更完整，但超出 Phase 1 最小闭环。 | |
| 由实现阶段决定 | 先在 CONTEXT 里记录安全倾向，具体由 planner 结合技术细节决定。 | ✓ |

**User's choice:** 4  
**Notes:** 用户将 token 存储方式交给 planner/implementation 决定。Phase 1 仍必须证明登录、刷新恢复、退出失效和受保护访问。

---

## 工程脚手架形态

| Option | Description | Selected |
|--------|-------------|----------|
| 严格按 LLD 双目录 | 建 `backend/` 和 `frontend/`，后端 FastAPI，前端 Vue/Vite；只加必要配置和启动命令。 | |
| 双目录 + Docker Compose | 除 `backend/`、`frontend/` 外，同时提供 MySQL/Redis 的 `docker-compose.yml`，方便本地一键启动。 | |
| 双目录 + Alembic + Docker Compose | Phase 1 就把数据库迁移、MySQL/Redis Compose、环境变量样例都搭好。更完整，但骨架阶段会更重。 | ✓ |
| 先前端/后端最小可运行，不接真实数据库 | 后端先用内存或 SQLite 支撑认证 smoke test，MySQL/Redis 留到后续阶段。 | |

**User's choice:** 3  
**Notes:** Phase 1 应建立 `backend/` + `frontend/`、Alembic、Docker Compose、MySQL 8、Redis 7 和环境变量样例。

---

## 开发与演示数据

| Option | Description | Selected |
|--------|-------------|----------|
| 只做数据库迁移，不放种子数据 | 最干净；用户自己注册账号进行 smoke test。 | |
| 提供一个 demo 用户 seed | 用脚本创建演示账号，方便评审和后续阶段联调。 | ✓ |
| 提供 demo 用户 + demo 团队/项目 | 但团队/项目属于 Phase 2，放在 Phase 1 会越界。 | |
| 只做测试 fixture，不做演示 seed | 测试里有用户 fixture，实际开发库不自动塞数据。 | |

**User's choice:** 2  
**Notes:** Phase 1 seed 只创建一个 demo 用户。团队、项目、任务等演示数据不得提前进入 Phase 1。

---

## 前端首屏形态

| Option | Description | Selected |
|--------|-------------|----------|
| 受保护空白首页 | 登录后进入一个简单页面，只显示当前用户信息和退出按钮。最快，但演示感弱。 | |
| TTCS 基础 AppLayout | 登录后进入带顶部栏/侧边栏/用户菜单的基础布局，内容区显示“Phase 1 受保护首页”。 | ✓ |
| 个人工作台雏形 | 登录后进入工作台样式页面，但工作台属于 Phase 5，容易提前越界。 | |
| 由 UI 阶段决定 | Phase 1 只要求受保护路由可用，具体布局交给 `$gsd-ui-phase 1`。 | |

**User's choice:** 2  
**Notes:** 登录后进入基础 TTCS AppLayout，但内容区保持 Phase 1 范围，不实现真实工作台队列。

---

## the agent's Discretion

- Token 存储方式由 planner/implementation 在 `localStorage` 与 `httpOnly` cookie 等方案中选择，并说明取舍。
- 具体启动命令、包管理器和测试工具由 planner 决定，但必须符合锁定技术栈和本地启动清晰性。

## Deferred Ideas

- 邮箱验证。
- 密码找回。
- Refresh token 和多设备会话管理。
- 团队/项目/任务 demo seed 数据。
- 个人工作台队列和 dashboard 指标。
