import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    // 系统管理 - 角色管理
    {
      path: '/roles',
      name: 'roles',
      component: () => import('../views/system/RolesView.vue'),
      meta: { requiresAuth: true, requiredRole: 'admin' }
    },
    // 系统管理 - 权限管理
    {
      path: '/permissions',
      name: 'permissions',
      component: () => import('../views/system/PermissionsView.vue'),
      meta: { requiresAuth: true, requiredRole: 'admin' }
    },
    // 将其他未匹配路由重定向到首页
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 判断路由是否需要登录权限
  if (to.meta.requiresAuth) {
    // 从localStorage获取token判断用户是否登录
    const token = localStorage.getItem('token')
    
    if (token) {
      // 检查是否需要特定角色
      if (to.meta.requiredRole) {
        const userData = JSON.parse(localStorage.getItem('user') || '{}')
        if (userData?.role === to.meta.requiredRole || userData?.role === 'admin') {
          next() // 有权限，放行
        } else {
          next('/') // 权限不足，转到首页
        }
      } else {
        next() // 已登录，允许访问
      }
    } else {
      // 未登录，重定向到登录页
      next({ 
        name: 'login',
        query: { redirect: to.fullPath } // 保存原本要访问的路径
      })
    }
  } else {
    // 不需要登录权限的页面直接放行
    next()
  }
})

export default router
