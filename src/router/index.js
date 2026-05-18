import { createRouter, createWebHistory } from 'vue-router';

import SafePathLoginView from '../../src/view/SafePathLoginView.vue';
import SafePathRegisterView from '../../src/view/SafePathRegisterView.vue';
import SafePathHomeView from '../../src/view/SafePathHomeView.vue';

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
    component: SafePathHomeView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;