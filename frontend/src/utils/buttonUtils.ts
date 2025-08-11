/**
 * 按钮工具类
 * 提供按钮样式相关的工具函数和常量
 */

export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'ghost' | 'outline'
export type ButtonSize = 'small' | 'medium' | 'large'

/**
 * 按钮变体配置
 */
export const BUTTON_VARIANTS = {
  primary: {
    label: '主要按钮',
    description: '用于主要操作，如提交、保存等',
    cssClass: 'btn-primary'
  },
  secondary: {
    label: '次要按钮',
    description: '用于次要操作，如取消、返回等',
    cssClass: 'btn-secondary'
  },
  success: {
    label: '成功按钮',
    description: '用于成功操作，如确认、完成等',
    cssClass: 'btn-success'
  },
  warning: {
    label: '警告按钮',
    description: '用于警告操作，如注意、提醒等',
    cssClass: 'btn-warning'
  },
  error: {
    label: '错误按钮',
    description: '用于危险操作，如删除、拒绝等',
    cssClass: 'btn-error'
  },
  info: {
    label: '信息按钮',
    description: '用于信息操作，如查看、详情等',
    cssClass: 'btn-info'
  },
  ghost: {
    label: '幽灵按钮',
    description: '透明背景按钮，用于次要操作',
    cssClass: 'btn-ghost'
  },
  outline: {
    label: '轮廓按钮',
    description: '边框按钮，用于强调但不突出的操作',
    cssClass: 'btn-outline'
  }
} as const

/**
 * 按钮尺寸配置
 */
export const BUTTON_SIZES = {
  small: {
    label: '小号',
    description: '适用于紧凑布局',
    cssClass: 'btn-small'
  },
  medium: {
    label: '中号',
    description: '默认尺寸，适用于大多数场景',
    cssClass: 'btn-medium'
  },
  large: {
    label: '大号',
    description: '适用于重要操作或大屏幕',
    cssClass: 'btn-large'
  }
} as const

/**
 * 按钮状态配置
 */
export const BUTTON_STATES = {
  normal: {
    label: '正常',
    description: '默认状态',
    cssClass: ''
  },
  disabled: {
    label: '禁用',
    description: '不可点击状态',
    cssClass: 'btn-disabled'
  },
  loading: {
    label: '加载中',
    description: '处理中状态',
    cssClass: 'btn-loading'
  }
} as const

/**
 * 生成按钮CSS类名
 */
export function generateButtonClasses(
  variant: ButtonVariant = 'primary',
  size: ButtonSize = 'medium',
  options: {
    disabled?: boolean
    loading?: boolean
    block?: boolean
    rounded?: boolean
  } = {}
): string[] {
  const classes = [
    'btn',
    BUTTON_VARIANTS[variant].cssClass,
    BUTTON_SIZES[size].cssClass
  ]

  if (options.disabled) {
    classes.push(BUTTON_STATES.disabled.cssClass)
  }

  if (options.loading) {
    classes.push(BUTTON_STATES.loading.cssClass)
  }

  if (options.block) {
    classes.push('btn-block')
  }

  if (options.rounded) {
    classes.push('btn-rounded')
  }

  return classes.filter(Boolean)
}

/**
 * 获取按钮变体的CSS变量名
 */
export function getButtonVariantCSSVars(variant: ButtonVariant) {
  return {
    background: `--button-${variant}`,
    backgroundHover: `--button-${variant}Hover`,
    backgroundActive: `--button-${variant}Active`,
    backgroundDisabled: `--button-${variant}Disabled`,
    text: `--button-${variant}Text`,
    border: variant === 'ghost' ? `--button-${variant}Border` : `--button-${variant}`
  }
}

/**
 * 按钮使用场景配置
 */
export const BUTTON_SCENARIOS = {
  form: {
    label: '表单操作',
    buttons: [
      { variant: 'primary' as ButtonVariant, text: '保存', description: '提交表单数据' },
      { variant: 'ghost' as ButtonVariant, text: '取消', description: '取消操作' },
      { variant: 'outline' as ButtonVariant, text: '重置', description: '重置表单' }
    ]
  },
  data: {
    label: '数据操作',
    buttons: [
      { variant: 'success' as ButtonVariant, text: '新增', description: '添加新数据' },
      { variant: 'info' as ButtonVariant, text: '编辑', description: '修改数据' },
      { variant: 'warning' as ButtonVariant, text: '禁用', description: '禁用数据' },
      { variant: 'error' as ButtonVariant, text: '删除', description: '删除数据' }
    ]
  },
  dialog: {
    label: '对话框',
    buttons: [
      { variant: 'error' as ButtonVariant, text: '确认删除', description: '确认危险操作' },
      { variant: 'ghost' as ButtonVariant, text: '取消', description: '取消操作' }
    ]
  },
  navigation: {
    label: '导航操作',
    buttons: [
      { variant: 'outline' as ButtonVariant, text: '上一步', description: '返回上一步' },
      { variant: 'primary' as ButtonVariant, text: '下一步', description: '进入下一步' },
      { variant: 'success' as ButtonVariant, text: '完成', description: '完成流程' }
    ]
  }
} as const

/**
 * 验证按钮变体
 */
export function isValidButtonVariant(variant: string): variant is ButtonVariant {
  return variant in BUTTON_VARIANTS
}

/**
 * 验证按钮尺寸
 */
export function isValidButtonSize(size: string): size is ButtonSize {
  return size in BUTTON_SIZES
}

/**
 * 获取按钮的可访问性属性
 */
export function getButtonA11yProps(
  variant: ButtonVariant,
  disabled: boolean = false,
  loading: boolean = false
) {
  const props: Record<string, any> = {
    role: 'button',
    tabindex: disabled ? -1 : 0
  }

  if (disabled) {
    props['aria-disabled'] = 'true'
  }

  if (loading) {
    props['aria-busy'] = 'true'
  }

  // 根据变体设置语义化标签
  switch (variant) {
    case 'error':
      props['aria-label'] = '危险操作按钮'
      break
    case 'success':
      props['aria-label'] = '确认操作按钮'
      break
    case 'warning':
      props['aria-label'] = '警告操作按钮'
      break
    case 'info':
      props['aria-label'] = '信息操作按钮'
      break
  }

  return props
}

/**
 * 按钮主题适配工具
 */
export class ButtonThemeAdapter {
  /**
   * 根据当前主题获取按钮样式
   */
  static getThemeStyles(theme: 'light' | 'dark' | 'future', variant: ButtonVariant) {
    const baseStyles = {
      transition: 'all 0.2s ease-in-out',
      cursor: 'pointer',
      userSelect: 'none' as const,
      outline: 'none'
    }

    // 未来科技主题特殊处理
    if (theme === 'future') {
      return {
        ...baseStyles,
        boxShadow: '0 0 10px rgba(0, 212, 255, 0.1)',
        '&:hover': {
          boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)',
          transform: 'translateY(-1px)'
        }
      }
    }

    return baseStyles
  }

  /**
   * 获取主题特定的按钮动画
   */
  static getThemeAnimations(theme: 'light' | 'dark' | 'future') {
    switch (theme) {
      case 'future':
        return {
          hover: {
            transform: 'translateY(-1px) scale(1.02)',
            boxShadow: '0 0 25px rgba(0, 212, 255, 0.4)'
          },
          active: {
            transform: 'translateY(0) scale(0.98)'
          }
        }
      case 'dark':
        return {
          hover: {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
          },
          active: {
            transform: 'translateY(0)'
          }
        }
      case 'light':
      default:
        return {
          hover: {
            transform: 'translateY(-1px)',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          },
          active: {
            transform: 'translateY(0)'
          }
        }
    }
  }
}

/**
 * 按钮组合工具
 */
export class ButtonGroupUtils {
  /**
   * 生成按钮组的布局类名
   */
  static getGroupClasses(
    direction: 'horizontal' | 'vertical' = 'horizontal',
    spacing: 'tight' | 'normal' | 'loose' = 'normal',
    alignment: 'start' | 'center' | 'end' | 'stretch' = 'start'
  ) {
    const classes = ['btn-group']

    classes.push(`btn-group-${direction}`)
    classes.push(`btn-group-spacing-${spacing}`)
    classes.push(`btn-group-align-${alignment}`)

    return classes
  }

  /**
   * 验证按钮组合的合理性
   */
  static validateButtonCombination(buttons: { variant: ButtonVariant; text: string }[]) {
    const warnings: string[] = []

    // 检查是否有多个主要按钮
    const primaryCount = buttons.filter(btn => btn.variant === 'primary').length
    if (primaryCount > 1) {
      warnings.push('建议一个按钮组中只有一个主要按钮')
    }

    // 检查危险操作按钮的位置
    const errorButtons = buttons.filter(btn => btn.variant === 'error')
    if (errorButtons.length > 0) {
      warnings.push('危险操作按钮建议放在右侧或单独确认')
    }

    return {
      isValid: warnings.length === 0,
      warnings
    }
  }
}