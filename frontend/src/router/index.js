import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login',
      component: () => import('@/views/LoginPage.vue'),
      meta: { title: '用户登录与注册', requiresAuth: false }
    },
    {
      path: '/',
      redirect: '/index',
    },
    {
      path: '/index',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: '首页', requiresAuth: false }
    },
    {
      path: '/items/:id',
    },
    {
      path: '/items/create',
      component: () => import('@/views/CreateItemView.vue'),
      meta: { title: '发布物品', requiresAuth: true }
    },
    {
      path: '/my-items',
      component: () => import('@/views/MyItemsView.vue'),
      meta: { title: '我的物品', requiresAuth: true }
    }
  ],
})

// 路由守卫 - 验证登录状态
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  document.title = to.meta.title || '校园闲置共享平台'

  console.log(`是否有效登录:${userStore.isLogin()}`)

  if (to.meta.requiresAuth && !userStore.isLogin()) {
    next('/login')
  } else {
    next()
  }
})

export default router
