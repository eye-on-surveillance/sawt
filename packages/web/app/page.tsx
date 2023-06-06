"use client"

import { ChangeEvent, useState } from "react"

export default function Home() {
  const apiEndpoint = "https://getanswer2-q5odwl64qa-ue.a.run.app"
  const [isProcessing, setIsProcessing] = useState(false)
  const [query, setQuery] = useState("")
  const [history, setHistory] = useState<any>([])

  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setQuery(e.target.value)
  }

  const submitQuery = async () => {
    setIsProcessing(true)
    const answerResp = await fetch(apiEndpoint, {
      method: "POST", 
      body: JSON.stringify({query}), 
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      }
    ,})
    const answer = await answerResp.text()
    setHistory([{query, answer}, ...history])
    setQuery("")
    setIsProcessing(false)
  }

  const renderSingleHistory = (singleHistory: any) => (
    <div className="flex flex-row text-left my-3" key={singleHistory.query}>
      <div>
        <span>Query: {singleHistory.query}</span>
      </div>
      <div className="ml-6">
        <span>Answer: {singleHistory.answer}</span>
      </div>
    </div>
  )

  const renderHistory = () => (
    <div className="mt-10">
      <p className="text-lg">Query history</p>
      {history.map(renderSingleHistory)}
    </div>
  )

  const hasHistory = history.length > 0

  return (
    <main className="flex min-h-screen flex-col items-center p-24 text-center">
     <div>
      <p className="text-2xl">Enter your question about New Orleans City Council meetings</p>
     </div>
     <div className="w-full">
      <form>
        <input value={query} onChange={handleQueryChange} disabled={isProcessing} type="text" className="w-full border-indigo-500 my-5" placeholder="Please outline instances where the police describe how often they use facial recognition and its results"></input>
        <button onClick={submitQuery} disabled={isProcessing} className="bg-teal-500 rounded-md p-2 w-1/2 text-white">{isProcessing? "Processing..." : "Submit"}</button>
      </form>
     </div>
     {!hasHistory ? null : renderHistory()}
    </main>
  )
}
