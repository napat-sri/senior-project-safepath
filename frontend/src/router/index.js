import { createRouter, createWebHistory } from 'vue-router';

import SafePathLoginView from '../view/SafePathLoginView.vue';
import SafePathRegisterView from '../view/SafePathRegisterView.vue';
import SafePathHomeView from '../view/SafePathHomeView.vue';
import SafePathRouteDetailsView from '../view/SafePathRouteDetailsView.vue';

const routes = [
  {
    path: '/',
    redirect: '/login'
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
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;