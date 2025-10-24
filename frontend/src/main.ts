import './assets/main.css'
import './assets/styles/theme.css'
import './styles/themes.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// 导入主题 store
import { useThemeStore } from './stores/theme'

// 导入 Toast 通知组件
import Toast, { useToast } from 'vue-toastification'
import "vue-toastification/dist/index.css"

// Toast 配置选项
const toastOptions = {
  position: "top-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true
}

const app = createApp(App)

app.use(createPinia())

// 初始化主题（必须在 Pinia 安装之后）
const themeStore = useThemeStore()
themeStore.loadTheme()

app.use(router)
app.use(Toast, toastOptions)

app.mount('#app')

// 挂载后，将 toast 实例暴露到全局（供 API 拦截器使用）
;(window as any).__toast = useToast()
