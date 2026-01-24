import { NextResponse } from 'next/server'
import path from 'path'
import fs from 'fs'

const WORKSPACE_ROOT = process.cwd()
const BASE_DIR = WORKSPACE_ROOT.endsWith('xhs-analyser-frontend') 
  ? path.join(WORKSPACE_ROOT, '..') 
  : WORKSPACE_ROOT
const DATA_DIR = path.join(BASE_DIR, 'backend', 'data')
const CREATORS_DATA_FILE = path.join(DATA_DIR, 'creators_data.json')

/**
 * GET /api/style/creators
 * 返回所有可供模仿风格的创作者列表
 * 从MongoDB生成的creators_data.json读取
 */
export async function GET() {
  try {
    // 优先从creators_data.json读取（100%从数据库生成）
    if (fs.existsSync(CREATORS_DATA_FILE)) {
      const raw = fs.readFileSync(CREATORS_DATA_FILE, 'utf8')
      const data = JSON.parse(raw)
      
      // 转换为风格创作者列表格式
      const styleCreators = (data.creators || []).map((creator: any) => ({
        user_id: creator.id,
        nickname: creator.name,
        avatar: creator.avatar || '',
        desc: creator.desc || '',
        fans: creator.followers || 0,
        ip_location: creator.ipLocation || '',
        total_notes: creator.total_notes || 0
      }))
      
      console.log(`[api/style/creators] ✅ 返回 ${styleCreators.length} 个创作者`)
      return NextResponse.json(styleCreators)
    }
    
    // 如果文件不存在，返回空数组
    console.warn('[api/style/creators] ⚠️ creators_data.json 不存在')
    return NextResponse.json([])
    
  } catch (error) {
    console.error('[api/style/creators] ❌ 错误:', error)
    return NextResponse.json(
      { error: 'Failed to load creators' },
      { status: 500 }
    )
  }
}
