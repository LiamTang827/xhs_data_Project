"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import StepSelectCreator from "./workflow/StepSelectCreator";
import StepMatchCreators from "./workflow/StepMatchCreators";
import StepGenerateContent from "./workflow/StepGenerateContent";

interface Creator {
  nickname: string;
  name?: string;
  user_id: string;
  followers: number;
  total_engagement: number;
  note_count?: number;
  topics: string[];
  avatar?: string;
  style?: string;
  platform?: string;
}

interface ContentOpportunity {
  note_title: string;
  note_id: string;
  engagement_index: number;
  engagement_count: number;
  reason: string;
  direction: string;
  angles: string[];
}

export function ContentStudio() {
  const steps = [
    { number: 1, title: "选择身份", description: "我是谁？" },
    { number: 2, title: "发现灵感", description: "匹配博主 & 找爆品方向" },
    { number: 3, title: "生成文案", description: "根据调性生成内容文案" }
  ];

  const [currentStep, setCurrentStep] = useState(1);
  const [workflowData, setWorkflowData] = useState({
    myCreator: null as Creator | null,
    similarCreators: [] as Creator[],
    selectedCompetitor: null as Creator | null,
    contentOpportunities: [] as ContentOpportunity[],
    selectedContent: null as ContentOpportunity | null,
    generatedContent: "",
    minEngagement: 1.0,
    topN: 5,
    days: null as number | null
  });

  const updateWorkflowData = (updates: any) => {
    setWorkflowData(prev => ({ ...prev, ...updates }));
  };

  const handleStepComplete = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setWorkflowData({
      myCreator: null,
      similarCreators: [],
      selectedCompetitor: null,
      contentOpportunities: [],
      selectedContent: null,
      generatedContent: "",
      minEngagement: 1.0,
      topN: 5,
      days: null
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* 头部 */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-black/5 shadow-xs">
        <div className="container mx-auto px-4 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="inline-flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 transition-colors"
              >
                ← 返回首页
              </Link>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
                ✨ 内容创作工作室
              </h1>
            </div>
            {currentStep > 1 && (
              <button
                onClick={handleReset}
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                重新开始
              </button>
            )}
          </div>
        </div>
      </header>

      {/* 进度条 */}
      <div className="bg-white border-b border-black/5">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            {steps.map((step, idx) => (
              <div key={step.number} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  {/* 步骤圆圈 */}
                  <button
                    onClick={() => {
                      if (step.number < currentStep) {
                        setCurrentStep(step.number);
                      }
                    }}
                    disabled={step.number > currentStep}
                    className={`
                      w-12 h-12 rounded-full font-bold text-sm mb-2 transition-all
                      ${
                        step.number < currentStep
                          ? "bg-green-500 text-white cursor-pointer hover:bg-green-600"
                          : step.number === currentStep
                          ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white ring-4 ring-purple-200"
                          : "bg-gray-200 text-gray-600 cursor-not-allowed"
                      }
                    `}
                  >
                    {step.number < currentStep ? "✓" : step.number}
                  </button>
                  <div className="text-center">
                    <div className="text-xs font-semibold text-black">{step.title}</div>
                    <div className="text-xs text-black/50">{step.description}</div>
                  </div>
                </div>

                {/* 连接线 */}
                {idx < steps.length - 1 && (
                  <div className="flex-1 h-1 mx-3 mb-8">
                    <div
                      className={`
                        h-full transition-colors
                        ${step.number < currentStep ? "bg-green-500" : "bg-gray-200"}
                      `}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Step 1: 选择创作者身份 */}
          {currentStep === 1 && (
            <StepSelectCreator
              onCreatorSelected={(creator) => {
                updateWorkflowData({ myCreator: creator });
                handleStepComplete();
              }}
            />
          )}

          {/* Step 2: 发现灵感（匹配博主 + 发现爆品，合并） */}
          {currentStep === 2 && workflowData.myCreator && (
            <StepMatchCreators
              myCreator={workflowData.myCreator}
              selectedCompetitor={workflowData.selectedCompetitor}
              contentOpportunities={workflowData.contentOpportunities}
              minEngagement={workflowData.minEngagement}
              topN={workflowData.topN}
              days={workflowData.days}
              onCompetitorSelected={(competitor) => {
                updateWorkflowData({ selectedCompetitor: competitor, contentOpportunities: [] });
              }}
              onContentDiscovered={(opportunities) => {
                updateWorkflowData({ contentOpportunities: opportunities });
              }}
              onContentSelected={(content) => {
                updateWorkflowData({ selectedContent: content });
                handleStepComplete();
              }}
              onParameterChange={(params) => {
                updateWorkflowData(params);
              }}
              onBack={handleBack}
            />
          )}

          {/* Step 3: 生成内容文案 */}
          {currentStep === 3 && workflowData.myCreator && workflowData.selectedContent && (
            <StepGenerateContent
              myCreator={workflowData.myCreator}
              selectedContent={workflowData.selectedContent}
              onContentGenerated={(content) => {
                updateWorkflowData({ generatedContent: content });
              }}
              onBack={handleBack}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </div>
  );
}
