import BetaCard from "@/components/BetaCard";
import { useCardResults } from "@/components/CardResultsProvider";

export default async function ClientCard({
  params,
}: {
  params: { cardId: string };
}) {
  const { cardId } = params;
  const { indexedCards } = useCardResults();
  const card = indexedCards.get(cardId);

  return (
    <div className="bg-slate-500 md:max-w-5xl">
      {!!card ? <BetaCard card={card} /> : <h1>Unable to locate query</h1>}
    </div>
  );
}
