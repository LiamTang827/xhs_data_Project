import { NextResponse } from 'next/server'

const API_BASE_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * POST /api/notes/search
 * 代理到后端 FastAPI 笔记语义搜索接口
 */
export async function POST(request: Request) {
  try {
    const body = await request.json()

    const response = await fetch(`${API_BASE_URL}/api/notes/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`[notes/search] Backend error: ${response.status}`, errorText)
      return NextResponse.json(
        { success: false, results: [], error: `Backend error: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('[notes/search] Error:', error)
    return NextResponse.json(
      { success: false, results: [], error: 'Internal server error' },
      { status: 500 }
    )
  }
}
