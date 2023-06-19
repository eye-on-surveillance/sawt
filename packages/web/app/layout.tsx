"use strict";
import Image from "next/image";
import Link from "next/link";
import React, { createContext, useContext, useEffect } from "react";
import "./globals.css";

const MetadataContext = createContext({
  title: "The Great New Orleanian Inquirer",
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
      <header className="flex items-center justify-between bg-red-500 px-6 py-2 text-white">
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
        <div className="mx-6 grow text-center">
          <h1 className="mb-2 text-xs font-bold md:text-base">
            {metadata.title}
          </h1>
          <p className="my-0 text-sm text-gray-200 md:text-base">
            Introducing the Great New Orleanian Inquirer—an innovative platform
            designed to bridge the gap between the residents of New Orleans and
            their city council representatives. Our mission is to provide an
            efficient and reliable channel for citizens to access accurate
            information based on the rich dataset derived from transcripts of
            city council meetings. Through our advanced language model (LLM), we
            aim to address the community&apos;s inquiries by leveraging the
            comprehensive knowledge gained from analyzing and understanding the
            discussions and decisions made during these meetings. The Great New
            Orleanian Inquirer empowers residents to obtain reliable insights,
            clarifications, and factual information, ensuring that their
            concerns are met with an informed and data-driven response.
          </p>
        </div>
        <div className="flex flex-col items-start text-sm">
          <Link href="/about">
            <p className="mb-2 cursor-pointer text-gray-200 underline">
              About Us
            </p>
          </Link>
          <a
            href="https://eyeonsurveillance.org/"
            className="cursor-pointer text-gray-200 underline"
          >
            About the Eye on Surveillance
          </a>
        </div>
      </header>
      <main className="bg-white p-6 text-black">{children}</main>
      <footer className="flex items-center justify-center bg-red-500 p-6 text-xs text-white">
        <p className="text-sm font-light md:text-base">
          &copy; {new Date().getFullYear()} The Great Inquirer
        </p>
      </footer>
    </>
  );
}
