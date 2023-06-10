import './globals.css'
import { Inter } from 'next/font/google'
import Image from 'next/image'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'The Great New Orleanian Inquirer by the Eye on Surveillance',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className + " bg-gray-50"}>
        <header className="p-4 bg-blue-600 text-white flex flex-col items-center space-y-4">
          <div className="w-32 h-32 md:w-48 md:h-48">
            <Image src="/photos/nolaflag.png" alt="New Orleans Flag" width={200} height={133} />
          </div>
          <h1 className="font-bold text-xl md:text-2xl">{metadata.title}</h1>
        </header>
        <main className="p-4">
          {children}
        </main>
        <footer className="p-4 bg-blue-600 text-white flex justify-center items-center">
          <p className="font-light text-sm md:text-base">© {new Date().getFullYear()} The Great Inquirer</p>
        </footer>
      </body>
    </html>
  )
}
