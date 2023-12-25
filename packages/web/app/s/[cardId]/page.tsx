import BetaCard from "@/components/Card/BetaCard";
import { getPageMetadata } from "@/lib/paths";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";

export async function generateMetadata({
  params,
}: {
  params: { cardId: string };
}) {
  const { cardId } = params;
  const { error, data: card } = await supabase
    .from(TABLES.CARDS)
    .select()
    .eq("id", cardId)
    .single();

  if (!!error) return getPageMetadata("Error");
  return getPageMetadata(card.title, true);
}

export default async function Card({ params }: { params: { cardId: string } }) {
  const { cardId } = params;
  const { error, data: card } = await supabase
    .from(TABLES.CARDS)
    .select()
    .eq("id", cardId)
    .single();

  if (error) throw new Error("Could not find card");

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
