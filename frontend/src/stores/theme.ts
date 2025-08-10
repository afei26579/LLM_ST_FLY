import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ThemeType, ThemeConfig } from '../types/theme'

const themes: Record<ThemeType, ThemeConfig> = {
  light: {
    name: 'light',
    label: '浅色主题',
    colors: {
      primary: '#3b82f6',
      secondary: '#6b7280',
      background: '#ffffff',
      surface: '#f8fafc',
      text: '#1f2937',
      textSecondary: '#6b7280',
      border: '#e5e7eb',
      accent: '#8b5cf6',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#06b6d4'
    },
    sidebar: {
      background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
      text: '#374151',
      activeBackground: 'rgba(59, 130, 246, 0.1)',
      activeText: '#3b82f6',
      hoverBackground: 'rgba(0, 0, 0, 0.05)',
      border: '#e5e7eb'
    },
    header: {
      background: '#ffffff',
      text: '#1f2937',
      border: '#e5e7eb'
    },
    card: {
      background: '#ffffff',
      border: '#e5e7eb',
      shadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
    },
    button: {
      primary: '#3b82f6',
      primaryHover: '#2563eb',
      secondary: '#6b7280',
      secondaryHover: '#4b5563'
    }
  },
  dark: {
    name: 'dark',
    label: '深色主题',
    colors: {
      primary: '#5e9bff',
      secondary: '#9ca3af',
      background: '#0f172a',
      surface: '#1e293b',
      text: '#e1e6f5',
      textSecondary: '#94a3b8',
      border: '#334155',
      accent: '#a569ff',
      success: '#22c55e',
      warning: '#fbbf24',
      error: '#f87171',
      info: '#38bdf8'
    },
    sidebar: {
      background: 'linear-gradient(180deg, #1a2233 0%, #0c1425 100%)',
      text: '#e1e6f5',
      activeBackground: 'rgba(94, 155, 255, 0.15)',
      activeText: '#5e9bff',
      hoverBackground: 'rgba(255, 255, 255, 0.08)',
      border: 'rgba(255, 255, 255, 0.1)'
    },
    header: {
      background: '#1e293b',
      text: '#e1e6f5',
      border: '#334155'
    },
    card: {
      background: '#1e293b',
      border: '#334155',
      shadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)'
    },
    button: {
      primary: '#5e9bff',
      primaryHover: '#4f8aff',
      secondary: '#64748b',
      secondaryHover: '#475569'
    }
  },
  future: {
    name: 'future',
    label: '未来科技',
    colors: {
      primary: '#00d4ff',
      secondary: '#7c3aed',
      background: '#0a0a0f',
      surface: '#1a1a2e',
      text: '#e0e7ff',
      textSecondary: '#a5b4fc',
      border: '#3730a3',
      accent: '#ff006e',
      success: '#00ff88',
      warning: '#ffaa00',
      error: '#ff0055',
      info: '#00aaff'
    },
    sidebar: {
      background: 'linear-gradient(180deg, #16213e 0%, #0f172a 50%, #1a1a2e 100%)',
      text: '#e0e7ff',
      activeBackground: 'linear-gradient(90deg, rgba(0, 212, 255, 0.2) 0%, rgba(255, 0, 110, 0.1) 100%)',
      activeText: '#00d4ff',
      hoverBackground: 'rgba(0, 212, 255, 0.1)',
      border: 'linear-gradient(90deg, #3730a3 0%, #7c3aed 100%)'
    },
    header: {
      background: 'linear-gradient(90deg, #1a1a2e 0%, #16213e 100%)',
      text: '#e0e7ff',
      border: '#3730a3'
    },
    card: {
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      border: '#3730a3',
      shadow: '0 0 20px rgba(0, 212, 255, 0.1), 0 0 40px rgba(255, 0, 110, 0.05)'
    },
    button: {
      primary: 'linear-gradient(90deg, #00d4ff 0%, #7c3aed 100%)',
      primaryHover: 'linear-gradient(90deg, #00b8e6 0%, #6d28d9 100%)',
      secondary: '#7c3aed',
      secondaryHover: '#6d28d9'
    }
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<ThemeType>('dark')
  
  // 从localStorage加载主题
  const loadTheme = () => {
    const savedTheme = localStorage.getItem('app-theme') as ThemeType
    if (savedTheme && themes[savedTheme]) {
      currentTheme.value = savedTheme
    }
    applyTheme()
  }
  
  // 设置主题
  const setTheme = (theme: ThemeType) => {
    currentTheme.value = theme
    localStorage.setItem('app-theme', theme)
    applyTheme()
  }
  
  // 应用主题到CSS变量
  const applyTheme = () => {
    const theme = themes[currentTheme.value]
    const root = document.documentElement
    
    // 设置CSS变量
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })
    
    Object.entries(theme.sidebar).forEach(([key, value]) => {
      root.style.setProperty(`--sidebar-${key}`, value)
    })
    
    Object.entries(theme.header).forEach(([key, value]) => {
      root.style.setProperty(`--header-${key}`, value)
    })
    
    Object.entries(theme.card).forEach(([key, value]) => {
      root.style.setProperty(`--card-${key}`, value)
    })
    
    Object.entries(theme.button).forEach(([key, value]) => {
      root.style.setProperty(`--button-${key}`, value)
    })
    
    // 设置body类名
    document.body.className = `theme-${theme.name}`
  }
  
  // 计算属性
  const theme = computed(() => themes[currentTheme.value])
  const themeList = computed(() => Object.values(themes))
  
  return {
    currentTheme,
    theme,
    themeList,
    setTheme,
    loadTheme
  }
})