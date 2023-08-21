"use client";

import { ICard } from "@/lib/api";
import { CARD_SHOW_PATH } from "@/lib/paths";
import {
  faShare,
  faSpinner,
  faThumbsUp,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";
import { useState } from "react";
import { useInterval } from "usehooks-ts";

const MAX_CHARACTERS_PREVIEW = 200;

type QueryResultParams = {
  card: ICard;
};

const LOADING_MESSAGES = [
  "Processing your request...",
  "About 30 seconds remaining...",
  "Processing your request...",
  "About 25 seconds remaining...",
  "Processing your request...",
  "About 20 seconds remaining...",
  "Processing your request...",
  "Processing your request...",
  "About 15 seconds remaining...",
  "Processing your request...",
  "About 10 seconds remaining...",
  "Hang tight...",
  "Hang tight...",
  "Hang tight...",
  "About 5 seconds remaining...",
  "About 5 seconds remaining...",
  "Finishing up...",
];

const WAIT_MS = 2500;

export default function QueryResult(queryResultParams: QueryResultParams) {
  const [msgIndex, setMsgIndex] = useState<number>(0);
  const { card } = queryResultParams;
  const isLoading = !card.responses || card.responses.length <= 0;

  useInterval(
    () => {
      if (msgIndex + 1 >= LOADING_MESSAGES.length) return;
      const plusOne = msgIndex + 1;
      setMsgIndex(plusOne);
    },

    // If waiting on answer to query and have more wait messages
    isLoading && msgIndex < LOADING_MESSAGES.length ? WAIT_MS : null
  );

  return (
    <Link href={`${CARD_SHOW_PATH}/${card.id}`}>
      <div
        className={`my-6 rounded-lg bg-blue-200 p-6 ${
          isLoading ? "border-4 border-dashed border-yellow-500" : null
        }`}
      >
        <h4 className="text-xl font-bold">{card.title}</h4>
        <h6 className="text-xs">
          <span className="text-amber-700">
            {card.is_mine ? "You | " : null}
          </span>
          {card.created_at!.toString()}
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

        <div className="text-sm">
          <span>
            <FontAwesomeIcon
              icon={faThumbsUp}
              className="mx-2 h-5 w-5 align-middle"
            />
            {card.likes}
          </span>

          <span className="ml-3">
            <FontAwesomeIcon
              icon={faShare}
              className="mx-2 h-5 w-5 align-middle"
            />
            Share
          </span>
        </div>
      </div>
    </Link>
  );
}
