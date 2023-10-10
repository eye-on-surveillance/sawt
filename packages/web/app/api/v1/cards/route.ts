import { ECardStatus, ICard } from "@/lib/api";
import { TABLES } from "@/lib/supabase/db";
import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
export const dynamic = "force-dynamic";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "PLACEHOLDER";
const supabaseSecretServiceKey =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "PLACEHOLDER";

/* Create card
 * Not creating directly from client because:
 *  - We have RLS enabled that only allows to view cards in 'public' status
 *  - All cards start off in 'new' status
 *  - This leads to users being able to create cards, but unable to retrieve their IDs directly
 *  - Easier to protect vars such as 'likes' with default valuse
 */
export async function POST(request: Request) {
  const cookieStore = cookies();
  const { title, card_type } = (await request.json()) as ICard;
  const supabase = createClient(supabaseUrl, supabaseSecretServiceKey);

  const card = {
    title,
    card_type,
    status: ECardStatus.NEW,
    likes: 0,
  };

  const newCard = await supabase
    .from(TABLES.CARDS)
    .insert(card)
    .select()
    .single();

  if (newCard.error) {
    console.warn("Could not record query");
    console.warn(newCard.error);
    return NextResponse.error();
  } else {
    // successfully inserted card
  }

  return NextResponse.json({
    card: newCard.data,
  });
}
