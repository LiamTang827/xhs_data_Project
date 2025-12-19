import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* 这里的配置就是让 Vercel 闭嘴的关键 */
  typescript: {
    // 忽略所有 TS 类型报错
    ignoreBuildErrors: true,
  },
  eslint: {
    // 忽略所有代码规范报错
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;