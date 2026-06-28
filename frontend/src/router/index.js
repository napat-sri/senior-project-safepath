import { createRouter, createWebHistory } from 'vue-router';

import SafePathAdminDashboardOverview from '../view/SafePathAdminDashboardOverview.vue';
import SafePathHomeView from '../view/SafePathHomeView.vue';
import SafePathIncidentView from '../view/SafePathIncidentView.vue';
import SafePathLoginView from '../view/SafePathLoginView.vue';
import SafePathProfileView from '../view/SafePathProfileView.vue';
import SafePathRegisterView from '../view/SafePathRegisterView.vue';
import SafePathRouteDetailsView from '../view/SafePathRouteDetailsView.vue';

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
    path: '/register',
    component: SafePathRegisterView
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

  },
  {
    path: '/incident',
    name: 'incident',
    component: SafePathIncidentView,
  },
  {
    path: '/profile',
    name: 'profile',
    component: SafePathProfileView,
  },
  {
    path: '/overview',
    name: 'overview',
    component: SafePathAdminDashboardOverview,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;

