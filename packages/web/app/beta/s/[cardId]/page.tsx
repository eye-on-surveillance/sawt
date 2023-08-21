import BetaCard from "@/components/BetaCard";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";

export default async function Card({ params }: { params: { cardId: string } }) {
  const { cardId } = params;
  console.log("loading  card " + cardId);
  const { error, data: card } = await supabase
    .from(TABLES.CARDS)
    .select()
    .eq("id", cardId)
    .single();

  console.log("loaded card");
  console.log(card);

  return (
    <div className="px-6 py-5 text-left sm:px-16 md:flex">
      <div className="md:grow"></div>
      <div className="md:w-3/4 md:max-w-2xl">
        <BetaCard card={card} />
      </div>
      <div className="md:grow"></div>
    </div>
  );
}
