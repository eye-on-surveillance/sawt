import { ECardStatus, ICard } from "@/lib/api"; // Importing types and interfaces
import { TABLES } from "@/lib/supabase/db"; // Importing table definitions
import { createClient } from "@supabase/supabase-js"; // Supabase client for interacting with the database
import { cookies } from "next/headers"; // Cookie handling
import { NextResponse } from "next/server"; // Next.js server-side response object

export const dynamic = "force-dynamic"; // Forces the handler to be dynamic


/* Create card
 * Not creating directly from client because:
 *  - We have RLS enabled that only allows to view cards in 'public' status
 *  - All cards start off in 'new' status
 *  - This leads to users being able to create cards, but unable to retrieve their IDs directly
 *  - Easier to protect vars such as 'likes' with default valuse
 */


const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "PLACEHOLDER";
const supabaseSecretServiceKey =
  process.env.SUPABASE_SERVICE_ROLE_SECRET || "PLACEHOLDER";

// POST handler for creating a new card
export async function POST(request: Request) {
  const cookieStore = cookies(); // Handle cookies, possibly for authentication
  const { title, card_type } = (await request.json()) as ICard; // Extract card details from the request's JSON body

  // Create a new Supabase client instance
  const supabase = createClient(supabaseUrl, supabaseSecretServiceKey);

  // Define a new card object with initial values
  const card = {
    title,
    card_type,
    status: ECardStatus.NEW, // Set the card status to NEW
    likes: 0, // Initialize likes to 0
  };
  const newCard = await supabase
    .from(TABLES.CARDS) // Target the 'cards' table
    .insert(card) // Insert the new card
    .select() // Select the inserted data
    .single(); // Expect a single result



  // Handle any error that occurs during the insert operation
  if (newCard.error) {
    console.warn("Could not record query");
    console.warn(newCard.error);
    return NextResponse.error(); // Return an error response
  } else {
    // If insertion is successful, additional processing could be done here
  }

  // Return the newly inserted card data in the JSON response
  return NextResponse.json({
    card: newCard.data,
  });
}
