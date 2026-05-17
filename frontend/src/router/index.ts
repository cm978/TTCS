import { createRouter, createWebHistory } from "vue-router";

import { authTokenKey } from "../api/client";
import { useAuthStore } from "../stores/auth";
import LoginView from "../views/LoginView.vue";
import ProjectBoardView from "../views/ProjectBoardView.vue";
import RegisterView from "../views/RegisterView.vue";
import TeamProjectStartView from "../views/TeamProjectStartView.vue";
import TeamMembersView from "../views/TeamMembersView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/app" },
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/register", name: "register", component: RegisterView, meta: { public: true } },
    { path: "/app", name: "team-project-start", component: TeamProjectStartView, meta: { requiresAuth: true } },
    { path: "/teams/:teamId/members", name: "team-members", component: TeamMembersView, meta: { requiresAuth: true } },
    { path: "/projects/:projectId/board", name: "project-board", component: ProjectBoardView, meta: { requiresAuth: true } },
    { path: "/:pathMatch(.*)*", redirect: "/app" }
  ]
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  auth.bindUnauthorizedHandler();
  const hasStoredToken = Boolean(window.localStorage.getItem(authTokenKey));
  if (!auth.hydrated || (!auth.isAuthenticated && hasStoredToken)) {
    await auth.loadCurrentUser();
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.public && auth.isAuthenticated) {
    return { name: "team-project-start" };
  }
  return true;
});

export default router;
