import { NextResponse } from 'next/server'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * GET /api/creators
 * 从后端FastAPI获取创作者网络数据并转换格式
 */
export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/creators/network`, {
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.error(`Backend API error: ${response.status}`)
      return NextResponse.json(
        {
          creators: [],
          creatorEdges: [],
          trackClusters: {},
          trendingKeywordGroups: [],
        },
        { status: response.status }
      )
    }

    const data = await response.json()

    // 后端返回的数据结构：{ creators: [...], edges: [...], ... }
    // 前端期望：{ creators: [...], creatorEdges: [...], ... }
    // 需要将 edges 重命名为 creatorEdges
    
    const transformedData = {
      creators: data.creators || [],
      creatorEdges: data.creatorEdges || data.edges || [],
      trackClusters: data.trackClusters || {},
      trendingKeywordGroups: data.trendingKeywordGroups || [],
    }

    return NextResponse.json(transformedData)
  } catch (error) {
    console.error('Error fetching creators from backend:', error)
    return NextResponse.json(
      {
        creators: [],
        creatorEdges: [],
        trackClusters: {},
        trendingKeywordGroups: [],
      },
      { status: 500 }
    )
  }
}
