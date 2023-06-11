"use client";
import { jsPDF } from "jspdf";
import { ChangeEvent, useState } from "react";

export default function Home() {
  const apiEndpoint = process.env.NEXT_PUBLIC_TGI_API_ENDPOINT!;
  const [isProcessing, setIsProcessing] = useState(false);
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<any>([]);

  const sampleQueries = [
    "Is NOPD's use of facial recognition effective?",
    "Were there any decisions made about the education budget in the last meeting?",
    "Has the issue of public transport been brought up in recent meetings?",
  ];

  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setQuery(e.target.value);
  };

  const handleQuerySelect = (query: string) => {
    setQuery(query);
  };

  const submitQuery = async (e: ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      const answerResp = await fetch(apiEndpoint, {
        method: "POST",
        body: JSON.stringify({ query }),
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const answer = await answerResp.text();
      setHistory([{ query, answer, timestamp: new Date() }, ...history]);
      setQuery("");
    } catch (error) {
      console.error("Failed to fetch answer:", error);
    }
    setIsProcessing(false);
  };

  const downloadTranscript = () => {
    const doc = new jsPDF();
    let cursor = 10;
    for (let i = history.length - 1; i >= 0; i--) {
      let lines = doc.splitTextToSize("Query: " + history[i].query, 180);
      doc.text(lines, 10, cursor);
      cursor += lines.length * 7;
      lines = doc.splitTextToSize("Response: " + history[i].answer, 180);
      doc.text(lines, 10, cursor);
      cursor += lines.length * 7 + 10;
    }
    doc.save("Transcript.pdf");
  };

  const renderSingleHistory = (singleHistory: any) => (
    <div className="my-4 rounded-lg border bg-gray-100 p-4" key={singleHistory.query}>
      <p className="font-bold text-blue-600">{singleHistory.query}</p>
      <p className="ml-6">{singleHistory.answer}</p>
    </div>
  );

  const renderHistory = () => <div className="mt-10">{history.map(renderSingleHistory)}</div>;

  const hasHistory = history.length > 0;

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-24 text-center">
      <div className="w-full md:w-2/3">
        <h1 className="text-3xl font-bold">
          Curious about the happenings in the New Orleans City Council? Ask away! Or pick a sample question if you're in need of inspiration.
        </h1>
      </div>
      <div className="w-full md:w-2/3 mt-8 flex flex-wrap justify-around">
        {sampleQueries.map((query, index) => (
          <div 
            key={index}
            className="p-4 m-2 border rounded-lg cursor-pointer hover:bg-gray-200"
            onClick={() => handleQuerySelect(query)}
          >
            {query}
          </div>
        ))}
      </div>
      <div className="w-full md:w-2/3 mt-8">
        <form onSubmit={submitQuery} className="space-y-4">
          <input
            value={query}
            onChange={handleQueryChange}
            disabled={isProcessing}
            type="text"
            className="w-full p-2 border-2 border-indigo-500 rounded-lg"
          />
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full rounded-md bg-teal-500 hover:bg-teal-700 p-2 text-white"
          >
            {isProcessing ? "Processing..." : "Ask"}
          </button>
        </form>
        {hasHistory && (
          <button
            onClick={downloadTranscript}
            className="mt-4 rounded-md bg-green-500 hover:bg-green-700 p-2 w-full text-white"
          >
            Download Transcript
          </button>
        )}
      </div>
      {hasHistory && renderHistory()}
    </main>
  );
}