"use strict";

import Footer from "../components/Footer";
import Navbar from "../components/Navbar";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen w-full overflow-hidden">
      <header className="items-center justify-center bg-blue-200 px-6 sm:px-16">
        <Navbar />
      </header>
      <main className="min-h-[80vh] items-center justify-center bg-blue-200">
        {children}
      </main>
      <footer className="items-center justify-center bg-violet-500 px-6 sm:px-16">
        <Footer />
      </footer>
    </div>
  );
}
