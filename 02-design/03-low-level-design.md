# 详细设计说明书

**文档编号：** LLD-2026-001  
**版本号：** V1.0  
**密级：** 内部公开  
**编制日期：** 2026-05-17  
**关联需求：** `01-requirements/02-srs.md` V2.4  
**关联概要设计：** `02-design/02-high-level-design.md`  
**关联专项设计：** `02-design/01-task-acceptance-design.md`

---

## 修订历史

| 版本 | 日期 | 修改说明 |
|------|------|---------|
| V1.0 | 2026-05-17 | 初始版本，补充一期 MVP 后端、前端、状态机、服务、接口和关键算法详细设计 |

---

## 1. 引言

### 1.1 目的

本文档在概要设计基础上细化 TTCS 一期 MVP 的模块内部设计，明确主要类、服务方法、状态机、权限判断、验收门禁算法、API 数据结构、前端组件和错误处理方式。

本文档用于指导编码、单元测试、接口测试和后续数据库/API 设计。

### 1.2 设计范围

本文档重点覆盖一期 MVP：

- 用户认证、团队、项目、任务、工作日志。
- 任务状态流转和证据门禁验收。
- 个人工作台行动队列。
- 通知与活动。
- 文档交付物证据。
- 代码任务的手工/模拟代码证据。

二期能力仅保留接口、数据结构和适配层说明：

- 真实 Git API/Webhook 同步。
- AI/Agent 辅助评审。
- 日历、成员主页、规则引擎。

## 2. 工程结构设计

### 2.1 后端目录结构

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── teams.py
│   │       ├── projects.py
│   │       ├── tasks.py
│   │       ├── work_logs.py
│   │       ├── acceptance.py
│   │       ├── documents.py
│   │       ├── code.py
│   │       ├── reports.py
│   │       ├── workspace.py
│   │       └── notifications.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── permissions.py
│   │   ├── errors.py
│   │   └── enums.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   ├── models/
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── work_log.py
│   │   ├── acceptance.py
│   │   ├── document.py
│   │   ├── code.py
│   │   └── notification.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── task.py
│   │   ├── acceptance.py
│   │   ├── workspace.py
│   │   └── common.py
│   ├── repositories/
│   │   ├── task_repository.py
│   │   ├── acceptance_repository.py
│   │   ├── work_log_repository.py
│   │   └── project_repository.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   ├── task_state_service.py
│   │   ├── acceptance_gate_service.py
│   │   ├── acceptance_submission_service.py
│   │   ├── acceptance_review_service.py
│   │   ├── acceptance_evidence_service.py
│   │   ├── work_log_service.py
│   │   ├── notification_service.py
│   │   ├── workspace_service.py
│   │   └── report_service.py
│   └── integrations/
│       ├── storage.py
│       ├── git_provider.py
│       └── ai_review_provider.py
├── tests/
└── pyproject.toml
```

### 2.2 前端目录结构

```text
frontend/
├── src/
│   ├── main.ts
│   ├── router/
│   │   └── index.ts
│   ├── stores/
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   ├── task.ts
│   │   ├── workspace.ts
│   │   └── notification.ts
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── tasks.ts
│   │   ├── acceptance.ts
│   │   ├── workspace.ts
│   │   └── reports.ts
│   ├── layouts/
│   │   └── AppLayout.vue
│   ├── views/
│   │   ├── LoginView.vue
│   │   ├── WorkspaceView.vue
│   │   ├── ProjectBoardView.vue
│   │   ├── TaskDetailView.vue
│   │   └── ReportsView.vue
│   ├── components/
│   │   ├── task/
│   │   │   ├── TaskCard.vue
│   │   │   ├── TaskStatusTag.vue
│   │   │   └── TaskEvidenceList.vue
│   │   ├── acceptance/
│   │   │   ├── AcceptancePanel.vue
│   │   │   ├── AcceptanceGateChecklist.vue
│   │   │   ├── SubmitAcceptanceModal.vue
│   │   │   ├── ReviewAcceptanceModal.vue
│   │   │   └── AcceptanceHistory.vue
│   │   ├── workspace/
│   │   │   ├── ActionQueue.vue
│   │   │   └── ProjectProgressList.vue
│   │   └── notification/
│   │       └── NotificationBell.vue
│   └── types/
│       ├── task.ts
│       ├── acceptance.ts
│       └── common.ts
└── package.json
```

## 3. 枚举与常量设计

### 3.1 任务相关枚举

```python
class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    REJECTED = "REJECTED"
    DONE = "DONE"
    CLOSED = "CLOSED"
    DELETED = "DELETED"

class TaskType(str, Enum):
    GENERAL = "GENERAL"
    DOCUMENT = "DOCUMENT"
    CODE = "CODE"

class TaskPriority(str, Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
```

状态显示映射：

| 后端枚举 | 中文显示 | 看板列 |
|----------|----------|--------|
| TODO | 待办 | 待办 |
| IN_PROGRESS | 进行中 | 进行中 |
| IN_REVIEW | 待验收 | 待验收 |
| REJECTED | 打回修改 | 打回修改 |
| DONE | 已完成 | 已完成 |
| CLOSED | 已关闭 | 不默认显示 |
| DELETED | 已删除 | 不显示 |

### 3.2 验收相关枚举

```python
class AcceptanceSubmissionStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEED_EVIDENCE = "NEED_EVIDENCE"

class AcceptanceReviewResult(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEED_EVIDENCE = "NEED_EVIDENCE"

class EvidenceType(str, Enum):
    SUBTASK = "SUBTASK"
    WORK_LOG = "WORK_LOG"
    DOCUMENT = "DOCUMENT"
    ATTACHMENT = "ATTACHMENT"
    COMMIT = "COMMIT"
    PR = "PR"
    CODE_REVIEW = "CODE_REVIEW"
    AI_REVIEW = "AI_REVIEW"
```

### 3.3 通知类型

```python
class NotificationType(str, Enum):
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_BLOCKED = "TASK_BLOCKED"
    ACCEPTANCE_SUBMITTED = "ACCEPTANCE_SUBMITTED"
    ACCEPTANCE_APPROVED = "ACCEPTANCE_APPROVED"
    ACCEPTANCE_REJECTED = "ACCEPTANCE_REJECTED"
    ACCEPTANCE_NEED_EVIDENCE = "ACCEPTANCE_NEED_EVIDENCE"
    MENTIONED = "MENTIONED"
    COMMENT_REPLIED = "COMMENT_REPLIED"
```

## 4. 数据模型详细设计

本节描述逻辑字段。物理字段类型、索引和约束在后续数据库设计文档中细化。

### 4.1 Task

| 字段 | 说明 |
|------|------|
| id | 任务 ID |
| project_id | 所属项目 |
| column_id | 当前看板列 |
| owner_id | 任务 Owner |
| title | 标题 |
| description | 描述 |
| task_type | GENERAL、DOCUMENT、CODE |
| status | TODO、IN_PROGRESS、IN_REVIEW、REJECTED、DONE、CLOSED、DELETED |
| priority | 优先级 |
| due_date | 截止日期 |
| progress | 子任务计算进度 |
| is_blocked | 是否存在未解除阻塞 |
| blocked_reason | 最近阻塞原因 |
| submitted_at | 最近提交验收时间 |
| accepted_at | 验收通过时间 |
| accepted_by | 验收人 |
| rejection_count | 打回次数 |
| deleted_at | 软删除时间 |
| created_at / updated_at | 创建/更新时间 |

### 4.2 TaskAssignee

| 字段 | 说明 |
|------|------|
| id | 主键 |
| task_id | 任务 ID |
| user_id | 参与者 ID |
| role | PARTICIPANT、WATCHER |
| created_at | 创建时间 |

业务约束：

- 每个任务最多 5 名 `PARTICIPANT`。
- Owner 可以不在参与者列表中，但建议创建任务时自动加入。

### 4.3 WorkLog

| 字段 | 说明 |
|------|------|
| id | 主键 |
| task_id | 任务 ID |
| user_id | 记录人 |
| work_date | 工作日期 |
| hours | 工时 |
| content | 工作内容 |
| work_type | 开发、测试、文档、沟通等 |
| is_blocked | 是否阻塞 |
| blocked_reason | 阻塞原因 |
| resolved_at | 阻塞解除时间 |
| commit_hash | 代码提交哈希，一期可手工录入 |
| branch_name | 分支名 |
| repository_url | 仓库地址 |
| git_synced | 是否由 Git 同步生成 |
| created_at / updated_at | 创建/更新时间 |

### 4.4 AcceptanceSubmission

| 字段 | 说明 |
|------|------|
| id | 主键 |
| task_id | 任务 ID |
| submitted_by | 提交人 |
| summary | 验收说明、功能自测说明或变更摘要 |
| gate_snapshot | 门禁检查快照 JSON |
| status | SUBMITTED、APPROVED、REJECTED、NEED_EVIDENCE |
| created_at | 提交时间 |

设计说明：

- 每次提交验收创建一条新记录。
- 被打回后重新提交时，不覆盖历史记录。
- `gate_snapshot` 记录当时的检查结果，避免后续证据变化导致历史不可追溯。

### 4.5 AcceptanceReview

| 字段 | 说明 |
|------|------|
| id | 主键 |
| submission_id | 验收提交 ID |
| task_id | 任务 ID |
| reviewer_id | Review 人 |
| result | APPROVED、REJECTED、NEED_EVIDENCE |
| comment | Review 说明 |
| created_at | Review 时间 |

### 4.6 AcceptanceEvidence

| 字段 | 说明 |
|------|------|
| id | 主键 |
| task_id | 任务 ID |
| submission_id | 可选，关联提交批次 |
| evidence_type | SUBTASK、WORK_LOG、DOCUMENT、COMMIT、PR、CODE_REVIEW 等 |
| ref_id | 内部业务记录 ID |
| ref_url | 外部链接 |
| title | 证据标题 |
| metadata | 证据快照 JSON |
| created_at | 创建时间 |

### 4.7 CodeReview

一期 CodeReview 支持模拟或手工录入。

| 字段 | 说明 |
|------|------|
| id | 主键 |
| project_id | 项目 ID |
| task_id | 可选，关联任务 |
| pr_url | PR/MR 链接 |
| title | 审核标题 |
| author_id | 作者 |
| status | PENDING、IN_REVIEW、APPROVED、REJECTED |
| unresolved_comment_count | 未解决评论数 |
| created_at / updated_at | 创建/更新时间 |

## 5. 后端服务详细设计

### 5.1 AuthService

| 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|
| `register(command)` | 邮箱、密码、姓名 | 用户 ID | 创建账号、发送验证邮件 |
| `login(command)` | 邮箱、密码 | Access Token | 校验密码并签发 JWT |
| `get_current_user(token)` | JWT | User | 解析当前用户 |

### 5.2 PermissionService

统一封装权限判断，避免权限散落在路由层。

| 方法 | 说明 |
|------|------|
| `ensure_project_member(user_id, project_id)` | 校验用户为项目成员 |
| `ensure_task_visible(user_id, task_id)` | 校验任务可见 |
| `ensure_task_editable(user_id, task_id)` | 校验任务可编辑 |
| `ensure_task_participant_or_owner(user_id, task_id)` | 校验可提交验收 |
| `ensure_acceptance_reviewer(user_id, task_id)` | 校验 Owner 或项目经理 Review 权限 |

权限伪代码：

```python
def ensure_acceptance_reviewer(user_id: int, task: Task) -> None:
    if task.owner_id == user_id:
        return
    if project_member_repo.has_role(user_id, task.project_id, "PROJECT_MANAGER"):
        return
    raise ForbiddenError("NO_ACCEPTANCE_REVIEW_PERMISSION")
```

### 5.3 TaskService

| 方法 | 说明 |
|------|------|
| `create_task(command, actor)` | 创建任务、Owner、参与者、默认状态 |
| `update_task(task_id, command, actor)` | 编辑任务基础信息 |
| `delete_task(task_id, actor)` | 软删除任务 |
| `change_status(task_id, target_status, actor)` | 任务状态流转 |
| `add_assignee(task_id, user_id, actor)` | 添加参与者，校验最多 5 人 |
| `remove_assignee(task_id, user_id, actor)` | 移除参与者 |
| `recalculate_progress(task_id)` | 按子任务完成度计算进度 |

`change_status` 约束：

- 参与者可执行 `TODO -> IN_PROGRESS`。
- 参与者不能直接执行 `IN_PROGRESS -> DONE`。
- `IN_PROGRESS/REJECTED -> IN_REVIEW` 必须通过 AcceptanceSubmissionService。
- `IN_REVIEW -> DONE/REJECTED` 必须通过 AcceptanceReviewService。

### 5.4 WorkLogService

| 方法 | 说明 |
|------|------|
| `create_work_log(task_id, command, actor)` | 创建工作日志 |
| `update_work_log(log_id, command, actor)` | 24 小时内编辑 |
| `resolve_blocker(log_id, actor)` | 解除阻塞 |
| `list_task_logs(task_id, actor)` | 查询任务日志 |

创建工作日志流程：

```text
校验任务可见
校验 actor 是任务参与者或 Owner
校验工时范围和工作日期
若 is_blocked=true，校验 blocked_reason >= 10 字符
写入 work_logs
若阻塞，更新 tasks.is_blocked=true
记录 activity_log
提交事务
发送阻塞通知
```

### 5.5 AcceptanceGateService

职责：根据任务类型返回门禁检查结果。

主要方法：

```python
def evaluate(task_id: int, actor: User) -> AcceptanceGateResult:
    task = task_repo.get(task_id)
    permission.ensure_task_participant_or_owner(actor.id, task_id)

    checks = [
        check_actor_can_submit(task, actor),
        check_no_unresolved_blocker(task),
        check_work_log_exists(task),
        check_summary_policy(task),
    ]

    if task.task_type == TaskType.GENERAL:
        checks += check_general_task(task)
    elif task.task_type == TaskType.DOCUMENT:
        checks += check_document_task(task)
    elif task.task_type == TaskType.CODE:
        checks += check_code_task(task)

    return AcceptanceGateResult.from_checks(checks)
```

检查项定义：

| 检查码 | 适用任务 | 通过条件 |
|--------|----------|----------|
| ACTOR_CAN_SUBMIT | 全部 | 用户是任务参与者或 Owner |
| SUBTASKS_COMPLETED | 全部 | 有子任务时全部完成 |
| SUMMARY_REQUIRED | 全部 | 无子任务或代码任务时提供说明 |
| WORK_LOG_REQUIRED | 全部 | 至少 1 条有效工作日志 |
| BLOCKER_UNRESOLVED | 全部 | 不存在未解除阻塞 |
| DOCUMENT_REQUIRED | 文档任务 | 至少 1 个可访问交付文档 |
| CODE_EVIDENCE_REQUIRED | 代码任务 | 至少 1 个 Commit、PR/MR 或 CodeReview |
| CODE_REVIEW_COMMENTS_OPEN | 代码任务 | 未解决评论数为 0 |

### 5.6 AcceptanceSubmissionService

| 方法 | 说明 |
|------|------|
| `submit(task_id, command, actor)` | 提交验收 |
| `list_submissions(task_id, actor)` | 查询验收历史 |

提交验收算法：

```text
1. 开启事务
2. 查询任务并加行级锁
3. 校验任务状态必须为 IN_PROGRESS 或 REJECTED
4. 执行 AcceptanceGateService.evaluate
5. 若门禁失败，返回 failed_checks，不创建提交记录
6. 收集 AcceptanceEvidence 快照
7. 创建 AcceptanceSubmission(status=SUBMITTED)
8. 写入证据快照
9. 更新任务状态为 IN_REVIEW，submitted_at=now
10. 记录 ActivityLog
11. 提交事务
12. 通知 Owner 和项目经理
```

状态限制：

- `DONE`、`CLOSED`、`DELETED` 任务不能提交验收。
- `IN_REVIEW` 任务重复提交应返回冲突错误。
- `REJECTED` 任务可重新提交，创建新的提交记录。

### 5.7 AcceptanceEvidenceService

| 方法 | 说明 |
|------|------|
| `collect_for_submission(task_id)` | 收集提交时证据快照 |
| `list_task_evidence(task_id, actor)` | 查询任务证据 |
| `add_manual_code_evidence(task_id, command, actor)` | 一期手工添加代码证据 |

证据收集规则：

- 子任务：记录子任务 ID、标题、完成状态、完成人。
- 工作日志：记录日志 ID、日期、工时、摘要、是否阻塞。
- 文档：记录文档 ID、文件名、URL、上传人。
- 代码：记录 commit hash、PR URL、CodeReview 状态。

### 5.8 AcceptanceReviewService

| 方法 | 说明 |
|------|------|
| `review(task_id, command, actor)` | 通过、打回、要求补充证据 |

Review 算法：

```text
1. 开启事务
2. 查询任务并加行级锁
3. 校验任务状态为 IN_REVIEW
4. 校验 actor 为 Owner 或项目经理
5. 查询最新 SUBMITTED 状态的 AcceptanceSubmission
6. 根据 result 创建 AcceptanceReview
7. 若 APPROVED：
   - submission.status = APPROVED
   - task.status = DONE
   - task.accepted_at = now
   - task.accepted_by = actor.id
8. 若 REJECTED：
   - 校验 comment >= 10 字符
   - submission.status = REJECTED
   - task.status = REJECTED
   - task.rejection_count += 1
9. 若 NEED_EVIDENCE：
   - 校验 comment >= 10 字符
   - submission.status = NEED_EVIDENCE
   - task.status 保持 IN_REVIEW
10. 记录 ActivityLog
11. 提交事务
12. 通知任务参与者
```

### 5.9 WorkspaceService

| 方法 | 说明 |
|------|------|
| `get_dashboard(user_id)` | 聚合个人工作台数据 |
| `get_action_queues(user_id)` | 查询行动队列 |

行动队列查询：

| 队列 | 查询条件 |
|------|----------|
| 今日待办 | 参与任务，截止日期为今日，状态非 DONE/CLOSED |
| 待写工作日志 | 参与任务，今日无工作日志，状态 IN_PROGRESS/REJECTED |
| 阻塞中 | 参与任务或 Owner，`is_blocked=true` |
| 待提交验收 | 参与任务，状态 IN_PROGRESS/REJECTED，门禁接近满足或用户主动筛选 |
| 待我验收 | 当前用户为 Owner 或项目经理，任务状态 IN_REVIEW |
| 被打回 | 参与任务，状态 REJECTED |

### 5.10 NotificationService

| 方法 | 说明 |
|------|------|
| `create_notification(event)` | 创建通知 |
| `push_to_user(user_id, payload)` | WebSocket 推送 |
| `mark_read(notification_id, user_id)` | 标记已读 |

发送策略：

- Service 层只发布领域事件。
- NotificationService 消费事件并写入通知。
- WebSocket 推送失败不回滚业务。

## 6. API 详细设计

### 6.1 通用响应

成功响应：

```json
{
  "success": true,
  "data": {}
}
```

失败响应：

```json
{
  "success": false,
  "error": {
    "code": "NO_ACCEPTANCE_REVIEW_PERMISSION",
    "message": "当前用户无权审核该任务",
    "details": {}
  }
}
```

### 6.2 查询验收门禁

```http
GET /api/v1/tasks/{task_id}/acceptance-gate
```

响应：

```json
{
  "success": true,
  "data": {
    "task_id": 1001,
    "task_type": "CODE",
    "can_submit": false,
    "checks": [
      {
        "code": "WORK_LOG_REQUIRED",
        "passed": true,
        "message": "已存在有效工作日志"
      },
      {
        "code": "CODE_EVIDENCE_REQUIRED",
        "passed": false,
        "message": "代码任务至少需要关联 1 个 Commit、PR/MR 或代码审核记录"
      }
    ]
  }
}
```

### 6.3 提交验收

```http
POST /api/v1/tasks/{task_id}/acceptance-submissions
```

请求：

```json
{
  "summary": "登录 API 已完成联调，子任务全部关闭，已关联 PR #18。"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "submission_id": 501,
    "task_id": 1001,
    "status": "SUBMITTED",
    "task_status": "IN_REVIEW"
  }
}
```

### 6.4 Review 验收

```http
POST /api/v1/tasks/{task_id}/acceptance-reviews
```

请求：

```json
{
  "submission_id": 501,
  "result": "REJECTED",
  "comment": "登录失败时缺少错误提示，请补充异常场景截图和自测说明。"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "review_id": 9001,
    "task_status": "REJECTED",
    "rejection_count": 1
  }
}
```

### 6.5 工作台行动队列

```http
GET /api/v1/workspace/action-queues
```

响应：

```json
{
  "success": true,
  "data": {
    "todo_today": [],
    "need_work_log": [],
    "blocked": [],
    "ready_to_submit": [],
    "waiting_my_review": [],
    "rejected": []
  }
}
```

## 7. 错误码设计

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| TASK_NOT_FOUND | 404 | 任务不存在 |
| TASK_NOT_VISIBLE | 403 | 无权查看任务 |
| INVALID_TASK_STATUS_TRANSITION | 400 | 非法任务状态流转 |
| TASK_ALREADY_IN_REVIEW | 409 | 任务已在待验收状态 |
| TASK_CANNOT_SUBMIT_ACCEPTANCE | 400 | 当前状态不可提交验收 |
| ACCEPTANCE_GATE_FAILED | 400 | 验收门禁未通过 |
| ACCEPTANCE_SUBMISSION_NOT_FOUND | 404 | 验收提交不存在 |
| NO_ACCEPTANCE_REVIEW_PERMISSION | 403 | 无权 Review 任务 |
| ACCEPTANCE_REJECT_COMMENT_REQUIRED | 400 | 打回或补充证据必须填写原因 |
| CODE_EVIDENCE_REQUIRED | 400 | 代码任务缺少代码证据 |
| DOCUMENT_EVIDENCE_REQUIRED | 400 | 文档任务缺少交付文档 |
| BLOCKER_UNRESOLVED | 400 | 存在未解除阻塞 |
| WORK_LOG_REQUIRED | 400 | 缺少工作日志 |

## 8. 前端详细设计

### 8.1 路由

| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录页 | 未登录 |
| `/workspace` | 个人工作台 | 已登录 |
| `/projects/:projectId/board` | 项目看板 | 项目成员 |
| `/tasks/:taskId` | 任务详情 | 任务可见 |
| `/projects/:projectId/reports` | 项目报表 | 项目成员 |

### 8.2 TaskDetailView

页面区域：

- 任务基础信息。
- 子任务列表。
- 工作日志。
- 附件和文档。
- 代码证据。
- 验收面板。
- 活动动态。

### 8.3 AcceptancePanel

职责：

- 加载验收门禁。
- 展示检查项通过/失败状态。
- 展示证据列表。
- 提供提交验收按钮。
- 对 Owner/项目经理展示 Review 操作。

组件状态：

| 状态 | UI 行为 |
|------|---------|
| loading | 显示骨架屏 |
| can_submit=false | 禁用提交按钮，展示失败检查项 |
| can_submit=true | 启用提交验收 |
| task.status=IN_REVIEW 且可 Review | 显示通过、打回、补充证据按钮 |
| task.status=REJECTED | 展示最近打回原因和重新提交入口 |
| task.status=DONE | 展示验收通过人、时间和证据快照 |

### 8.4 AcceptanceGateChecklist

展示字段：

- 检查项名称。
- 是否通过。
- 失败原因。
- 跳转操作，例如“去记录工作日志”“上传文档”“关联 PR”。

### 8.5 ReviewAcceptanceModal

输入：

- Review 结果：通过、打回、要求补充证据。
- Review 说明。

校验：

- 打回和要求补充证据时说明不少于 10 字符。
- 通过时说明可选，但建议填写。

### 8.6 WorkspaceView

工作台布局：

- 左侧或上方：今日行动队列。
- 中部：我的项目进度。
- 右侧：最近活动和通知。

行动队列优先级：

1. 被打回任务。
2. 待我验收。
3. 阻塞中任务。
4. 今日截止任务。
5. 待写工作日志。
6. 待提交验收。

## 9. 状态机详细设计

### 9.1 状态流转表

| 当前状态 | 目标状态 | 触发动作 | 允许角色 |
|----------|----------|----------|----------|
| TODO | IN_PROGRESS | 开始任务 | 参与者、Owner、项目经理 |
| IN_PROGRESS | IN_REVIEW | 提交验收 | 参与者、Owner |
| REJECTED | IN_REVIEW | 重新提交验收 | 参与者、Owner |
| IN_REVIEW | DONE | 通过验收 | Owner、项目经理 |
| IN_REVIEW | REJECTED | 打回任务 | Owner、项目经理 |
| DONE | CLOSED | 关闭任务 | Owner、项目经理 |

### 9.2 禁止流转

| 禁止流转 | 原因 |
|----------|------|
| IN_PROGRESS -> DONE | 必须经过验收 |
| TODO -> DONE | 必须经过执行和验收 |
| REJECTED -> DONE | 必须重新提交验收 |
| IN_REVIEW -> IN_PROGRESS | 必须通过打回进入 REJECTED |
| CLOSED -> 任意状态 | 已关闭任务不可重新打开，一期不支持 |

### 9.3 状态机伪代码

```python
ALLOWED_TRANSITIONS = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS},
    TaskStatus.IN_PROGRESS: {TaskStatus.IN_REVIEW},
    TaskStatus.REJECTED: {TaskStatus.IN_REVIEW},
    TaskStatus.IN_REVIEW: {TaskStatus.DONE, TaskStatus.REJECTED},
    TaskStatus.DONE: {TaskStatus.CLOSED},
}

def validate_transition(task: Task, target: TaskStatus, actor: User) -> None:
    if target not in ALLOWED_TRANSITIONS.get(task.status, set()):
        raise BadRequestError("INVALID_TASK_STATUS_TRANSITION")

    if target == TaskStatus.IN_REVIEW:
        permission.ensure_task_participant_or_owner(actor.id, task.id)
    elif target in {TaskStatus.DONE, TaskStatus.REJECTED}:
        permission.ensure_acceptance_reviewer(actor.id, task)
```

## 10. 关键算法

### 10.1 任务进度计算

```python
def calculate_task_progress(task_id: int) -> int:
    subtasks = subtask_repo.list_by_task(task_id)
    if not subtasks:
        return 0
    completed = sum(1 for item in subtasks if item.is_completed)
    return round(completed / len(subtasks) * 100)
```

### 10.2 验收门禁聚合

```python
def build_gate_result(checks: list[GateCheck]) -> AcceptanceGateResult:
    return AcceptanceGateResult(
        can_submit=all(check.passed for check in checks),
        checks=checks,
        failed_checks=[check for check in checks if not check.passed],
    )
```

### 10.3 工作台行动队列排序

```python
ACTION_QUEUE_ORDER = [
    "rejected",
    "waiting_my_review",
    "blocked",
    "todo_today",
    "need_work_log",
    "ready_to_submit",
]
```

队列内排序规则：

1. 逾期任务优先。
2. 高优先级任务优先。
3. 阻塞时长更久的任务优先。
4. 最近更新时间更早的任务优先。

## 11. 测试设计

### 11.1 单元测试

| 模块 | 测试重点 |
|------|----------|
| TaskStateService | 合法/非法状态流转 |
| AcceptanceGateService | 普通/文档/代码任务门禁 |
| AcceptanceSubmissionService | 提交验收事务和证据快照 |
| AcceptanceReviewService | 通过、打回、补充证据 |
| PermissionService | Owner、项目经理、参与者权限 |
| WorkspaceService | 行动队列筛选和排序 |

### 11.2 集成测试

| 场景 | 预期 |
|------|------|
| 普通任务无工作日志提交验收 | 返回 `ACCEPTANCE_GATE_FAILED` |
| 文档任务无文档提交验收 | 返回 `DOCUMENT_EVIDENCE_REQUIRED` |
| 代码任务无代码证据提交验收 | 返回 `CODE_EVIDENCE_REQUIRED` |
| 待验收任务由参与者通过 | 返回 403 |
| Owner 打回任务 | 状态变为 REJECTED，打回次数 +1 |
| 被打回任务重新提交 | 新建提交记录，历史保留 |
| 阻塞未解除提交验收 | 返回 `BLOCKER_UNRESOLVED` |

### 11.3 Demo 验收脚本

建议准备 3-5 人样例数据：

- 张三：项目经理。
- 李四：后端开发，负责代码任务。
- 王五：测试人员，负责测试任务。
- 赵六：产品/文档负责人，负责文档任务。

演示路径：

1. 李四在工作台看到今日代码任务。
2. 李四记录工作日志并关联模拟 PR。
3. 系统门禁检查通过，李四提交验收。
4. 张三在“待我验收”看到任务。
5. 张三打回任务，要求补充异常场景说明。
6. 李四补充说明并重新提交。
7. 张三通过验收，任务进入已完成。
8. 报表显示验收统计和打回次数。

## 12. 二期扩展点

| 扩展点 | 一期预留 | 二期实现 |
|--------|----------|----------|
| Git 同步 | CodeEvidence 手工/模拟记录 | GitHub/GitLab API + Webhook |
| AI/Agent 评审 | ai_review_reports 表和 API 入口 | 真实 Agent 调用和报告生成 |
| 验收规则 | 固定三类任务门禁 | 项目级规则模板 |
| 多角色会签 | 单 Owner/项目经理 Review | 多角色并行/串行 Review |
| 日历 | 仅任务截止日期字段 | 日/周/月视图和外部同步 |

## 13. 实现顺序建议

1. 建立后端基础工程、数据库连接、认证和错误响应。
2. 实现用户、团队、项目基础模型。
3. 实现任务、参与者、子任务、状态机。
4. 实现工作日志和阻塞标记。
5. 实现任务验收门禁、提交、Review、证据快照。
6. 实现个人工作台行动队列。
7. 实现通知与活动。
8. 实现文档证据和代码证据的手工/模拟录入。
9. 实现报表统计。
10. 补齐前端任务详情、验收面板和工作台页面。

## 14. 结论

TTCS 一期详细设计围绕“任务从执行到验收完成”的真实闭环展开。实现时应优先保证以下约束：

- 参与者不能直接完成任务。
- 提交验收前必须通过分类型门禁。
- Owner 或项目经理才拥有最终完成权。
- 打回和重新提交必须保留历史。
- 工作台必须展示行动队列，而不是只展示统计卡片。
- AI/Agent 评审只作为二期辅助能力，不影响一期主流程。
