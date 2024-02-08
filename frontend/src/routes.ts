import { createRouter, createWebHistory } from 'vue-router'
import { useSnackbar } from 'vue3-snackbar'
import { fetchCurrentUser } from './api/user'
import { useCurrentUser } from './lib/states'

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

const unprotectedRoutes = ['/login']

router.beforeEach(async (to) => {
  const { setCurrentUser } = useCurrentUser()
  const snackbar = useSnackbar()

  try {
    const currentUser = await fetchCurrentUser()
    setCurrentUser(currentUser.data)
    if (to.path === '/login')
      return { path: to.query.next as string || '/' }
  }
  catch (error) {
    setCurrentUser(undefined)
    if (!unprotectedRoutes.includes(to.path) && error.response.status === 401) {
      snackbar.add({
        type: 'error',
        text: 'You need to login to access this page',
      })
      return { path: '/login', query: { next: to.path } }
    }
  }
})

export default router
