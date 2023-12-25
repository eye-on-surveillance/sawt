"use strict";

import CardResultsProvider from "@/components/CardResultsProvider";
import Footer from "@/components/Footer";
import Navbar from "@/components/NavBar/Navbar";
import { ECardStatus } from "@/lib/api";
import { TABLES } from "@/lib/supabase/db";
import { config } from "@fortawesome/fontawesome-svg-core";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { Analytics } from "@vercel/analytics/react";
import { cookies } from "next/headers";
import "./globals.css";
import styles from "./layout.module.scss";

config.autoAddCss = false;

export const dynamic = "force-dynamic";

// Metadata export for favicon
export const metadata = {
  favicon: "/photos/favicon.ico",
};

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
<div className={styles["nav-header"]}>
            <header className="items-center justify-center px-6 text-primary">
              <Navbar />
            </header>
            </div>
            <div className={styles["content"]}>
            <main className="min-h-[80vh] items-center justify-center">
              {children}
            </main>
            <footer className="items-center justify-center bg-purple px-6">
              <Footer />
            </footer>
          </div>
          </div>
          {modal}
        </CardResultsProvider>
        <Analytics />
      </body>
    </html>
  );
}
