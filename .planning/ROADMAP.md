# Roadmap: TTCS

**Created:** 2026-05-17  
**Mode:** Standard granularity, vertical MVP phases  
**Core Value:** 只有当可追溯证据和人工验收共同证明工作可交付时，任务才能进入完成状态。

## Phase Overview

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 1 | 应用基础与认证骨架 | 建立可运行的前后端基础、认证会话、项目结构和核心工程约束 | AUTH-01..04, ARCH-01..04 |
| 2 | 团队、项目与基础看板 | 让用户能创建团队和项目，并进入默认看板工作空间 | TEAM-01..03, PROJ-01..03 |
| 3 | 任务执行、日志与阻塞闭环 | 让成员能创建和推进任务，记录工作日志，暴露阻塞风险 | TASK-01..08, WORK-01..06 |
| 4 | 证据门禁与人工验收核心 | 让任务完成必须经过证据门禁、提交验收和 Owner/项目经理 Review | ACPT-01..10, EVID-01..05, ARCH-05 |
| 5 | 工作台、通知与项目报表 | 让用户从行动队列工作，并让项目经理看到风险、进度和验收质量 | DASH-01..03, NTFY-01..02, RPT-01..03 |
| 6 | MVP 验证、质量收口与演示准备 | 验证性能、测试覆盖、关键路径和演示体验，形成可验收 MVP | QUAL-01..03 |

## Phase Details

### Phase 1: 应用基础与认证骨架

**Goal:** 搭建 TTCS 可运行的前后端基础，并交付最小认证闭环。  
**Mode:** mvp  
**Requirements:** AUTH-01, AUTH-02, AUTH-03, AUTH-04, ARCH-01, ARCH-02, ARCH-03, ARCH-04  
**UI hint:** yes

**Success Criteria:**
1. 前端 Vue 3/Vite/TypeScript 应用可以启动，并能访问登录、注册和基础布局页面。
2. 后端 FastAPI 应用可以启动，并提供 `/api/v1` 健康检查、认证和当前用户接口。
3. 用户可以注册、登录、获取 JWT，并访问受保护接口。
4. 密码使用 bcrypt 哈希存储，不在响应或日志中泄露明文。
5. 项目结构符合现有 LLD 的前后端目录约定，后续阶段可以直接扩展。

**Notes:**
- 这一阶段不做完整团队/项目业务，只保证身份、工程骨架和 API 约定稳定。
- 单体 FastAPI 后端是 MVP 约束，不引入微服务拆分。

### Phase 2: 团队、项目与基础看板

**Goal:** 让已登录用户创建团队和项目，并拥有可进入的默认项目看板。  
**Mode:** mvp  
**Requirements:** TEAM-01, TEAM-02, TEAM-03, PROJ-01, PROJ-02, PROJ-03  
**UI hint:** yes

**Success Criteria:**
1. 用户可以创建团队，并自动成为团队管理员。
2. 团队管理员可以邀请、查看、调整和移除团队成员，同时保证团队至少保留一个管理员。
3. 团队成员可以创建项目，并自动成为项目经理。
4. 项目经理可以管理项目成员和项目角色。
5. 新项目自动创建默认看板列：待办、进行中、待验收、打回修改、已完成。

**Notes:**
- 角色模型要区分团队角色和项目角色。
- 看板列先服务任务状态闭环，不做复杂自定义列能力。

### Phase 3: 任务执行、日志与阻塞闭环

**Goal:** 让项目成员能真实推进任务，记录每日工作，主动暴露阻塞。  
**Mode:** mvp  
**Requirements:** TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, WORK-01, WORK-02, WORK-03, WORK-04, WORK-05, WORK-06  
**UI hint:** yes

**Success Criteria:**
1. 项目成员可以创建、编辑、软删除任务，并设置 Owner、参与者、任务类型、优先级、截止日期和标签。
2. 每个任务最多 5 名参与者，并始终保留明确 Owner。
3. 任务支持子任务、依赖关系和合法状态机流转。
4. 任务参与者可以记录工作日志，系统校验日期、工时和内容。
5. 成员可以标记阻塞并填写原因；未解除阻塞会阻止提交验收。
6. 阻塞任务会通知 Owner 或项目经理，并可进入站会阻塞报告的数据来源。

**Notes:**
- 阻塞不做主状态，避免状态机膨胀。
- 工作日志中的代码字段只作为手工/模拟证据预留。

### Phase 4: 证据门禁与人工验收核心

**Goal:** 建立 TTCS 的核心差异化能力：任务完成必须经过证据门禁和人工 Review。  
**Mode:** mvp  
**Requirements:** ACPT-01, ACPT-02, ACPT-03, ACPT-04, ACPT-05, ACPT-06, ACPT-07, ACPT-08, ACPT-09, ACPT-10, EVID-01, EVID-02, EVID-03, EVID-04, EVID-05, ARCH-05  
**UI hint:** yes

**Success Criteria:**
1. 系统按普通、文档、代码任务执行不同验收门禁，并返回结构化失败原因。
2. 任务参与者或 Owner 可以提交验收，但无法直接完成任务。
3. Owner 或项目经理可以通过、打回或要求补充证据。
4. 打回原因、补证要求、验收提交、门禁快照、Review 和证据引用均追加保存。
5. 文档任务可以关联上传文档作为证据。
6. 代码任务可以手工或模拟关联 Commit、PR/MR 或代码审核记录作为证据。
7. 验收提交、Review 决策和任务状态更新保持事务一致。

**Notes:**
- 真实 Git 同步和真实 AI/Agent 评审不进入本阶段。
- 代码审核通过只是证据，不等于任务完成。

### Phase 5: 工作台、通知与项目报表

**Goal:** 把个人执行、项目风险和验收质量聚合到可行动界面。  
**Mode:** mvp  
**Requirements:** DASH-01, DASH-02, DASH-03, NTFY-01, NTFY-02, RPT-01, RPT-02, RPT-03  
**UI hint:** yes

**Success Criteria:**
1. 个人工作台展示今日待办、待写日志、阻塞中、待提交验收、待我验收、被打回任务队列。
2. 待我验收只展示当前用户作为 Owner 或项目经理可处理的待验收任务。
3. 被打回任务展示最近打回原因和打回人。
4. 系统记录任务、评论、文件、工作日志、阻塞和验收相关活动。
5. WebSocket 或通知记录能推送关键事件，包括分配、提及、阻塞、提交验收、通过、打回和补证。
6. 项目报表展示进度、任务分布、工时统计、阻塞报告和验收统计。

**Notes:**
- 工作台优先做行动入口，不做静态大屏。
- 报表以 MVP 决策和演示为目标，先覆盖关键指标。

### Phase 6: MVP 验证、质量收口与演示准备

**Goal:** 对完整交付闭环做质量验证，确保系统能支撑演示和验收。  
**Mode:** mvp  
**Requirements:** QUAL-01, QUAL-02, QUAL-03  
**UI hint:** yes

**Success Criteria:**
1. 验收门禁检查单任务响应时间小于 500ms。
2. 工作台数据加载小于 1 秒。
3. 核心模块单元测试覆盖率达到或接近 70% 目标，并记录无法覆盖的风险。
4. 完成至少一条端到端演示路径：注册登录 -> 创建团队项目 -> 创建任务 -> 记录日志/阻塞 -> 解除阻塞 -> 提交验收 -> Review 通过 -> 报表可见。
5. 文档、配置和项目指引与实际实现保持一致。

**Notes:**
- 这一阶段不新增大功能，重点补齐验证、测试、性能和演示可用性。

## Requirement Coverage

| Phase | Requirements | Count |
|-------|--------------|-------|
| Phase 1 | AUTH-01..04, ARCH-01..04 | 8 |
| Phase 2 | TEAM-01..03, PROJ-01..03 | 6 |
| Phase 3 | TASK-01..08, WORK-01..06 | 14 |
| Phase 4 | ACPT-01..10, EVID-01..05, ARCH-05 | 16 |
| Phase 5 | DASH-01..03, NTFY-01..02, RPT-01..03 | 8 |
| Phase 6 | QUAL-01..03 | 3 |

**Coverage:**
- v1 requirements: 55 total
- Mapped to phases: 55
- Unmapped: 0

## Deferred Scope

The following are intentionally outside this v1 roadmap:

- Real GitHub/GitLab Webhook/API synchronization.
- Real AI/Agent code review calls.
- Full acceptance rule engine.
- External calendar synchronization and iCal import/export.
- Member homepage analytics.
- Document versioning and archive management.
- Multi-language UI.
- Mobile app.
- CI/CD integration.
- Microservice split.

---
*Roadmap created: 2026-05-17*
*Last updated: 2026-05-17 after initialization*
