import BetaCard from "@/components/BetaCard";
import Modal from "@/components/Modal";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";

export default async function CardModal({
  params,
}: {
  params: { cardId: string };
}) {
  const { cardId } = params;
  console.log("loading  card " + cardId);
  const card: any = await supabase
    .from(TABLES.CARDS)
    .select()
    .eq("id", cardId)
    .single();

  console.log("loaded card");
  console.log(card);

  return (
    <Modal>
      <div className="bg-slate-500 md:max-w-5xl">
        <BetaCard card={card} />
      </div>
    </Modal>
  );
}
