"use strict";

import Link from "next/link";
import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="flex flex-col items-center justify-between bg-red-500 px-6 py-2 text-white">
          <div className="mx-6 grow text-center">
            <h1 className="mb-2 text-xl font-bold md:text-2xl">
              <Link href="/">Sawt</Link>
            </h1>
          </div>
          <div className="flex flex-col items-start text-sm">
            <span>
              <Link href="/about">Learn more</Link> /{" "}
              <Link href="https://github.com/eye-on-surveillance/the-great-inquirer">
                Github
              </Link>
            </span>
          </div>
        </header>
        <main className="mb-12 min-h-screen bg-white p-6 text-black">
          {children}
        </main>
        <footer className="fixed bottom-0 mt-48 flex w-screen flex-col items-center justify-center bg-red-500 p-6 text-xs text-white">
          <div>
            <p className="md:sm text-sm font-light">
              &copy; {new Date().getFullYear()} Sawt
            </p>
          </div>
          <div className="mt-2">
            <h2 className=" text-xs md:text-sm">
              by{" "}
              <Link href={"https://eyeonsurveillance.org"}>
                Eye on Surveillance
              </Link>
            </h2>
          </div>
        </footer>
      </body>
    </html>
  );
}
