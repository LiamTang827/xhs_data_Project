"use client";

import { Link } from "@/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "./LanguageSwitcher";

interface HeaderProps {
  currentLocale: string;
}

export function Header({ currentLocale }: HeaderProps) {
  const t = useTranslations("header");

  return (
    <header className="border-b border-black/10 bg-white/90 backdrop-blur">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          {t("brand")}
        </Link>
        <LanguageSwitcher />
      </div>
    </header>
  );
}
