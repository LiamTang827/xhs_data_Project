import { NextResponse } from 'next/server'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * GET /api/style/creators
 * 从后端FastAPI获取可模仿的创作者列表
 */
export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/style/creators`, {
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.error(`Backend API error: ${response.status}`)
      return NextResponse.json(
        {
          success: false,
          creators: [],
          error: `Backend returned ${response.status}`,
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching style creators from backend:', error)
    return NextResponse.json(
      {
        success: false,
        creators: [],
        error: String(error),
      },
      { status: 500 }
    )
  }
}
