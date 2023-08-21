"use client";

import BetaCard from "@/components/BetaCard";
import { useCardResults } from "@/components/CardResultsProvider";

export default async function ClientCard({ cardId }: { cardId: string }) {
  const { indexedCards } = useCardResults();
  const card = indexedCards.get(cardId);

  return (
    <div className="bg-slate-200 md:max-w-5xl">
      {!!card ? (
        <BetaCard card={card} />
      ) : (
        <h1 className="p-12 text-lg">Unable to locate query</h1>
      )}
    </div>
  );
}
