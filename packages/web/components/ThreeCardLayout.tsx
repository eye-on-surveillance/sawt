"use client";

import { ICard } from "@/lib/api";
import { CARD_SHOW_PATH, getPageURL } from "@/lib/paths";
import { supabase } from "@/lib/supabase/supabaseClient";
import {
  faCheck,
  faShare,
  faSpinner,
  faThumbsUp,
  faTimes,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import Link from "next/link";
import { useEffect, useState } from "react";
import useClipboardApi from "use-clipboard-api";
import { useInterval } from "usehooks-ts";
import { v4 as uuidv4 } from "uuid";

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

export default function ThreeCardLayout({ card }: { card: ICard }) {

  const [msgIndex, setMsgIndex] = useState<number>(0);
  const isLoading = !card.responses || card.responses.length <= 0;
  const [value, copy] = useClipboardApi();
  const currentUrl = getPageURL(`${CARD_SHOW_PATH}/${card.id}`);
  const [recentlyCopied, setRecentlyCopied] = useState(false);
  const [prettyCreatedAt, setPrettyCreatedAt] = useState(
    !!card.created_at && new Date(card.created_at) < new Date()
      ? moment(card.created_at).fromNow()
      : moment().fromNow()
  );


  return (
    <div className="flex justify-center mt-10 space-x-4-x">
      {card && card.map((card, index) => (
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

        </div>
      ))
      }
    </div>
  );
}