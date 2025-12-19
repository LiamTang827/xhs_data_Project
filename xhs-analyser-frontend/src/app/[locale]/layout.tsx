import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "../../app/globals.css";
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { Header } from "@/components/Header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "XHS Insight Studio",
  description: "Creator intelligence workspace for Xiaohongshu brands.",
};

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const messages = await getMessages({ locale });

  return (
    <div className={`${geistSans.variable} ${geistMono.variable} antialiased`}> 
      <NextIntlClientProvider messages={messages} locale={locale}>
        <Header currentLocale={locale} />
        {children}
      </NextIntlClientProvider>
    </div>
  );
}
