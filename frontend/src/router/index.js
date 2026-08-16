import { createRouter, createWebHistory } from 'vue-router';

import SafePathAdminDashboard from '../view/admin/SafePathAdminDashboard.vue';
import SafePathHomeView from '../view/SafePathHomeView.vue';
import SafePathIncidentView from '../view/SafePathIncidentView.vue';
import SafePathLoginView from '../view/SafePathLoginView.vue';
import SafePathProfileView from '../view/SafePathProfileView.vue';
import SafePathRouteDetailsView from '../view/SafePathRouteDetailsView.vue';

// keycloak
import keycloak from '../services/keycloak';

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    component: SafePathLoginView
  },
  {
    path: '/home',
    name: 'home',
    component: SafePathHomeView
  },
  {
    path: '/route-details/:routeId',
    name: 'route-details',
    component: SafePathRouteDetailsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/incident',
    name: 'incident',
    component: SafePathIncidentView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: SafePathProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/overview',
    name: 'overview',
    component: SafePathAdminDashboard,
    meta: {
      requiresAuth: true,
      requiredRole: 'Admin'
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0, left: 0 };
  }
});

// keycloak
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !keycloak.authenticated) {
    keycloak.login({ redirectUri: window.location.origin + to.fullPath });
    return false;
  }
  if (to.meta.requiredRole && !keycloak.hasRealmRole(to.meta.requiredRole)) {
    return { path: '/home' };
  }          // logged in but not an admin → send home
  return true;
});

export default router;