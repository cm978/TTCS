import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

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
