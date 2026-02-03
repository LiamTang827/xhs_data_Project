'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';

interface AddCreatorDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface TaskProgress {
  percent: number;
  message: string;
}

interface TaskStatus {
  task_id: string;
  status: 'pending' | 'initializing' | 'checking' | 'fetching' | 'analyzing' | 'completed' | 'failed';
  progress: TaskProgress;
  error?: string;
}

export default function AddCreatorDialog({ isOpen, onClose, onSuccess }: AddCreatorDialogProps) {
  const t = useTranslations();
  const [userId, setUserId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState('');

  // 重置状态
  const resetState = () => {
    setUserId('');
    setIsSubmitting(false);
    setTaskStatus(null);
    setError('');
  };

  // 轮询任务状态
  useEffect(() => {
    if (!taskStatus || !taskStatus.task_id) return;
    if (taskStatus.status === 'completed' || taskStatus.status === 'failed') return;

    const pollInterval = setInterval(async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/creators/task/${taskStatus.task_id}`);
        
        if (!response.ok) {
          throw new Error('获取任务状态失败');
        }

        const data: TaskStatus = await response.json();
        setTaskStatus(data);

        // 任务完成
        if (data.status === 'completed') {
          clearInterval(pollInterval);
          setTimeout(() => {
            onSuccess();
            resetState();
            onClose();
          }, 1500);
        }

        // 任务失败
        if (data.status === 'failed') {
          clearInterval(pollInterval);
          setError(data.error || '添加失败');
          setIsSubmitting(false);
        }
      } catch (err) {
        console.error('轮询任务状态失败:', err);
      }
    }, 1000); // 每秒轮询一次

    return () => clearInterval(pollInterval);
  }, [taskStatus, onSuccess, onClose]);

  // 提交添加创作者
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userId.trim()) {
      setError('请输入用户ID');
      return;
    }

    // 简单验证ID格式
    if (userId.length < 10) {
      setError('用户ID格式不正确（至少10个字符）');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/creators/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          auto_update: true,
        }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.message || '添加失败');
      }

      // 开始轮询任务状态
      setTaskStatus({
        task_id: data.task_id,
        status: 'pending',
        progress: {
          percent: 0,
          message: '任务已创建...',
        },
      });

    } catch (err) {
      console.error('添加创作者失败:', err);
      setError(err instanceof Error ? err.message : '添加失败，请重试');
      setIsSubmitting(false);
    }
  };

  // 关闭对话框
  const handleClose = () => {
    if (isSubmitting && taskStatus?.status !== 'completed' && taskStatus?.status !== 'failed') {
      if (!confirm('任务正在进行中，确定要关闭吗？')) {
        return;
      }
    }
    resetState();
    onClose();
  };

  if (!isOpen) return null;

  // 获取状态显示文本
  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      pending: '⏳ 等待开始',
      initializing: '🔧 初始化中',
      checking: '🔍 检查创作者',
      fetching: '📥 爬取数据中',
      analyzing: '🤖 AI分析中',
      completed: '✅ 完成',
      failed: '❌ 失败',
    };
    return statusMap[status] || status;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">添加创作者</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
            disabled={isSubmitting && taskStatus?.status !== 'completed' && taskStatus?.status !== 'failed'}
          >
            ×
          </button>
        </div>

        {!taskStatus ? (
          // 输入表单
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                小红书用户ID
              </label>
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="例如: 5e6472940000000001008d4e"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
              />
              <p className="mt-1 text-xs text-gray-500">
                打开小红书用户主页，从URL中复制用户ID
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={isSubmitting}
              >
                取消
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                disabled={isSubmitting}
              >
                {isSubmitting ? '处理中...' : '添加'}
              </button>
            </div>
          </form>
        ) : (
          // 进度显示
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-4xl mb-2">{getStatusText(taskStatus.status)}</div>
              <p className="text-gray-600">{taskStatus.progress.message}</p>
            </div>

            {/* 进度条 */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  taskStatus.status === 'completed'
                    ? 'bg-green-500'
                    : taskStatus.status === 'failed'
                    ? 'bg-red-500'
                    : 'bg-blue-500'
                }`}
                style={{ width: `${taskStatus.progress.percent}%` }}
              />
            </div>

            <div className="text-center text-sm text-gray-500">
              {taskStatus.progress.percent}%
            </div>

            {/* 错误信息 */}
            {taskStatus.status === 'failed' && taskStatus.error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{taskStatus.error}</p>
              </div>
            )}

            {/* 完成/失败后的按钮 */}
            {(taskStatus.status === 'completed' || taskStatus.status === 'failed') && (
              <button
                onClick={handleClose}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {taskStatus.status === 'completed' ? '完成' : '关闭'}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
