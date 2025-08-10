/**
 * 主题工具类
 * 提供主题相关的实用功能
 */

import type { ThemeType, ThemeConfig } from '../types/theme'

/**
 * 检测系统主题偏好
 */
export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/**
 * 监听系统主题变化
 */
export function watchSystemTheme(callback: (theme: 'light' | 'dark') => void) {
  if (typeof window === 'undefined') return () => {}
  
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  
  const handler = (e: MediaQueryListEvent) => {
    callback(e.matches ? 'dark' : 'light')
  }
  
  mediaQuery.addEventListener('change', handler)
  
  // 返回清理函数
  return () => {
    mediaQuery.removeEventListener('change', handler)
  }
}

/**
 * 获取当前时间对应的推荐主题
 */
export function getTimeBasedTheme(): 'light' | 'dark' {
  const hour = new Date().getHours()
  
  // 6:00-18:00 使用浅色主题，其他时间使用深色主题
  return hour >= 6 && hour < 18 ? 'light' : 'dark'
}

/**
 * 颜色工具函数
 */
export class ColorUtils {
  /**
   * 将十六进制颜色转换为RGB
   */
  static hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  /**
   * 将RGB转换为十六进制颜色
   */
  static rgbToHex(r: number, g: number, b: number): string {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
  }

  /**
   * 调整颜色亮度
   */
  static adjustBrightness(hex: string, percent: number): string {
    const rgb = this.hexToRgb(hex)
    if (!rgb) return hex

    const adjust = (color: number) => {
      const adjusted = Math.round(color * (1 + percent / 100))
      return Math.max(0, Math.min(255, adjusted))
    }

    return this.rgbToHex(
      adjust(rgb.r),
      adjust(rgb.g),
      adjust(rgb.b)
    )
  }

  /**
   * 获取颜色的对比色
   */
  static getContrastColor(hex: string): string {
    const rgb = this.hexToRgb(hex)
    if (!rgb) return '#000000'

    // 计算亮度
    const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000
    
    // 根据亮度返回黑色或白色
    return brightness > 128 ? '#000000' : '#ffffff'
  }

  /**
   * 混合两个颜色
   */
  static mixColors(color1: string, color2: string, ratio: number = 0.5): string {
    const rgb1 = this.hexToRgb(color1)
    const rgb2 = this.hexToRgb(color2)
    
    if (!rgb1 || !rgb2) return color1

    const mix = (c1: number, c2: number) => Math.round(c1 * (1 - ratio) + c2 * ratio)

    return this.rgbToHex(
      mix(rgb1.r, rgb2.r),
      mix(rgb1.g, rgb2.g),
      mix(rgb1.b, rgb2.b)
    )
  }
}

/**
 * 主题验证工具
 */
export class ThemeValidator {
  /**
   * 验证主题配置是否完整
   */
  static validateThemeConfig(config: Partial<ThemeConfig>): string[] {
    const errors: string[] = []
    
    if (!config.name) errors.push('主题名称不能为空')
    if (!config.label) errors.push('主题标签不能为空')
    
    // 验证必需的颜色
    const requiredColors = [
      'primary', 'secondary', 'background', 'surface', 
      'text', 'textSecondary', 'border', 'accent',
      'success', 'warning', 'error', 'info'
    ]
    
    requiredColors.forEach(color => {
      if (!config.colors?.[color as keyof typeof config.colors]) {
        errors.push(`缺少颜色配置: ${color}`)
      }
    })
    
    return errors
  }

  /**
   * 验证颜色对比度
   */
  static validateContrast(backgroundColor: string, textColor: string): boolean {
    const bgRgb = ColorUtils.hexToRgb(backgroundColor)
    const textRgb = ColorUtils.hexToRgb(textColor)
    
    if (!bgRgb || !textRgb) return false
    
    // 计算相对亮度
    const getLuminance = (rgb: { r: number; g: number; b: number }) => {
      const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(c => {
        c = c / 255
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
      })
      return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }
    
    const bgLuminance = getLuminance(bgRgb)
    const textLuminance = getLuminance(textRgb)
    
    const contrast = (Math.max(bgLuminance, textLuminance) + 0.05) / 
                    (Math.min(bgLuminance, textLuminance) + 0.05)
    
    // WCAG AA 标准要求对比度至少为 4.5:1
    return contrast >= 4.5
  }
}

/**
 * 主题动画工具
 */
export class ThemeAnimations {
  /**
   * 创建主题切换动画
   */
  static createTransition(duration: number = 300): void {
    const style = document.createElement('style')
    style.textContent = `
      * {
        transition: 
          background-color ${duration}ms ease,
          color ${duration}ms ease,
          border-color ${duration}ms ease,
          box-shadow ${duration}ms ease !important;
      }
    `
    
    document.head.appendChild(style)
    
    // 动画结束后移除样式
    setTimeout(() => {
      document.head.removeChild(style)
    }, duration)
  }

  /**
   * 创建主题切换的淡入淡出效果
   */
  static fadeTransition(callback: () => void, duration: number = 200): void {
    const body = document.body
    
    // 淡出
    body.style.transition = `opacity ${duration}ms ease`
    body.style.opacity = '0.7'
    
    setTimeout(() => {
      // 执行主题切换
      callback()
      
      // 淡入
      setTimeout(() => {
        body.style.opacity = '1'
        
        // 清理样式
        setTimeout(() => {
          body.style.transition = ''
          body.style.opacity = ''
        }, duration)
      }, 50)
    }, duration)
  }
}

/**
 * 主题存储工具
 */
export class ThemeStorage {
  private static readonly THEME_KEY = 'app-theme'
  private static readonly SETTINGS_KEY = 'theme-settings'

  /**
   * 保存主题
   */
  static saveTheme(theme: ThemeType): void {
    try {
      localStorage.setItem(this.THEME_KEY, theme)
    } catch (error) {
      console.warn('无法保存主题设置:', error)
    }
  }

  /**
   * 加载主题
   */
  static loadTheme(): ThemeType | null {
    try {
      const theme = localStorage.getItem(this.THEME_KEY) as ThemeType
      return theme && ['light', 'dark', 'future'].includes(theme) ? theme : null
    } catch (error) {
      console.warn('无法加载主题设置:', error)
      return null
    }
  }

  /**
   * 保存主题设置
   */
  static saveSettings(settings: Record<string, any>): void {
    try {
      localStorage.setItem(this.SETTINGS_KEY, JSON.stringify(settings))
    } catch (error) {
      console.warn('无法保存主题设置:', error)
    }
  }

  /**
   * 加载主题设置
   */
  static loadSettings(): Record<string, any> {
    try {
      const settings = localStorage.getItem(this.SETTINGS_KEY)
      return settings ? JSON.parse(settings) : {}
    } catch (error) {
      console.warn('无法加载主题设置:', error)
      return {}
    }
  }

  /**
   * 清除所有主题数据
   */
  static clear(): void {
    try {
      localStorage.removeItem(this.THEME_KEY)
      localStorage.removeItem(this.SETTINGS_KEY)
    } catch (error) {
      console.warn('无法清除主题数据:', error)
    }
  }
}