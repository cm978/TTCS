# Phase 3: 任务执行、日志与阻塞闭环 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-18
**Phase:** 3-任务执行、日志与阻塞闭环
**Areas discussed:** 任务详情承载方式, 任务参与者与 Owner 行为, 子任务与进度表达, 阻塞记录与解除方式, 看板任务卡信息密度, 工作日志写入体验

---

## 任务详情承载方式

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| 任务卡点击后，Phase 3 的任务详情应该怎么承载？ | 抽屉优先 / 独立详情页 / 抽屉 + 详情页 | 抽屉 + 详情页 |
| Phase 3 里抽屉和详情页分别承担什么？ | 抽屉可编辑，详情页完整查看 / 抽屉只读预览，详情页编辑 / 两边都可完整编辑 | 抽屉可编辑，详情页完整查看 |
| 任务抽屉里哪些内容应该引导用户打开完整详情页？ | 复杂结构才跳转 / 所有详情都有跳转 / 只有用户主动点按钮 | 复杂结构才跳转 |
| 独立任务详情页应该支持哪种访问方式？ | 可直接访问 `/tasks/:taskId` / 只在项目内访问 `/projects/:projectId/tasks/:taskId` / Phase 3 先不要求可分享 URL | 可直接访问 `/tasks/:taskId` |

**Notes:** The drawer is the quick execution surface; the full detail page is the complete context surface and future acceptance/evidence home.

---

## 任务参与者与 Owner 行为

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| 创建任务时，Owner 和参与者的默认关系怎么定？ | Owner 默认也是参与者 / Owner 独立于参与者 / 创建时可选 | Owner 默认也是参与者 |
| 任务创建后，谁可以添加或移除参与者？ | Owner + 项目经理 / 只有项目经理 / Owner + 项目经理 + 创建者 | Owner + 项目经理 |
| 如果某个参与者已经写过工作日志，是否还能被移除？ | 可以移除，但历史保留 / 不允许移除 / 只能设为非活跃 | 可以移除，但历史保留 |
| 任务创建时是否允许只有 Owner 一个参与者？ | 允许 Owner 单人任务 / 必须再添加至少一名参与者 / 按任务类型决定 | 允许 Owner 单人任务 |

**Notes:** Current participant membership and historical execution records are separate concerns.

---

## 子任务与进度表达

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| Phase 3 的子任务应该做成什么粒度？ | 轻量 checklist / 可分配小任务 / 混合模式 | 轻量 checklist |
| SRS 写了“最多 3 级子任务”，但 Phase 3 要控制实现复杂度。这里怎么落地？ | Phase 3 只做一层子任务 / 直接支持最多 3 级 / 数据模型预留 parent_id，UI 先只开放一层 | Phase 3 只做一层子任务 |
| 任务进度应该怎么计算？ | 完全由子任务完成比例计算 / 允许手工填写进度 / 子任务比例 + 状态兜底 | 完全由子任务完成比例计算 |
| 如果任务没有子任务，后续提交验收前应该依赖什么补足说明？ | 使用验收说明字段 / 使用工作日志摘要 / Phase 3 不考虑 | 使用验收说明字段 |

**Notes:** Progress remains objective; no manual progress editing or pseudo-progress is introduced.

---

## 阻塞记录与解除方式

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| Phase 3 的阻塞数据应该怎么建模？ | 工作日志驱动 + 任务当前状态冗余 / 纯任务级阻塞字段 / 独立 blocker 表 | 工作日志驱动 + 任务当前状态冗余 |
| 如果多个参与者都标记阻塞，Phase 3 怎么表达？ | 允许多条未解除阻塞，任务只显示当前最严重/最新一条 / 一个任务同一时间只允许一个未解除阻塞 / 每个参与者最多一个未解除阻塞 | 允许多条未解除阻塞，任务只显示当前最严重/最新一条 |
| 未解除阻塞由谁来解除？ | 阻塞记录创建者 + Owner + 项目经理 / 只有创建者 / Owner + 项目经理 | 阻塞记录创建者 + Owner + 项目经理 |
| 解除阻塞时要不要强制写原因/说明？ | 必填解除说明，不少于 10 字符 / 可选解除说明 / 管理者解除时必填，创建者解除时可选 | 必填解除说明，不少于 10 字符 |

**Notes:** Blockers are part of the evidence/risk trail, not just a task flag.

---

## 看板任务卡信息密度

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| Phase 3 的看板卡片默认应该展示多少信息？ | 中密度执行卡 / 极简卡片 / 高密度卡片 | 中密度执行卡 |
| 卡片上最醒目的风险/状态信号应该是什么？ | 阻塞优先，其次逾期/优先级 / 优先级优先，其次阻塞 / 截止日期优先，其次阻塞 | 阻塞优先，其次逾期/优先级 |
| 卡片要不要显示“今日已写日志 / 待写日志”？ | 显示轻量日志状态 / 不显示日志状态 / 显示最近日志摘要 | 显示轻量日志状态 |
| 卡片上应该放哪些直接操作？ | 只放打开抽屉/更多菜单 / 放高频快捷操作 / 只允许点击整卡打开 | 只放打开抽屉/更多菜单 |

**Notes:** Cards should support quick risk scanning without becoming full detail panels.

---

## 工作日志写入体验

| Question | Options Presented | User's Choice |
|----------|-------------------|---------------|
| 工作日志主要在哪里写？ | 任务抽屉内写入 / 独立日志弹窗 / 详情页为主 | 任务抽屉内写入 |
| 工作日志日期规则怎么定？ | 允许补记过去日期，不允许未来日期 / 只允许当天日志 / 允许过去和未来日期 | 允许补记过去日期，不允许未来日期 |
| 工作日志中的 Commit Hash、分支、仓库地址等代码字段怎么处理？ | 可选文本字段，仅保存和展示 / 只预留后端字段，前端暂不显示 / 做基础格式校验 | 可选文本字段，仅保存和展示 |
| 工作日志创建后是否允许修改？ | 创建者可编辑/软删除，但保留审计字段 / 创建后不可修改 / 仅当天可编辑 | 创建者可编辑/软删除，但保留审计字段 |

**Notes:** Work logs are optimized for daily execution while preserving enough audit structure for later acceptance evidence.

---

## the agent's Discretion

- Exact backend route names, schema names, service names, and frontend component names can be selected during planning.
- Drawer layout and full detail page section ordering can be chosen during UI planning.
- Data-model reservation for future nested subtasks may be decided by the planner if it does not expose Phase 3 nested UI or recursive complexity.

## Deferred Ideas

- Full acceptance submission and Review actions belong to Phase 4.
- Notifications, workbench queues, and reports belong to Phase 5.
- Real Git platform integration, strict Git validation, and AI/Agent review belong to v2.
- Three-level nested subtask UI is deferred.
