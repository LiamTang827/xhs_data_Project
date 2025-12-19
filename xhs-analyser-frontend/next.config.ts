import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n.ts");

const nextConfig: NextConfig = {
  /* xhs specific config can go here */
  
  // 可选：如果需要代理后端 API（避免 CORS 问题的另一种方案）
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: 'http://localhost:8000/:path*',
  //     },
  //   ];
  // },
};

export default withNextIntl(nextConfig);
