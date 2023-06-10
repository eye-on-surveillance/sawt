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
          <Image src="/photos/nolaflag.png" alt="New Orleans Flag" width={200} height={133} />
          <h1 className="font-bold text-xl">{metadata.title}</h1>
        </header>
        <main className="p-4">
          {children}
        </main>
        <footer className="p-4 bg-blue-600 text-white flex justify-center items-center">
          <p className="font-light">© {new Date().getFullYear()} The Great Inquirer</p>
        </footer>
      </body>
    </html>
  )
}
