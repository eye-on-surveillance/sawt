"use client";

import { ICard, RESPONSE_TYPE_GENERAL } from "@/lib/api";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";
import { faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ChangeEvent, useState } from "react";
import Cards from "./components/Cards";
import ResponseToggle from "./components/ResponseToggle";

// Predefined queries
const predefinedQueries = [
  "What is city council doing to address racial inequality?",
  "What is a proviso?",
  "Is NOPD's use of facial recognition effective according to quarterly reports",
];

export default function Home() {
  const apiEndpoint = process.env.NEXT_PUBLIC_TGI_API_ENDPOINT!;
  const [isProcessing, setIsProcessing] = useState(false);
  const [query, setQuery] = useState("");
  const [responseMode, setResponseMode] = useState(RESPONSE_TYPE_GENERAL);
  const [cards, setCards] = useState<ICard[]>([]);

  const handleQueryChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setQuery(e.target.value);
  };

  const handlePredefinedQueryClick = (predefinedQuery: string) => {
    setQuery(predefinedQuery);
  };

  const recordQueryAsked = async () => {
    const newQuery = {
      query,
      response_type: responseMode,
    };
    const { data: queryData, error } = await supabase
      .from(TABLES.USER_QUERIES)
      .insert([newQuery])
      .select();

    if (error) {
      console.warn("Could not record query");
      console.warn(error);
      return "";
    } else {
      const { id } = queryData[0];
      return id;
    }
  };

  const updateQueryResponded = async (
    card: ICard,
    queryId: string,
    startedProcessingAt: number
  ) => {
    if (queryId.length <= 0) return;

    const genResponseSecs = Math.ceil(
      (Date.now() - startedProcessingAt) / 1000
    );
    const queryUpdate = {
      response: JSON.stringify(card),
      gen_response_secs: genResponseSecs,
    };
    const { error } = await supabase
      .from(TABLES.USER_QUERIES)
      .update(queryUpdate)
      .eq("id", queryId);

    if (error) {
      console.warn("Could not record query");
      console.warn(error);
      return;
    } else {
    }
  };

  const compareCards = (a: ICard, b: ICard) => {
    return b.local_timestamp.getTime() - a.local_timestamp.getTime();
  };
  const submitQuery = async (e: ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      // Record question in DB
      const startedProcessingAt = Date.now();
      const queryId = await recordQueryAsked();

      // Start processing question
      const answerResp = await fetch(apiEndpoint, {
        method: "POST",
        body: JSON.stringify({ query, response_type: responseMode }), // Pass responseMode to your API endpoint
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const card: ICard = await answerResp.json();
      card.query = query;
      card.local_timestamp = new Date();
      await updateQueryResponded(card, queryId, startedProcessingAt);
      setCards((oldCards: any) => {
        const newCards = [...oldCards, card];
        newCards.sort(compareCards);
        return newCards;
      });
      setQuery("");
    } catch (error) {
      console.error("Failed to fetch answer:", error);
    }
    setIsProcessing(false);
  };

  const hasHistory = cards.length > 0;

  const clearHistory = () => {
    setCards([]);
  };

  return (
    <div className="mt-14 flex flex-col items-center p-4 text-center md:space-y-6">
      <div className="w-full space-y-7 md:w-2/3">
        <p className="text-2xl">Curious about New Orleans City Council?</p>
        <p className="text-sm text-gray-500">
          Type or choose a question from one of the prompts below and let us
          find the answer for you.
        </p>

        <ResponseToggle onToggle={setResponseMode} />

        <form onSubmit={submitQuery} className="space-y-4">
          <div className="relative">
            <input
              value={query}
              onChange={handleQueryChange}
              disabled={isProcessing}
              type="text"
              className="w-full rounded-lg border-2 border-indigo-500 p-2 pl-12 shadow-lg"
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
            {isProcessing ? "Searching for your answer..." : "Ask"}
          </button>
        </form>
        <div className="my-4">
          {predefinedQueries.map((predefinedQuery, index) => (
            <button
              key={index}
              onClick={(e) => {
                e.preventDefault();
                handlePredefinedQueryClick(predefinedQuery);
              }}
              className="m-2 rounded-full bg-gray-200 p-2 text-sm text-blue-500 hover:bg-gray-300"
            >
              {predefinedQuery}
            </button>
          ))}
        </div>
        {hasHistory && Cards(cards, clearHistory)}
      </div>
    </div>
  );
}
