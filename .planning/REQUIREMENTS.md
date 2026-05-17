# 需求: TTCS

**定义日期:** 2026-05-17  
**核心价值:** 只有当可追溯证据和人工验收共同证明工作可交付时，任务才能进入完成状态。

## v1 需求

当前 v1 面向课程/演示优先 MVP，目标是交付“每日站会 + 个人执行 + 证据门禁验收”的完整闭环。

### 认证与用户

- [ ] **AUTH-01**: 用户可以通过邮箱和密码注册账号。
- [ ] **AUTH-02**: 用户可以通过邮箱和密码登录，并获得 JWT 会话。
- [ ] **AUTH-03**: 用户可以查看和编辑基础个人信息。
- [ ] **AUTH-04**: 用户密码以 bcrypt 哈希方式存储。

### 团队与项目

- [x] **TEAM-01**: 用户可以创建团队，并自动成为团队管理员。
- [x] **TEAM-02**: 团队管理员可以邀请成员加入团队。
- [x] **TEAM-03**: 团队管理员可以管理团队成员角色和移除成员。
- [x] **PROJ-01**: 团队成员可以创建项目，并自动成为项目经理。
- [x] **PROJ-02**: 项目经理可以管理项目成员和项目角色。
- [x] **PROJ-03**: 新项目默认包含待办、进行中、待验收、打回修改、已完成看板列。

### 任务与看板

- [ ] **TASK-01**: 项目成员可以创建任务，包含标题、描述、任务类型、优先级、截止日期、Owner、参与者、所属列和标签。
- [ ] **TASK-02**: 有权限的用户可以编辑任务基础信息。
- [ ] **TASK-03**: 项目经理可以软删除任务。
- [ ] **TASK-04**: 任务支持普通任务、文档任务、代码任务三种类型。
- [ ] **TASK-05**: 每个任务必须有明确 Owner，并最多支持 5 名参与者。
- [ ] **TASK-06**: 任务可以拆分为最多 3 级子任务，并基于子任务完成度自动计算进度。
- [ ] **TASK-07**: 任务可以设置同项目内依赖关系，并禁止循环依赖。
- [ ] **TASK-08**: 任务状态只能按待办、进行中、待验收、打回修改、已完成、已关闭的合法状态机流转。

### 工作日志与阻塞

- [ ] **WORK-01**: 任务参与者可以记录工作日志，包含日期、工时、工作内容和工作类型。
- [ ] **WORK-02**: 工作日志工时最小 0.5 小时，最大 24 小时。
- [ ] **WORK-03**: 工作日志可选关联 Commit Hash、分支名称和仓库地址，作为一期手工/模拟代码证据。
- [ ] **WORK-04**: 成员可以在工作日志中标记阻塞，并填写不少于 10 个字符的阻塞原因。
- [ ] **WORK-05**: 未解除阻塞会阻止任务提交验收。
- [ ] **WORK-06**: 阻塞任务必须进入每日站会阻塞报告并通知 Owner 或项目经理。

### 任务验收

- [ ] **ACPT-01**: 系统可以按任务类型查询验收门禁，并返回结构化失败原因。
- [ ] **ACPT-02**: 普通任务提交验收前必须满足子任务完成或验收说明、至少一条有效工作日志、无未解除阻塞、提交人有权限、验收说明不少于 10 个字符。
- [ ] **ACPT-03**: 文档任务提交验收前必须满足普通任务门禁，并关联至少一个可访问的交付文档或附件。
- [ ] **ACPT-04**: 代码任务提交验收前必须满足普通任务门禁，并关联至少一个 Commit、PR/MR 或代码审核记录。
- [ ] **ACPT-05**: 若代码任务关联代码审核记录，未解决评论数量必须为 0。
- [ ] **ACPT-06**: 任务参与者或 Owner 可以提交验收，但不能直接将任务置为已完成。
- [ ] **ACPT-07**: Owner 或项目经理可以通过验收、打回任务或要求补充证据。
- [ ] **ACPT-08**: 打回任务必须记录不少于 10 个字符的打回原因。
- [ ] **ACPT-09**: 要求补充证据时，任务保持待验收状态。
- [ ] **ACPT-10**: 验收提交、门禁快照、Review 记录、证据引用和打回原因必须追加保存，不得覆盖。

### 文档与代码证据

- [ ] **EVID-01**: 用户可以上传、下载和软删除项目文档或任务附件。
- [ ] **EVID-02**: 文档元数据、访问权限和任务证据关联必须保存到数据库。
- [ ] **EVID-03**: 文档任务可以将交付文档作为验收证据。
- [ ] **EVID-04**: 代码任务可以手工或模拟录入 Commit、PR/MR 和代码审核记录。
- [ ] **EVID-05**: 代码审核通过不等于任务完成，代码任务仍需通过任务验收 Review。

### 个人工作台、通知与报表

- [ ] **DASH-01**: 个人工作台展示今日待办、待写日志、阻塞中、待提交验收、待我验收和被打回任务队列。
- [ ] **DASH-02**: 待我验收仅展示当前用户作为 Owner 或项目经理可 Review 的待验收任务。
- [ ] **DASH-03**: 被打回任务必须展示最近一次打回原因和打回人。
- [ ] **NTFY-01**: 系统记录任务创建、编辑、删除、状态变更、评论、文件、工作日志、阻塞和验收活动。
- [ ] **NTFY-02**: 系统通过通知记录和 WebSocket 推送任务分配、@提及、阻塞、验收提交、通过、打回和补证请求。
- [ ] **RPT-01**: 项目报表展示项目进度、任务分布和工时统计。
- [ ] **RPT-02**: 阻塞任务报告按阻塞时长展示任务、原因、Owner 和影响验收状态。
- [ ] **RPT-03**: 验收统计展示待验收任务数、通过率、平均验收时长、打回次数，并按任务类型和成员聚合。

### 架构与质量

- [ ] **ARCH-01**: 前端使用 Vue 3、TypeScript、Vite、Pinia、Vue Router、Axios 和 Ant Design Vue。
- [ ] **ARCH-02**: 后端使用 Python 3.10+、FastAPI、SQLAlchemy、MySQL 8.0+ 和 Redis 7+。
- [ ] **ARCH-03**: API 使用 RESTful `/api/v1` JSON 风格，并使用 WebSocket 支撑实时通知。
- [ ] **ARCH-04**: MVP 保持单体 FastAPI 后端，不拆微服务。
- [ ] **ARCH-05**: 影响任务完成状态的任务流转、验收提交、Review 决策和证据快照必须在事务边界内保持一致。
- [ ] **QUAL-01**: 验收门禁检查单任务响应时间应小于 500ms。
- [ ] **QUAL-02**: 工作台数据加载应小于 1 秒。
- [ ] **QUAL-03**: 核心模块单元测试覆盖率目标不低于 70%。

## v2 需求

以下需求已确认方向，但不进入当前 v1 路线图。

### 日历与成员主页

- **CAL-01**: 支持日/周/月日历视图。
- **CAL-02**: 支持 iCal 导入导出、CalDAV 或 Google Calendar 同步。
- **MEMB-01**: 支持成员主页、成员统计、负责项目、最近工作日志和可见性细化。

### 文档与代码平台化

- **DOCV-01**: 支持文档版本、归档策略、容量管理和批量整理。
- **GIT-01**: 支持真实 GitHub/GitLab Webhook 自动同步 Commit、PR/MR 和代码状态。
- **GIT-02**: 支持代码浏览增强和 Diff 对比增强。

### 智能评审与规则扩展

- **AI-01**: 支持 AI/Agent 对代码任务输出变更摘要、风险点、测试建议和验收匹配度。
- **AI-02**: AI/Agent 评审只作为辅助证据，不拥有最终完成权。
- **RULE-01**: 支持项目级验收模板、任务类型自定义、多角色会签和验收风险评分。
- **I18N-01**: 支持英文界面和多语言体验。

## 暂不纳入

| 功能 | 原因 |
|------|------|
| 真实 Git 平台同步作为一期依赖 | 项目章程原本排除代码仓库集成；v1 仅保留手工/模拟代码证据以证明验收链路 |
| 真实 AI/Agent 评审调用 | 设计文档明确为二期能力，且不能拥有最终完成权 |
| 完整规则引擎 | MVP 使用明确任务类型门禁即可，规则引擎会增加实现复杂度 |
| 外部日历双向同步 | 与 v1 核心交付闭环关系弱，延后到二期 |
| 移动端 App | 当前只要求响应式 Web |
| CI/CD 集成 | 不属于当前 MVP 交付闭环 |
| 微服务拆分 | 当前模块事务耦合强，单体更适合快速交付和一致性控制 |

## 追踪矩阵

| 需求 | 阶段 | 状态 |
|------|------|------|
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| AUTH-03 | Phase 1 | Pending |
| AUTH-04 | Phase 1 | Pending |
| TEAM-01 | Phase 2 | Complete |
| TEAM-02 | Phase 2 | Complete |
| TEAM-03 | Phase 2 | Complete |
| PROJ-01 | Phase 2 | Complete |
| PROJ-02 | Phase 2 | Complete |
| PROJ-03 | Phase 2 | Complete |
| TASK-01 | Phase 3 | Pending |
| TASK-02 | Phase 3 | Pending |
| TASK-03 | Phase 3 | Pending |
| TASK-04 | Phase 3 | Pending |
| TASK-05 | Phase 3 | Pending |
| TASK-06 | Phase 3 | Pending |
| TASK-07 | Phase 3 | Pending |
| TASK-08 | Phase 3 | Pending |
| WORK-01 | Phase 3 | Pending |
| WORK-02 | Phase 3 | Pending |
| WORK-03 | Phase 3 | Pending |
| WORK-04 | Phase 3 | Pending |
| WORK-05 | Phase 3 | Pending |
| WORK-06 | Phase 3 | Pending |
| ACPT-01 | Phase 4 | Pending |
| ACPT-02 | Phase 4 | Pending |
| ACPT-03 | Phase 4 | Pending |
| ACPT-04 | Phase 4 | Pending |
| ACPT-05 | Phase 4 | Pending |
| ACPT-06 | Phase 4 | Pending |
| ACPT-07 | Phase 4 | Pending |
| ACPT-08 | Phase 4 | Pending |
| ACPT-09 | Phase 4 | Pending |
| ACPT-10 | Phase 4 | Pending |
| EVID-01 | Phase 4 | Pending |
| EVID-02 | Phase 4 | Pending |
| EVID-03 | Phase 4 | Pending |
| EVID-04 | Phase 4 | Pending |
| EVID-05 | Phase 4 | Pending |
| DASH-01 | Phase 5 | Pending |
| DASH-02 | Phase 5 | Pending |
| DASH-03 | Phase 5 | Pending |
| NTFY-01 | Phase 5 | Pending |
| NTFY-02 | Phase 5 | Pending |
| RPT-01 | Phase 5 | Pending |
| RPT-02 | Phase 5 | Pending |
| RPT-03 | Phase 5 | Pending |
| ARCH-01 | Phase 1 | Pending |
| ARCH-02 | Phase 1 | Pending |
| ARCH-03 | Phase 1 | Pending |
| ARCH-04 | Phase 1 | Pending |
| ARCH-05 | Phase 4 | Pending |
| QUAL-01 | Phase 6 | Pending |
| QUAL-02 | Phase 6 | Pending |
| QUAL-03 | Phase 6 | Pending |

**覆盖率:**
- v1 需求: 55 total
- 已映射到阶段: 55
- 未映射: 0

---
*需求定义: 2026-05-17*
*最后更新: 2026-05-17，初始化后*
