"use client";

import CardLoading from "./CardLoading";
import { useCardResults } from "./CardResultsProvider";
import QueryResult from "./QueryResult";

export default function HomeBanner() {
  const { cards } = useCardResults();
  const hasCards = cards.length > 0;

  return (
    <div className="min-h-[40vh] w-screen bg-indigo-800 px-6 py-12 sm:px-16">
      <div className="md:flex">
        <div className="md:grow"></div>
        <div className="md:w-3/4 md:max-w-2xl">
          {hasCards ? (
            cards.map((card) => <QueryResult key={card.id} card={card} />)
          ) : (
            <div className="space-y-7">
              <CardLoading />
              <CardLoading />
              <CardLoading />
            </div>
          )}
          {}
        </div>
        <div className="md:grow"></div>
      </div>
    </div>
  );
}
