import { NextIntlClientProvider } from 'next-intl'
import { getMessages } from 'next-intl/server'
import '../../src/app/globals.css'
import { Header } from '@/components/Header'

export default async function LocaleLayout({ 
  children, 
  params 
}: { 
  children: React.ReactNode; 
  params: Promise<{ locale: string }> 
}) {
  // In Next.js 16+, params is a Promise and must be awaited
  const { locale } = await params

  const messages = await getMessages({ locale })

  return (
    <NextIntlClientProvider messages={messages} locale={locale}>
      <Header currentLocale={locale} />
      {children}
    </NextIntlClientProvider>
  )
}
