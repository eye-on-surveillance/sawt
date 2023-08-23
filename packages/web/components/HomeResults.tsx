"use client";

import { useEffect, useRef, useState } from "react";
import { BeatLoader } from "react-spinners";
import CardLoading from "./CardLoading";
import { useCardResults } from "./CardResultsProvider";
import QueryResult from "./QueryResult";

export default function HomeBanner() {
  const { cards, fetchMoreCards, hasMoreCards } = useCardResults();
  const hasCards = cards.length > 0;

  // State and refs for infinite scrolling
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isInView, setIsInView] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleScroll = () => {
    if (containerRef.current && typeof window !== "undefined") {
      const container = containerRef.current;
      const { bottom } = container.getBoundingClientRect();
      const { innerHeight } = window;
      if (bottom <= innerHeight + 100) {
        setIsInView(true);
      }
    }
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  useEffect(() => {
    if (isInView && !isLoading && hasMoreCards) {
      // Check for hasMoreCards here
      setIsLoading(true);

      // Fetch more cards
      fetchMoreCards().then(() => {
        setIsInView(false);
        setIsLoading(false);
      });
    }
  }, [isInView, isLoading, fetchMoreCards, hasMoreCards]);

  return (
    <div
      ref={containerRef}
      className="min-h-[40vh] w-screen bg-indigo-800 px-6 py-12 sm:px-16"
    >
      <div className="md:flex">
        <div className="md:grow"></div>
        <div className="md:w-3/4 md:max-w-2xl">
          {hasCards &&
            cards.map((card) => <QueryResult key={card.id} card={card} />)}

          {isLoading && (
            <div className="my-4 flex items-center justify-center">
              <BeatLoader color="#FFFFFF" />
            </div>
          )}

          {!hasCards && !isLoading && (
            <div className="space-y-7">
              <CardLoading />
              <CardLoading />
              <CardLoading />
            </div>
          )}
        </div>
        <div className="md:grow"></div>
      </div>
    </div>
  );
}
