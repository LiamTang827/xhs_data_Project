import { NextResponse } from 'next/server'

// 服务器端环境变量（不需要 NEXT_PUBLIC_ 前缀）
// 优先使用 API_URL，然后是 NEXT_PUBLIC_API_URL（兼容），最后是 localhost
const API_BASE_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

console.log('[creators/route] Using API_BASE_URL:', API_BASE_URL)

/**
 * GET /api/creators
 * 从后端FastAPI获取创作者网络数据并转换格式
 */
export async function GET() {
  try {
    console.log('[creators/route] Fetching from:', `${API_BASE_URL}/api/creators/network`)
    const response = await fetch(`${API_BASE_URL}/api/creators/network`, {
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.error(`[creators/route] Backend API error: ${response.status}`)
      const errorText = await response.text()
      console.error(`[creators/route] Error response:`, errorText)
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
    console.log('[creators/route] Backend response:', {
      creatorsCount: data.creators?.length || 0,
      edgesCount: data.edges?.length || data.creatorEdges?.length || 0
    })

    // 后端返回的数据结构：{ creators: [...], edges: [...], ... }
    // 前端期望：{ creators: [...], creatorEdges: [...], ... }
    // 需要将 edges 重命名为 creatorEdges
    
    const transformedData = {
      creators: data.creators || [],
      creatorEdges: data.creatorEdges || data.edges || [],
      trackClusters: data.trackClusters || {},
      trendingKeywordGroups: data.trendingKeywordGroups || [],
    }

    console.log('[creators/route] Transformed data:', {
      creatorsCount: transformedData.creators.length,
      edgesCount: transformedData.creatorEdges.length
    })

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
