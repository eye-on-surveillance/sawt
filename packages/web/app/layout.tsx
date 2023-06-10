import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'The Great Inquirer',
  description: 'Ask anything about New Orleans City Council meetings',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="p-4 bg-blue-500 text-white">
          <h1>{metadata.title}</h1>
          <p>{metadata.description}</p>
          <input type="search" placeholder="Search transcripts" className="mt-2 p-2 w-full" />
        </header>
        <main className="p-4">
          {children}
        </main>
        <footer className="p-4 bg-blue-500 text-white">
          <p>© {new Date().getFullYear()} The Great Inquirer</p>
        </footer>
      </body>
    </html>
  )
}
