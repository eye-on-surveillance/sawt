"use client"

import { ChangeEvent, useState } from "react"

export default function Home() {
  // const apiEndpoint = "https://getanswer5-q5odwl64qa-ue.a.run.app"
  const apiEndpoint = process.env.NEXT_PUBLIC_TGI_API_ENDPOINT!
  const [isProcessing, setIsProcessing] = useState(false)
  const [query, setQuery] = useState("")
  const [history, setHistory] = useState<any>([])

  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setQuery(e.target.value)
  }

  const submitQuery = async (e: ChangeEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsProcessing(true)
    try {
      const answerResp = await fetch(apiEndpoint, {
        method: "POST", 
        body: JSON.stringify({query}), 
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
      })
      const answer = await answerResp.text()
      setHistory([{query, answer, timestamp: new Date()}, ...history])
      setQuery("")
    } catch (error) {
      console.error("Failed to fetch answer:", error)
    }
    setIsProcessing(false)
  }

  const renderSingleHistory = (singleHistory: any) => (
    <div className="flex flex-row text-left my-3 p-4 border rounded-lg bg-gray-100" key={singleHistory.query}>
      <div>
        <span className="font-bold text-blue-600">Query: {singleHistory.query}</span>
        <span className="text-gray-500 text-xs"> (asked on {singleHistory.timestamp.toLocaleDateString()})</span>
      </div>
      <div className="ml-6">
        <span>Answer: {singleHistory.answer}</span>
      </div>
    </div>
  )

  const renderHistory = () => (
    <div className="mt-10">
      <h2 className="text-lg font-bold text-gray-700">Query history</h2>
      {history.map(renderSingleHistory)}
    </div>
  )

  const hasHistory = history.length > 0

  return (
    <main className="flex min-h-screen flex-col items-center p-24 text-center">
     <div>
      <h1 className="text-3xl font-bold">Enter your question about New Orleans City Council meetings</h1>
     </div>
     <div className="w-full mt-8">
      <form onSubmit={submitQuery}>
        <input value={query} onChange={handleQueryChange} disabled={isProcessing} type="text" className="w-full p-2 border-2 border-indigo-500 my-5 rounded-lg" placeholder="Please outline instances where the police describe how often they use facial recognition and its results"></input>
        <button type="submit" disabled={isProcessing} className="bg-teal-500 hover:bg-teal-700 rounded-md p-2 w-1/2 text-white">{isProcessing? "Processing..." : "Submit"}</button>
      </form>
     </div>
     {!hasHistory ? null : renderHistory()}
    </main>
  )
}
