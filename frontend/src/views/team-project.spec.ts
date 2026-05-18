import { createPinia, setActivePinia } from "pinia";
import { shallowMount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import BoardColumn from "../components/project/BoardColumn.vue";
import ProjectMemberDrawer from "../components/project/ProjectMemberDrawer.vue";
import TeamMemberTable from "../components/team/TeamMemberTable.vue";
import { createProject, listProjects } from "../api/projects";
import { createTeam, listMyInvitations, listTeams } from "../api/teams";
import { useProjectStore } from "../stores/project";
import { useTeamStore } from "../stores/team";

vi.mock("../api/teams", () => ({
  acceptInvitation: vi.fn(),
  cancelInvitation: vi.fn(),
  createTeam: vi.fn(),
  inviteTeamMember: vi.fn(),
  listMyInvitations: vi.fn(),
  listTeamInvitations: vi.fn(),
  listTeamMembers: vi.fn(),
  listTeams: vi.fn(),
  removeTeamMember: vi.fn(),
  updateTeamMemberRole: vi.fn()
}));

vi.mock("../api/projects", () => ({
  addProjectMember: vi.fn(),
  createProject: vi.fn(),
  getProjectBoard: vi.fn(),
  listProjectMembers: vi.fn(),
  listProjects: vi.fn(),
  removeProjectMember: vi.fn(),
  updateProjectMemberRole: vi.fn()
}));

const team = {
  id: 1,
  name: "Demo Team",
  description: null,
  created_by_id: 1,
  created_at: "2026-05-17T00:00:00Z"
};

const project = {
  id: 10,
  team_id: 1,
  name: "Launch",
  description: null,
  start_date: null,
  end_date: null,
  created_by_id: 1,
  created_at: "2026-05-17T00:00:00Z"
};

const user = {
  id: 1,
  email: "manager@example.com",
  display_name: "Manager",
  is_active: true,
  created_at: "2026-05-17T00:00:00Z"
};

describe("team and project stores", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("loads teams and current-user invitations for /app", async () => {
    vi.mocked(listTeams).mockResolvedValue([team]);
    vi.mocked(listMyInvitations).mockResolvedValue([]);
    const store = useTeamStore();

    await store.loadAppData();

    expect(store.teams).toHaveLength(1);
    expect(store.selectedTeamId).toBe(1);
    expect(store.myInvitations).toEqual([]);
  });

  it("surfaces team creation failures", async () => {
    vi.mocked(createTeam).mockRejectedValue(new Error("duplicate"));
    const store = useTeamStore();

    await expect(store.createTeam({ name: "Demo Team" })).rejects.toThrow("创建团队失败");
    expect(store.error).toBe("创建团队失败。请检查团队名称后重试。");
  });

  it("creates projects and returns the board target id", async () => {
    vi.mocked(createProject).mockResolvedValue(project);
    const store = useProjectStore();

    const created = await store.createProject(1, { name: "Launch" });

    expect(created.id).toBe(10);
    expect(store.projects[0].id).toBe(10);
  });

  it("loads projects without persisting recent project routing", async () => {
    vi.mocked(listProjects).mockResolvedValue([project]);
    const store = useProjectStore();

    await store.loadProjects();

    expect(store.projects).toHaveLength(1);
    expect("recentProjectId" in store.$state).toBe(false);
  });
});

describe("team project UI components", () => {
  it("renders board empty column copy without fake task cards", () => {
    const wrapper = shallowMount(BoardColumn, {
      props: {
        column: { id: 1, project_id: 10, name: "待办", status: "TODO", position: 1 }
      }
    });

    expect(wrapper.text()).toContain("暂无待办任务");
    expect(wrapper.text()).toContain("任务功能将在后续阶段接入。当前看板列已准备就绪。");
    expect(wrapper.text()).not.toContain("创建任务");
  });

  it("shows project manager guard and permission copy in member drawer", () => {
    const wrapper = shallowMount(ProjectMemberDrawer, {
      props: {
        open: true,
        currentUserId: 2,
        teamMembers: [],
        members: [{ id: 1, project_id: 10, user, role: "PROJECT_MANAGER", created_at: "2026-05-17T00:00:00Z" }]
      },
      global: {
        stubs: {
          "a-drawer": { template: "<div><slot /></div>" },
          "a-alert": { template: "<div><slot name='message' /></div>" },
          "a-select": { template: "<div><slot /></div>" },
          "a-select-option": { template: "<div><slot /></div>" },
          "a-button": { template: "<button><slot /></button>" },
          "a-popconfirm": { template: "<div><slot /></div>" }
        }
      }
    });

    expect(wrapper.text()).toContain("只有项目经理可以管理项目成员。");
    expect(wrapper.text()).toContain("项目至少需要保留 1 名项目经理。");
    expect(wrapper.text()).toContain("添加项目成员");
  });

  it("does not duplicate accepted invitations in team member table", () => {
    const wrapper = shallowMount(TeamMemberTable, {
      props: {
        isAdmin: true,
        members: [
          {
            id: 1,
            team_id: 1,
            user: { ...user, email: "456@example.com", display_name: "测试成员1" },
            role: "TEAM_MEMBER",
            created_at: "2026-05-18T02:49:00Z"
          }
        ],
        invitations: [
          {
            id: 1,
            team_id: 1,
            email: "456@example.com",
            role: "TEAM_MEMBER",
            status: "ACCEPTED",
            invited_by_id: 1,
            accepted_by_id: 2,
            expires_at: "2026-05-25T00:00:00Z",
            accepted_at: "2026-05-18T02:49:00Z",
            cancelled_at: null,
            created_at: "2026-05-18T02:48:00Z"
          },
          {
            id: 2,
            team_id: 1,
            email: "pending@example.com",
            role: "TEAM_MEMBER",
            status: "PENDING",
            invited_by_id: 1,
            accepted_by_id: null,
            expires_at: "2026-05-25T00:00:00Z",
            accepted_at: null,
            cancelled_at: null,
            created_at: "2026-05-18T02:48:00Z"
          }
        ]
      },
      global: {
        stubs: {
          "a-select": { template: "<div><slot /></div>" },
          "a-select-option": { template: "<div><slot /></div>" },
          "a-tag": { template: "<span><slot /></span>" },
          "a-button": { template: "<button><slot /></button>" },
          "a-popconfirm": { template: "<div><slot /></div>" }
        }
      }
    });

    expect(wrapper.text()).toContain("456@example.com");
    expect(wrapper.text()).toContain("pending@example.com");
    expect(wrapper.text()).toContain("待接受邀请");
    expect(wrapper.text()).not.toContain("已接受");
  });
});
