import type { Metadata } from "next";
import Panel from "@/components/Panel";

export const metadata: Metadata = { title: "Panel", robots: { index: false, follow: false } };

export default function Admin() {
  return <Panel />;
}
