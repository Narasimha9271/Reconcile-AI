export const metadata = { title: "ReconcileAI", description: "Invoice and purchase-order reconciliation" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
