"use client";

import { useCardResults } from "@/app/feedback/CardResultsProvider";
import BetaCard from "@/components/Card/BetaCard";
import { faClose } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useRouter } from "next/navigation";

export default async function ClientCard({ cardId }: { cardId: string }) {
  const { indexedCards } = useCardResults();
  const card = indexedCards.get(cardId);
  const router = useRouter();

  return (
    <div className="w-full bg-slate-200">
      <div
        className="w-full cursor-pointer px-6 py-4"
        onClick={() => router.back()}
      >
        <FontAwesomeIcon icon={faClose} className="fa-pull-right h-7 w-7" />
      </div>
      {!!card ? (
        <div className="px-12 py-6">
          <BetaCard card={card} />
        </div>
      ) : (
        <h1 className="p-12 text-lg">Unable to locate query</h1>
      )}
    </div>
  );
}
