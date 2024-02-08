import { createRouter, createWebHistory } from 'vue-router'

const protectedRoutes = [
  { path: '', component: () => import('./views/home/index.vue') },
]

const routes = [
  { path: '/', component: () => import('./components/ProtectedLayout.vue'), children: protectedRoutes },
  { path: '/login', component: () => import('./views/login/index.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
