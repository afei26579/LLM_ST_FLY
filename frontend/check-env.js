/**
 * 环境变量检查脚本
 * 运行: node check-env.js
 */

import { readFileSync, existsSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

console.log('🔍 正在检查前端环境配置...\n')

// 检查 .env.development 文件
const envPath = resolve(__dirname, '.env.development')
const envExists = existsSync(envPath)

if (!envExists) {
  console.log('❌ 未找到 .env.development 文件')
  console.log('📝 请创建该文件并配置以下变量：')
  console.log('')
  console.log('   VITE_API_BASE_URL=http://localhost:8000/api/v1')
  console.log('   VITE_GD_API_KEY=你的高德地图API_Key')
  console.log('')
  console.log('💡 参考：frontend/ENV_SETUP_GUIDE.md')
  process.exit(1)
}

console.log('✅ 找到 .env.development 文件\n')

// 读取并解析环境变量
const envContent = readFileSync(envPath, 'utf-8')
const envVars = {}

envContent.split('\n').forEach((line) => {
  const trimmed = line.trim()
  if (trimmed && !trimmed.startsWith('#')) {
    const [key, ...valueParts] = trimmed.split('=')
    if (key && valueParts.length > 0) {
      envVars[key.trim()] = valueParts.join('=').trim()
    }
  }
})

// 检查必需的变量
const required = ['VITE_API_BASE_URL', 'VITE_GD_API_KEY']
const optional = ['VITE_GD_SECURITY_CODE']

let hasError = false

console.log('📋 检查必需变量：\n')

required.forEach((key) => {
  if (envVars[key]) {
    const value = envVars[key]
    // 隐藏敏感信息
    const displayValue =
      key.includes('KEY') || key.includes('SECRET')
        ? `${value.substring(0, 8)}...`
        : value

    console.log(`   ✅ ${key} = ${displayValue}`)
  } else {
    console.log(`   ❌ ${key} 未配置`)
    hasError = true
  }
})

console.log('\n📋 检查可选变量：\n')

optional.forEach((key) => {
  if (envVars[key]) {
    const value = envVars[key]
    const displayValue =
      key.includes('KEY') || key.includes('SECRET')
        ? `${value.substring(0, 8)}...`
        : value

    console.log(`   ✅ ${key} = ${displayValue}`)
  } else {
    console.log(`   ⚪ ${key} 未配置（可选）`)
  }
})

// 验证 API Key 格式
console.log('\n🔍 验证配置：\n')

if (envVars.VITE_GD_API_KEY) {
  const key = envVars.VITE_GD_API_KEY
  if (key === 'your_gaode_api_key_here' || key.length < 20) {
    console.log('   ⚠️  高德地图 API Key 可能无效（使用了示例值或长度不足）')
    hasError = true
  } else {
    console.log('   ✅ 高德地图 API Key 格式正常')
  }
}

if (envVars.VITE_API_BASE_URL) {
  const url = envVars.VITE_API_BASE_URL
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    console.log('   ⚠️  API URL 格式可能有误（应以 http:// 或 https:// 开头）')
    hasError = true
  } else {
    console.log('   ✅ API URL 格式正常')
  }
}

// 最终结果
console.log('\n' + '='.repeat(50))
if (hasError) {
  console.log('❌ 配置检查失败，请修复上述问题')
  console.log('💡 参考文档：frontend/ENV_SETUP_GUIDE.md')
  process.exit(1)
} else {
  console.log('✅ 所有配置检查通过！')
  console.log('🚀 可以启动服务了：pnpm dev')
}
console.log('='.repeat(50) + '\n')

