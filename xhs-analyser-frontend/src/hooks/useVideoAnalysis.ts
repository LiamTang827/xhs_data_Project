/**
 * 获取视频分析数据的React Hook
 */
import { useState, useEffect } from 'react';
import type { VideoAnalysisData } from '@/types/videoAnalysis';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

export function useVideoAnalysis(noteId?: string) {
  const [data, setData] = useState<VideoAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const url = noteId ? `${API_BASE_URL}/api/video-analysis?note_id=${encodeURIComponent(noteId)}` : `${API_BASE_URL}/api/video-analysis`;
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const jsonData = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        console.error('Error fetching video analysis:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        setData(null);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return { data, loading, error };
}
