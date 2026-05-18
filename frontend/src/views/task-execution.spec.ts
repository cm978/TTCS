import { shallowMount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BoardColumn from "../components/project/BoardColumn.vue";
import TaskCard from "../components/task/TaskCard.vue";
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
    expect(router.getRoutes().some((route) => route.path.includes("acceptance-reviews"))).toBe(false);
    expect(router.getRoutes().some((route) => route.path.includes("notifications"))).toBe(false);
    expect(router.getRoutes().some((route) => route.path.includes("reports"))).toBe(false);
  });
});
