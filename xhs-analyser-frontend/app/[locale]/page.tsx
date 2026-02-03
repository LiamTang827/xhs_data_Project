import { HomePage } from '@/components/HomePage'

interface PageProps {
  params: Promise<{ locale: string }>
}

export default async function LocalePage({ params }: PageProps) {
  // In Next.js 16+, params is a Promise and must be awaited
  await params
  // render the same HomePage used under src/app
  return <HomePage />
}
