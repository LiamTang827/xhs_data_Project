import { HomePage } from "@/components/HomePage";

interface PageProps {
  params: Promise<{ locale: string }>;
}

export default async function Page({ params }: PageProps) {
  await params; // Ensure params are resolved
  return <HomePage />;
}
