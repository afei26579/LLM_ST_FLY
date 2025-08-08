import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import VerifyEmailView from '../views/VerifyEmailView.vue'

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
    // 邮箱验证路由
    {
      path: '/verify-email',
      name: 'verify-email',
      component: VerifyEmailView,
      meta: { requiresAuth: false }
    },
    // 系统管理 - 用户管理
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/system/UsersView.vue'),
      meta: { requiresAuth: true }
    },
    // 系统管理 - 角色管理
    {
      path: '/roles',
      name: 'roles',
      component: () => import('../views/system/RolesView.vue'),
      meta: { requiresAuth: true }
    },
    // 系统管理 - 权限管理
    {
      path: '/permissions',
      name: 'permissions',
      component: () => import('../views/system/PermissionsView.vue'),
      meta: { requiresAuth: true }
    },
    // 系统管理 - 日志管理
    {
      path: '/logs',
      name: 'logs',
      component: () => import('../views/system/LogsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/logs/system',
      name: 'system-logs',
      component: () => import('../views/system/SystemLogsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/logs/user',
      name: 'user-logs',
      component: () => import('../views/system/UserLogsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/logs/api',
      name: 'api-logs',
      component: () => import('../views/system/ApiLogsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/logs/error',
      name: 'error-logs',
      component: () => import('../views/system/ErrorLogsView.vue'),
      meta: { requiresAuth: true }
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
  console.log('路由跳转:', { from: from.path, to: to.path, meta: to.meta })
  
  // 判断路由是否需要登录权限
  if (to.meta.requiresAuth) {
    // 从localStorage获取token判断用户是否登录
    const token = localStorage.getItem('token')
    console.log('当前token状态:', !!token)
    
    if (token) {
      // 检查是否需要特定角色
      if (to.meta.requiredRole) {
        const userData = JSON.parse(localStorage.getItem('userInfo') || '{}')
        console.log('用户角色检查:', { 
          requiredRole: to.meta.requiredRole, 
          userRole: userData?.role 
        })
        
        if (userData?.role === to.meta.requiredRole || userData?.role === 'admin') {
          console.log('权限检查通过')
          next() // 有权限，放行
        } else {
          console.log('权限不足，重定向到首页')
          next('/') // 权限不足，转到首页
        }
      } else {
        console.log('无需角色权限，允许访问')
        next() // 已登录，允许访问
      }
    } else {
      // 未登录，重定向到登录页
      console.log('未登录，重定向到登录页')
      next({ 
        name: 'login',
        query: { redirect: to.fullPath } // 保存原本要访问的路径
      })
    }
  } else {
    // 不需要登录权限的页面直接放行
    console.log('无需登录权限，直接放行')
    next()
  }
})

export default router
