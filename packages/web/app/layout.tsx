"use client";
import Image from "next/image";
import Link from "next/link";
import React, { createContext, useContext, useEffect } from "react";
import "./globals.css";

const MetadataContext = createContext({
  title: "The Great New Orleanian Inquirer by the Eye on Surveillance",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const metadata = useContext(MetadataContext);

  useEffect(() => {
    document.documentElement.classList.remove("dark");
  }, []);

  return (
    <>
      <header className="flex flex-col items-center space-y-6 bg-red-500 p-6 text-white">
        <div className="h-36 w-36 md:h-52 md:w-52">
          <Image
            src="/photos/nolaflag.png"
            alt="New Orleans Flag"
            width={200}
            height={133}
          />
        </div>
        <h1 className="text-2xl font-bold md:text-3xl">{metadata.title}</h1>
      </header>
      <main className="bg-white p-6 text-black">{children}</main>
      <footer className="flex items-center justify-center bg-red-500 p-6 text-xs text-white">
        <p className="text-sm font-light md:text-base">
          &copy; {new Date().getFullYear()} The Great Inquirer
        </p>
        <Link href="/about" className="ml-6 text-xs text-gray-200 underline">
          About Us
        </Link>
      </footer>
    </>
  );
}
