import { HomePage } from '@/components/HomePage'

interface PageProps {
  params: { locale: string }
}

export default async function LocalePage({ params }: PageProps) {
  // render the same HomePage used under src/app
  return <HomePage />
}
