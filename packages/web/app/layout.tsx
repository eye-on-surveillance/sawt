"use strict";
import React, { useEffect, useState, useContext } from 'react';
import './globals.css';
import { Inter } from 'next/font/google';
import { createContext } from 'react';
import Image from 'next/image';

const inter = Inter({ subsets: ['latin'] });

export const MetadataContext = createContext({
  title: 'The Great New Orleanian Inquirer by the Eye on Surveillance',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const metadata = useContext(MetadataContext);

  useEffect(() => {
    setIsDarkMode(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }, []);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <>
      <header className="p-4 bg-blue-600 text-white flex flex-col items-center space-y-4">
        <div className="w-32 h-32 md:w-48 md:h-48">
          <Image src="/photos/nolaflag.png" alt="New Orleans Flag" width={200} height={133} />
        </div>
        <h1 className="font-bold text-xl md:text-2xl">{metadata.title}</h1>
      </header>
      <main className="p-4">{children}</main>
      <footer className="p-4 bg-blue-600 text-white flex justify-center items-center text-xs">
        <p className="font-light text-sm md:text-base">&copy; {new Date().getFullYear()} The Great Inquirer</p>
        <a href="/about" className="ml-4 underline text-xs text-gray-200">About Us</a>
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="ml-4 bg-gray-200 p-1 rounded"
        >
          Toggle Dark Mode
        </button>
      </footer>
    </>
  );
}
