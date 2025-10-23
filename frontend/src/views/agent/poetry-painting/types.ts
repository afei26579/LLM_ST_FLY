/**
 * 诗词绘画智能体类型定义
 */

export interface Poetry {
  title: string
  content: string
  style: string
  format: string
  theme: string
  analysis?: PoetryAnalysis
}

export interface PoetryAnalysis {
  imagery: ImageryItem[]
  emotion: string
  rhetoric: string[]
  allusion: AllusionItem[]
  imagery_description: string
}

export interface ImageryItem {
  name: string
  meaning: string
}

export interface AllusionItem {
  reference: string
  meaning: string
}

export interface Painting {
  url: string
  local_path?: string
  prompt: string
  style: string
  description: string
}

export interface PoetryPaintingWork {
  id: number
  conversation: number
  poetry_theme: string
  poetry_format: string
  poetry_style: string
  poetry_content: string
  poetry_title: string
  poetry_analysis: PoetryAnalysis | null
  painting_prompt: string
  painting_style: string
  painting_url: string
  painting_url_full?: string
  painting_local_path: string
  iteration_count: number
  user_rating: number | null
  created_at: string
}

export interface PoetryPaintingMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  work?: number
  created_at: string
}

export interface PoetryPaintingConversation {
  id: number
  user: number
  title: string
  created_at: string
  updated_at: string
  messages?: PoetryPaintingMessage[]
  works?: PoetryPaintingWork[]
  works_count?: number
  latest_work?: PoetryPaintingWork
}

export interface CreateWorkRequest {
  input: string
  poetry_style?: string
  poetry_format?: string
  painting_style?: string
  image_size?: string
  conversation_id?: number
}

export interface CreateWorkResponse {
  work_id: number
  conversation_id: number
  work: PoetryPaintingWork
  result: {
    poetry: Poetry
    painting: Painting
    metadata: {
      iteration: number
      current_step: string
    }
  }
}

export interface IterateWorkRequest {
  feedback: string
  type?: 'poetry' | 'painting' | 'both'
}

export type PoetryStyleType = '豪放' | '婉约' | '田园' | '边塞' | '山水'
export type PoetryFormatType = 'five_jueju' | 'seven_jueju' | 'five_lvshi' | 'seven_lvshi' | 'ci'
export type PaintingStyleType = 'chinese_ink' | 'gongbi' | 'oil_painting' | 'watercolor' | 'modern'

export interface StyleOption {
  value: string
  label: string
  description: string
}

export const POETRY_STYLES: StyleOption[] = [
  { value: '', label: '智能选择', description: '由AI根据主题推荐' },
  { value: '豪放', label: '豪放', description: '气势磅礴，意境开阔' },
  { value: '婉约', label: '婉约', description: '细腻柔美，含蓄隽永' },
  { value: '田园', label: '田园', description: '清新自然，恬淡闲适' },
  { value: '边塞', label: '边塞', description: '雄浑壮阔，慷慨悲壮' },
  { value: '山水', label: '山水', description: '描绘自然，意境清幽' }
]

export const POETRY_FORMATS: StyleOption[] = [
  { value: '', label: '智能选择', description: '由AI根据主题推荐' },
  { value: 'five_jueju', label: '五言绝句', description: '四句，每句五字' },
  { value: 'seven_jueju', label: '七言绝句', description: '四句，每句七字' },
  { value: 'five_lvshi', label: '五言律诗', description: '八句，每句五字' },
  { value: 'seven_lvshi', label: '七言律诗', description: '八句，每句七字' },
  { value: 'ci', label: '词', description: '长短句，讲究韵律' }
]

export const PAINTING_STYLES: StyleOption[] = [
  { value: '', label: '智能选择', description: '由AI根据诗词推荐' },
  { value: 'chinese_ink', label: '水墨画', description: '淡雅飘逸，留白艺术' },
  { value: 'gongbi', label: '工笔画', description: '细腻精致，色彩典雅' },
  { value: 'oil_painting', label: '油画风格', description: '色彩浓郁，笔触明显' },
  { value: 'watercolor', label: '水彩风格', description: '清新淡雅，水色交融' },
  { value: 'modern', label: '现代艺术', description: '抽象表现，构图创新' }
]

export interface WorkStep {
  key: string
  label: string
  done: boolean
}

export interface ImageSizeOption {
  value: string
  label: string
  aspect_ratio: string
}

export const IMAGE_SIZES: ImageSizeOption[] = [
  { value: '1328*1328', label: '1:1 (1328x1328)', aspect_ratio: '1:1' },
  { value: '1664*928', label: '16:9 (1664x928)', aspect_ratio: '16:9' },
  { value: '928*1664', label: '9:16 (928x1664)', aspect_ratio: '9:16' },
  { value: '1472*1140', label: '4:3 (1472x1140)', aspect_ratio: '4:3' },
  { value: '1140*1472', label: '3:4 (1140x1472)', aspect_ratio: '3:4' }
]

