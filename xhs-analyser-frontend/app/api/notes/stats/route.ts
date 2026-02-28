import { NextResponse } from 'next/server'

const API_BASE_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * GET /api/notes/stats
 * 获取笔记 embedding 统计信息
 */
export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/notes/stats`, {
      cache: 'no-store',
    })

    if (!response.ok) {
      return NextResponse.json(
        { total_notes: 0, total_creators: 0 },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('[notes/stats] Error:', error)
    return NextResponse.json(
      { total_notes: 0, total_creators: 0 },
      { status: 500 }
    )
  }
}
