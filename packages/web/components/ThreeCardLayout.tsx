"use client";

import { ICard } from "@/lib/api";
import { CARD_SHOW_PATH, getPageURL } from "@/lib/paths";
import { supabase } from "@/lib/supabase/supabaseClient";
import {
  faSpinner,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import Link from "next/link";
import { useState } from "react";
import useClipboardApi from "use-clipboard-api";
import { v4 as uuidv4 } from "uuid"; //will need
import CommentBox from "./CommentBoxes";

import Rubric from '@/components/Rubric';

const criteria = [
  { id: 'criterion1', description: 'Criterion 1 Description' },
  { id: 'criterion2', description: 'Criterion 2 Description' },
  // Add more criteria as needed
];



const MAX_CHARACTERS_PREVIEW = 300;

const LOADING_MESSAGES = [
  "Processing your request...",
  "About 30 seconds remaining...",
  "Processing your request...",
  "About 25 seconds remaining...",
  "About 25 seconds remaining...",
  "Processing your request...",
  "About 20 seconds remaining...",
  "About 20 seconds remaining...",
  "Processing your request...",
  "Processing your request...",
  "About 15 seconds remaining...",
  "About 15 seconds remaining...",
  "Processing your request...",
  "About 10 seconds remaining...",
  "About 10 seconds remaining...",
  "Hang tight...",
  "Hang tight...",
  "Hang tight...",
  "About 5 seconds remaining...",
  "About 5 seconds remaining...",
  "Finishing up...",
];

const WAIT_MS = 2500;
const POLL_INTERVAL = 10000;

type SupabaseRealtimePayload<T = any> = {
  old: T;
  new: T;
};


// IDEA: Use similar system to the likes to format the choice

function hasLikedCardBefore(cardId?: string): boolean {
  if (!cardId || typeof window === "undefined") {
    return false;
  }
  const likedCards = JSON.parse(localStorage.getItem("likedCards") || "[]");
  return likedCards.includes(cardId);
}

function markCardAsLiked(cardId: string) {
  const likedCards = JSON.parse(localStorage.getItem("likedCards") || "[]");
  likedCards.push(cardId);
  localStorage.setItem("likedCards", JSON.stringify(likedCards));
}


export default function ThreeCardLayout({ cards }: { cards: ICard }) {

  const [msgIndex, setMsgIndex] = useState<number>(0);
  const isLoading = !cards.responses || cards.responses.length <= 0;
  const [value, copy] = useClipboardApi();
  const currentUrl = getPageURL(`${CARD_SHOW_PATH}/${cards.id}`);
  const [recentlyCopied, setRecentlyCopied] = useState(false);
  const [prettyCreatedAt, setPrettyCreatedAt] = useState(
    !!cards.created_at && new Date(cards.created_at) < new Date()
      ? moment(cards.created_at).fromNow()
      : moment().fromNow()
  );

  //Function that sends comments to supabase under respective card.comment
  const submitCommentFeedback = async ({
    comment,
    card
  }: {
    comment: string;
    card: ICard;
  }) => {
    try {
      
      /* This commented out code is for if we want to add the ability to update previous comments.
      */
      // let { data: cards, error: fetchError } = await supabase
      //   .from("cards")
      //   .select("comment")
      //   .eq("id", card.id)
      //   .single();

      // if (fetchError) {
      //   throw fetchError;
      // }

      // const newFeedbackId = uuidv4();

      // const newComment = { id: newFeedbackId, type: comment };

      // const existingComment = 
      //   existingCard.comment && Array.isArray(existingCard.comment)
      //     ? existingCard.comment
      //     : [];
      // const updatedComment = [...existingComment, newComment];

      const { data, error } = await supabase
        .from("cards")
        .update([{ comment: comment }])
        .eq("id", card.id)
        .select()

      if (error) {
        throw error;
      }
    } catch (error) {}
  };


  return (
    <div className="flex justify-center mt-10 space-x-4-x">
      {cards && cards.map((card, index) => (
        <div key={index} className={`my-6 rounded-lg bg-blue p-6 text-primary 
        ${isLoading ? "border-4 border-dashed border-yellow-500" : ""
          }`}>
          <Link href={`${CARD_SHOW_PATH}/${card.id}`}>
            <div>
              <h4 className="text-xl font-bold">{card.title}</h4>
              <h6 className="text-xs">
                <span className="text-purple">
                  {card.is_mine ? "You | " : null}
                </span>
                <span className="text-secondary">{prettyCreatedAt}</span>
              </h6>

              {!isLoading && !!card.responses ? (
                <p className="my-5">
                  {card.responses[0].response.substring(0, MAX_CHARACTERS_PREVIEW)}
                  {card.responses[0].response.length > MAX_CHARACTERS_PREVIEW
                    ? "..."
                    : null}
                </p>
              ) : (
                <p className="my-5">
                  <FontAwesomeIcon
                    icon={faSpinner}
                    className="mx-2 h-5 w-5 animate-spin align-middle duration-300"
                  />
                  {LOADING_MESSAGES[msgIndex]}
                </p>
              )}
            </div>
          </Link>
      <CommentBox
        card = {card}
        onSubmit={submitCommentFeedback}
      />

          <hr></hr>
          <label className="flex justify-center mt-10 space-x-1-x">Rubric</label>
          <Rubric criteria={criteria}/>

        </div>
      ))
      }

    </div>
  );
}