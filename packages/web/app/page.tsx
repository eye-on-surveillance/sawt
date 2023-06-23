"use client";
import { faDownload, faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { jsPDF } from "jspdf";
import { ChangeEvent, useState } from "react";
import ResponseToggle from "./components/ResponseToggle";

interface HistoryItem {
  query: string;
  answer: string;
}

// Predefined queries
const predefinedQueries = [
  "Why is crime on the rise in New Orleans?",
  "What is the city doing to mitigate the rise of crime?",
  "Provide a detailed report on NOPD's use of facial recognition according to quarterly reports",
];

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [responseMode, setResponseMode] = useState("General Summary");

  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setQuery(e.target.value);
  };

  const handlePredefinedQueryClick = (predefinedQuery: string) => {
    setQuery(predefinedQuery);
  };

  const handleResponseModeToggle = (selected: string) => {
    setResponseMode(selected);
  };

  const submitQuery = async (e: ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsProcessing(true);

    const res = await fetch("/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
        responseMode: responseMode,
      }),
    });

    const { answer } = await res.json();
    setIsProcessing(false);

    setHistory((prevHistory) => [
      ...prevHistory,
      { query: query, answer: answer },
    ]);
  };

  const downloadTranscript = () => {
    const doc = new jsPDF();
    let cursor = 10;
    let pageNumber = 1;

    for (let i = history.length - 1; i >= 0; i--) {
      let lines = doc.splitTextToSize("Query: " + history[i].query, 180);
      const queryPageHeight = lines.length * 7;
      const responsePageHeight = 7;

      if (
        cursor + queryPageHeight + responsePageHeight >
        doc.internal.pageSize.getHeight()
      ) {
        doc.addPage();
        cursor = 10;
        pageNumber++;
      }

      doc.text(lines, 10, cursor);
      cursor += queryPageHeight;

      lines = doc.splitTextToSize("Response: " + history[i].answer, 180);
      doc.text(lines, 10, cursor);
      cursor += lines.length * 7 + 10;
    }

    doc.save(`Transcript_Page_${pageNumber}.pdf`);
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const renderSingleHistory = (singleHistory: HistoryItem) => (
    <div
      className="my-4 rounded-lg border bg-gray-100 p-4"
      key={singleHistory.query}
    >
      <p className="font-bold text-blue-600">{singleHistory.query}</p>
      <p className="mx-6" style={{ whiteSpace: "pre-line" }}>
        {singleHistory.answer}
      </p>
    </div>
  );

  const renderHistory = () => (
    <div className="mt-10">
      {history.map(renderSingleHistory)}
      <button
        onClick={clearHistory}
        className="mt-4 text-sm text-red-500 underline"
      >
        Clear History
      </button>
    </div>
  );

  const hasHistory = history.length > 0;

  const title =
    "Discover What's Happening Behind Closed Doors at the New Orleans City Council";
  return (
    <main className="flex flex-col items-center space-y-4 p-4 text-center md:space-y-6 md:p-24">
      <div className="w-full space-y-8 md:w-2/3">
        <h1 className="text-3xl font-bold">{title}</h1>
        <p className="text-sm text-gray-500">
          Type or choose a question from one of the prompts below and let us
          find the answer for you.
        </p>
        <div className="my-4">
          {predefinedQueries.map((predefinedQuery, index) => (
            <button
              key={index}
              onClick={() => handlePredefinedQueryClick(predefinedQuery)}
              className="m-2 rounded-full bg-gray-200 p-1 text-sm text-blue-500 hover:bg-gray-300"
            >
              {predefinedQuery}
            </button>
          ))}
        </div>
        <ResponseToggle onToggle={handleResponseModeToggle} />
        <form onSubmit={submitQuery} className="space-y-4">
          <div className="relative">
            <input
              value={query}
              onChange={handleQueryChange}
              disabled={isProcessing}
              type="text"
              className="w-full rounded-lg border-2 border-indigo-500 p-2 pl-10 shadow-lg"
              placeholder="Type your question here"
            />
            <FontAwesomeIcon
              icon={faSearch}
              className="absolute left-3 top-1/2 h-7 w-7 -translate-y-1/2 text-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full rounded-md bg-teal-500 p-2 text-white shadow-lg hover:bg-teal-700"
          >
            {isProcessing ? "Searching" : "Ask"}
          </button>
        </form>
        {hasHistory && (
          <button
            onClick={downloadTranscript}
            className="mt-4 flex w-full items-center justify-center space-x-2 rounded-md bg-green-500 p-2 text-white shadow-lg hover:bg-green-700"
          >
            <FontAwesomeIcon icon={faDownload} />
            <span>Download Transcript</span>
          </button>
        )}
        {hasHistory && renderHistory()}
      </div>
    </main>
  );
}
