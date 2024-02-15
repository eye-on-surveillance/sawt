// Ensure the client is executed only on the server-side for security
"use client";

import { TABLES } from "@/lib/supabase/db"; // Importing table definitions
import { createClient } from "@supabase/supabase-js"; // Supabase client for interacting with the database
import { NextResponse } from "next/server"; // Next.js server-side response object

// Environment variables for Supabase URL and secret service key
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "PLACEHOLDER";
const supabaseSecretServiceKey =
  process.env.SUPABASE_SERVICE_ROLE_SECRET || "PLACEHOLDER";

export const dynamic = "force-dynamic"; // Forces the handler to be dynamic

export async function POST(request: Request) {
  // Check if the Supabase environment variables are set
  if (!supabaseUrl || !supabaseSecretServiceKey) {
    console.error("Supabase environment variables not set!");
    return NextResponse.error();
  }

  // Create a new Supabase client instance
  const supabase = createClient(supabaseUrl, supabaseSecretServiceKey);

  // Extract the cardId from the request's JSON body
  const { cardId } = (await request.json()) as { cardId: string };

  // Check if the card exists in the database
  const { data: cardData, error: fetchError } = await supabase
    .from(TABLES.CARDS)
    .select("id")
    .eq("id", cardId)
    .single();

  // If there's an error fetching the card or if the card is not found, return an error
  if (fetchError || !cardData) {
    console.error("Error fetching card or card not found:", fetchError);
    return NextResponse.error();
  }

  // Fetch the current likes value for the card
  const { data: currentLikeData, error: likeError } = await supabase
    .from(TABLES.CARDS)
    .select("likes")
    .eq("id", cardId)
    .single();

  // If there's an error fetching the likes value or if it's not found, return an error
  if (likeError || !currentLikeData) {
    console.error("Error fetching current likes value:", likeError);
    return NextResponse.error();
  }

  // Increment the likes value by 1
  const newLikesValue = currentLikeData.likes + 1;

  // Update the card's likes in the database with the new value
  const { data, error } = await supabase
    .from(TABLES.CARDS)
    .upsert({ id: cardId, likes: newLikesValue });

  // If there's an error updating the likes, return an error
  if (error) {
    console.error("Error while updating likes:", error);
    return NextResponse.error();
  }

  // If successful, return the updated likes data
  return NextResponse.json({ message: "Likes updated successfully.", data });
}
