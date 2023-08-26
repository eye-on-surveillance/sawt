"use strict";

import CardResultsProvider from "@/components/CardResultsProvider";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { ECardStatus } from "@/lib/api";
import { TABLES } from "@/lib/supabase/db";
import { config } from "@fortawesome/fontawesome-svg-core";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { Analytics } from "@vercel/analytics/react";
import { cookies } from "next/headers";
import "./globals.css";
config.autoAddCss = false;

export const dynamic = "force-dynamic";

export default async function RootLayout({
  children,
  modal,
}: {
  children: React.ReactNode;
  modal: React.ReactNode;
}) {
  const supabase = createServerComponentClient({ cookies });
  const { data: cards } = await supabase
    .from(TABLES.CARDS)
    .select("*")
    .eq("status", ECardStatus.PUBLIC);

  return (
    <html lang="en">
      <body className="min-h-screen">
        {/* There is no user session so the new query input in the banner
        needs to locally communicated with results in order to identify
        queries created by the current user. */}
        <CardResultsProvider serverCards={cards || []}>
          <div className="min-h-screen w-full overflow-hidden">
            <header className="items-center justify-center bg-blue px-6 text-primary">
              <Navbar />
            </header>
            <main className="min-h-[80vh] items-center justify-center">
              {children}
            </main>
            <footer className="items-center justify-center bg-purple px-6">
              <Footer />
            </footer>
          </div>
          {modal}
        </CardResultsProvider>
        <Analytics />
      </body>
    </html>
  );
}
