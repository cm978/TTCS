import { shallowMount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BoardColumn from "../components/project/BoardColumn.vue";
import CreateTaskDrawer from "../components/task/CreateTaskDrawer.vue";
import SubtaskChecklist from "../components/task/SubtaskChecklist.vue";
import TaskDrawer from "../components/task/TaskDrawer.vue";
import TaskCard from "../components/task/TaskCard.vue";
import WorkLogForm from "../components/task/WorkLogForm.vue";
import router from "../router";
import type { TaskBoardCard } from "../types/task";

const task: TaskBoardCard = {
  id: 1,
  project_id: 10,
  column_id: 1,
  owner_id: 1,
  title: "修复阻塞接口",
  description: null,
  task_type: "CODE",
  status: "TODO",
  priority: "HIGH",
  due_date: null,
  labels: [],
  progress: 0,
  is_blocked: true,
  current_blocker_summary: "Waiting for route decision",
  acceptance_summary: null,
  deleted_at: null,
  created_at: "2026-05-18T00:00:00Z",
  updated_at: "2026-05-18T00:00:00Z",
  owner: {
    id: 1,
    email: "owner@example.com",
    display_name: "Owner",
    is_active: true,
    created_at: "2026-05-18T00:00:00Z"
  },
  participants: [],
  subtask_total: 2,
  subtask_completed: 1,
  latest_work_log_at: null,
  blocker_summary: { is_blocked: true, current_blocker_summary: "Waiting for route decision", unresolved_count: 1 }
};

describe("task execution UI", () => {
  it("renders API-backed task cards with blocker priority text", () => {
    const wrapper = shallowMount(TaskCard, { props: { task } });

    expect(wrapper.text()).toContain("修复阻塞接口");
    expect(wrapper.text()).toContain("阻塞中");
    expect(wrapper.text()).toContain("待写日志");
    expect(wrapper.text()).not.toContain("Waiting for route decision");
  });

  it("renders board columns with real tasks and scoped empty state", () => {
    const withTask = shallowMount(BoardColumn, {
      props: { column: { id: 1, project_id: 10, name: "待办", status: "TODO", position: 1 }, tasks: [task] }
    });
    const empty = shallowMount(BoardColumn, {
      props: { column: { id: 2, project_id: 10, name: "进行中", status: "IN_PROGRESS", position: 2 }, tasks: [] }
    });

    expect(withTask.text()).toContain("待办 · 1");
    expect(withTask.findComponent(TaskCard).props("task")).toMatchObject({ id: 1, title: "修复阻塞接口" });
    expect(empty.text()).toContain("当前列还没有真实任务。创建任务后，它会按状态出现在这里。");
    expect(empty.text()).not.toContain("后续阶段");
  });

  it("does not register premature acceptance review routes", () => {
    const taskRoute = router.getRoutes().find((route) => route.name === "task-detail");
    expect(taskRoute?.path).toBe("/tasks/:taskId");
    expect(taskRoute?.meta.requiresAuth).toBe(true);
    expect(router.getRoutes().some((route) => route.path.includes("acceptance-reviews"))).toBe(false);
    expect(router.getRoutes().some((route) => route.path.includes("notifications"))).toBe(false);
    expect(router.getRoutes().some((route) => route.path.includes("reports"))).toBe(false);
  });

  it("renders drawer detail action without acceptance review controls", () => {
    const wrapper = shallowMount(TaskDrawer, {
      props: {
        open: true,
        loading: false,
        saving: false,
        error: null,
        task: { ...task, subtasks: [], dependencies: [], work_logs: [], column: null }
      },
      global: {
        stubs: {
          "a-drawer": { template: "<div><slot name='title' /><slot /></div>" },
          "a-alert": { template: "<div><slot name='message' /></div>" },
          "a-form": { template: "<form><slot /></form>" },
          "a-form-item": { props: ["label", "extra"], template: "<label>{{ label }}<span>{{ extra }}</span><slot /></label>" },
          "a-select": { template: "<div><slot /></div>" },
          "a-select-option": { template: "<div><slot /></div>" },
          "a-tag": { template: "<span><slot /></span>" },
          "a-input": { template: "<input />" },
          "a-textarea": { template: "<textarea />" },
          "a-input-number": { template: "<input />" },
          "a-date-picker": { template: "<input />" },
          "a-checkbox": { template: "<label><slot /></label>" },
          "a-button": { template: "<button><slot /></button>" }
        }
      }
    });

    expect(wrapper.text()).toContain("打开完整详情");
    expect(wrapper.text()).toContain("截止日期");
    expect(wrapper.text()).toContain("记录工作日志");
    expect(wrapper.text()).toContain("标记阻塞");
    expect(wrapper.text()).not.toContain("验收通过");
    expect(wrapper.text()).not.toContain("Review");
  });

  it("renders visible work-log form labels and helper copy", () => {
    const wrapper = shallowMount(WorkLogForm, {
      props: { saving: false },
      global: {
        stubs: {
          "a-form": { template: "<form><slot /></form>" },
          "a-alert": { template: "<div><slot name='message' /></div>" },
          "a-form-item": { props: ["label", "extra"], template: "<label>{{ label }}<span>{{ extra }}</span><slot /></label>" },
          "a-input": { template: "<input />" },
          "a-textarea": { template: "<textarea />" },
          "a-input-number": { template: "<input />" },
          "a-date-picker": { template: "<input />" },
          "a-checkbox": { template: "<label><slot /></label>" },
          "a-button": { template: "<button><slot /></button>" }
        }
      }
    });

    expect(wrapper.text()).toContain("工作日期");
    expect(wrapper.text()).toContain("工时");
    expect(wrapper.text()).toContain("工作类型");
    expect(wrapper.text()).toContain("工作内容");
    expect(wrapper.text()).toContain("同时标记为阻塞");
    expect(wrapper.text()).toContain("代码证据（可选）");
    expect(wrapper.text()).toContain("仅手动记录，不会连接 Git 平台或自动校验提交。");
    expect(wrapper.text()).toContain("Commit Hash");
    expect(wrapper.text()).toContain("分支名称");
    expect(wrapper.text()).toContain("仓库地址");
  });

  it("opens a confirmed create-task drawer before submitting a task", async () => {
    const wrapper = shallowMount(CreateTaskDrawer, {
      props: { open: true, saving: false, ownerId: 7, error: null },
      global: {
        stubs: {
          "a-drawer": { template: "<div><slot name='title' /><slot /></div>" },
          "a-alert": { template: "<div><slot name='message' /></div>" },
          "a-form": { template: "<form><slot /></form>" },
          "a-form-item": { props: ["label"], template: "<label>{{ label }}<slot /></label>" },
          "a-input": { template: "<input />" },
          "a-textarea": { template: "<textarea />" },
          "a-select": { template: "<div><slot /></div>" },
          "a-select-option": { template: "<div><slot /></div>" },
          "a-date-picker": { template: "<input />" },
          "a-button": { template: "<button><slot /></button>" }
        }
      }
    });

    expect(wrapper.text()).toContain("任务标题");
    expect(wrapper.text()).toContain("截止日期");
    expect(wrapper.emitted("submit")).toBeUndefined();
  });

  it("emits real checkbox state when completing and uncompleting subtasks", async () => {
    const wrapper = shallowMount(SubtaskChecklist, {
      props: {
        subtasks: [
          {
            id: 11,
            task_id: 1,
            title: "补充验收截图",
            is_completed: false,
            completed_by_id: null,
            completed_at: null,
            position: 1,
            created_at: "2026-05-18T00:00:00Z",
            updated_at: "2026-05-18T00:00:00Z"
          }
        ],
        updatingId: null
      },
      global: {
        stubs: {
          "a-input": { template: "<input />" },
          "a-button": { template: "<button><slot /></button>" }
        }
      }
    });

    const checkbox = wrapper.find("input[type='checkbox']");
    await checkbox.setValue(true);

    expect(wrapper.emitted("toggle")?.[0]?.[1]).toBe(true);
  });

  it("renders blocker mode as a focused mark-blocked action", () => {
    const wrapper = shallowMount(WorkLogForm, {
      props: { saving: false, mode: "blocker" },
      global: {
        stubs: {
          "a-form": { template: "<form><slot /></form>" },
          "a-alert": { template: "<div><slot name='message' /></div>" },
          "a-form-item": { props: ["label", "extra"], template: "<label>{{ label }}<span>{{ extra }}</span><slot /></label>" },
          "a-textarea": { template: "<textarea />" },
          "a-button": { template: "<button><slot /></button>" }
        }
      }
    });

    expect(wrapper.text()).toContain("阻塞原因");
    expect(wrapper.text()).toContain("确认标记阻塞");
    expect(wrapper.text()).not.toContain("工作内容");
    expect(wrapper.text()).not.toContain("Commit Hash");
  });
});
