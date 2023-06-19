"use strict";
import Image from "next/image";
import Link from "next/link";
import React, { createContext, useContext, useEffect } from "react";
import "./globals.css";

const MetadataContext = createContext({
  title: "The Great New Orleanian Inquirer",
});

export default function RootLayout({ children }: { children: React.ReactNode; }) {
  const metadata = useContext(MetadataContext);

  useEffect(() => {
    document.documentElement.classList.remove("dark");
  }, []);

  return (
    <>
      <header className="flex bg-red-500 px-6 py-2 text-white items-center justify-between">
        <div className="self-center">
          <div className="h-42 w-42 md:h-42 md:w-42">
            <Image
              src="/photos/nolaflag.png"
              alt="New Orleans Flag"
              width={200}
              height={800}
              layout="responsive"
            />
          </div>
        </div>
        <div className="mx-6 flex-grow text-center">
          <h1 className="text-xs font-bold md:text-base mb-2">{metadata.title}</h1>
          <p className="text-gray-200 my-0 text-sm md:text-base">
            The Great New Orleanian Inquirer is a groundbreaking platform designed to foster direct communication between the residents of New Orleans and their city council representatives. Our mission is to empower the community by providing a seamless and efficient channel for citizens to express their concerns, ask questions, and receive accurate information directly from their elected officials.
          </p>
        </div>
        <div className="flex flex-col items-start text-sm">
          <Link href="/about">
            <p className="cursor-pointer text-gray-200 underline mb-2">About Us</p>
          </Link>
          <a href="https://eyeonsurveillance.org/" className="cursor-pointer text-gray-200 underline">About the Eye on Surveillance</a>
        </div>
      </header>
      <main className="bg-white p-6 text-black">
        {children}
      </main>
      <footer className="flex items-center justify-center bg-red-500 p-6 text-xs text-white">
        <p className="text-sm font-light md:text-base">
          &copy; {new Date().getFullYear()} The Great Inquirer
        </p>
      </footer>
    </>
  );
}
