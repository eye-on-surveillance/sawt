"use client";
import { jsPDF } from "jspdf";
import { ChangeEvent, useState } from "react"
import ALL_SOURCES from "public/metadata.json" assert { type: "json" };

export default function Home() {
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
      const answerWSources = await answerResp.text()
      const [answer, _sources] = answerWSources.split("SOURCES: ")
      const sources = !_sources ||  _sources === "N/A" ? [] : _sources.split(",")
      setHistory([{query, answer, timestamp: new Date(), sources}, ...history])
      setQuery("")
    } catch (error) {
      console.error("Failed to fetch answer:", error)
    }
    setIsProcessing(false)
  }

  const downloadTranscript = () => {
    const doc = new jsPDF();
    let cursor = 10;
    for (let i = history.length - 1; i >= 0; i--) {
      let lines = doc.splitTextToSize('Query: ' + history[i].query, 180);
      doc.text(lines, 10, cursor);
      cursor += (lines.length * 7);
      lines = doc.splitTextToSize('Response: ' + history[i].answer, 180);
      doc.text(lines, 10, cursor);
      cursor += (lines.length * 7) + 10;
    }
    doc.save('Transcript.pdf');
  }

  const renderSource = (sourceId: string) => {
    const sourceIdStripped = sourceId.replaceAll(" ", "")
    const source = (ALL_SOURCES as any)[sourceIdStripped]

    return (
      <li key={crypto.randomUUID()}><a href={source?.video_url}>{source?.title}; uploaded on {source?.publish_date}</a></li>
    )
  }

  const renderSingleHistory = (singleHistory: any) => (
    <div className="my-4 p-4 border rounded-lg bg-gray-100" key={crypto.randomUUID()}>
      <p className="font-bold text-blue-600">{singleHistory.query}</p>
      <p className="mx-6">{singleHistory.answer}</p>
      <ul className="text-sm mt-3 list-disc list-inside">
        <p><strong>Sources:</strong></p>
        {singleHistory.sources.length === 0 ? <p>None</p> : singleHistory.sources.map(renderSource)}
      </ul>
    </div>
  )

  const renderHistory = () => (
    <div className="mt-10">
      {history.map(renderSingleHistory)}
    </div>
  )

  const hasHistory = history.length > 0

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-24 text-center">
     <div className="w-full md:w-2/3">
      <h1 className="text-3xl font-bold">Curious about the happenings in the New Orleans City Council? Ask away!</h1>
     </div>
     <div className="w-full md:w-2/3 mt-8">
      <form onSubmit={submitQuery} className="space-y-4">
        <input value={query} onChange={handleQueryChange} disabled={isProcessing} type="text" className="w-full p-2 border-2 border-indigo-500 rounded-lg" ></input>
        <button type="submit" disabled={isProcessing} className="w-full bg-teal-500 hover:bg-teal-700 rounded-md p-2 text-white">{isProcessing? "Processing..." : "Ask"}</button>
      </form>
      {!hasHistory ? null : <button onClick={downloadTranscript} className="mt-4 bg-green-500 hover:bg-green-700 rounded-md p-2 w-full text-white">Download Transcript</button>}
     </div>
     {!hasHistory ? null : renderHistory()}
    </main>
  )
}
