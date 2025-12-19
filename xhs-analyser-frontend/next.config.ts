import createNextIntlPlugin from 'next-intl/plugin';

// 初始化多语言插件
const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig = {
  // 1. 依然保持忽略 TS 报错
  typescript: {
    ignoreBuildErrors: true,
  },
  // 2. 依然保持忽略 ESLint 报错
  eslint: {
    ignoreDuringBuilds: true,
  },
};

// 3. 关键修复：用 withNextIntl 包裹配置并导出
export default withNextIntl(nextConfig);