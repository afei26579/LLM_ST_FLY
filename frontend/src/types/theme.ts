/**
 * 主题系统类型定义
 */

export type ThemeType = 'light' | 'dark' | 'future'

export interface ThemeColors {
  primary: string
  secondary: string
  background: string
  surface: string
  text: string
  textSecondary: string
  border: string
  accent: string
  success: string
  warning: string
  error: string
  info: string
}

export interface ThemeSidebar {
  background: string
  text: string
  activeBackground: string
  activeText: string
  hoverBackground: string
  border: string
}

export interface ThemeHeader {
  background: string
  text: string
  border: string
}

export interface ThemeCard {
  background: string
  border: string
  shadow: string
}

export interface ThemeButton {
  primary: string
  primaryHover: string
  secondary: string
  secondaryHover: string
}

export interface ThemeConfig {
  name: string
  label: string
  colors: ThemeColors
  sidebar: ThemeSidebar
  header: ThemeHeader
  card: ThemeCard
  button: ThemeButton
}

export interface ThemeStore {
  currentTheme: ThemeType
  theme: ThemeConfig
  themeList: ThemeConfig[]
  setTheme: (theme: ThemeType) => void
  loadTheme: () => void
}

/**
 * 主题事件类型
 */
export interface ThemeChangeEvent {
  oldTheme: ThemeType
  newTheme: ThemeType
  timestamp: number
}

/**
 * 主题设置选项
 */
export interface ThemeSettings {
  autoSwitchTime?: {
    lightThemeStart: string // 如 "06:00"
    darkThemeStart: string  // 如 "18:00"
  }
  followSystem?: boolean // 是否跟随系统主题
  animations?: boolean   // 是否启用主题切换动画
}

/**
 * CSS变量映射
 */
export type CSSVariableMap = {
  [K in keyof ThemeColors as `--color-${K}`]: string
} & {
  [K in keyof ThemeSidebar as `--sidebar-${K}`]: string
} & {
  [K in keyof ThemeHeader as `--header-${K}`]: string
} & {
  [K in keyof ThemeCard as `--card-${K}`]: string
} & {
  [K in keyof ThemeButton as `--button-${K}`]: string
}