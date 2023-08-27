"use client";

import { ICard, ICitation, IResponse } from "@/lib/api";
import { CARD_SHOW_PATH, getPageURL } from "@/lib/paths";
import { faCheck, faShare } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import { useState } from "react";
import useClipboardApi from "use-clipboard-api";
import CardResponse from "./CardResponse";
import Citation from "./Citation";

const BetaCard = ({ card }: { card: ICard }) => {
  const responses: IResponse[] = card.responses ?? [];
  const citations: ICitation[] = card.citations ?? [];
  const [value, copy] = useClipboardApi();
  const currentUrl = getPageURL(`${CARD_SHOW_PATH}/${card.id}`);
  const [recentlyCopied, setRecentlyCopied] = useState(false);
  const [showCitations, setShowCitations] = useState(false);

  return (
    <div className="w-full">
      {/* Card Header */}
      <div className="mb-4 space-y-2">
        <h1 className="text-2xl">{card.title}</h1>
        <h1 className="text-sm">{moment(card.created_at!).fromNow()}</h1>
        {recentlyCopied ? (
          <span className="text-green-400">
            <FontAwesomeIcon
              icon={faCheck}
              className="mr-2 h-5 w-5 align-middle"
            />
            Copied
          </span>
        ) : (
          <span
            className="cursor-pointer"
            onClick={() => {
              copy(currentUrl);
              setRecentlyCopied(true);
            }}
          >
            <FontAwesomeIcon
              icon={faShare}
              className="mr-2 h-5 w-5 align-middle"
            />
            Share
          </span>
        )}
      </div>

      {/* Card Responses */}
      {responses.map((response, index) => (
        <CardResponse response={response} key={index} />
      ))}

      {/* Citations Section */}
      <div className="mb-6 mt-4">
        <button
          className="mb-2 rounded px-4 py-2 text-black"
          onClick={() => setShowCitations((prev) => !prev)}
        >
          {showCitations ? "Hide Citations" : "Show Citations"}
        </button>

        {showCitations && (
          <div className="mt-2 text-sm">
            {citations.map((citation, index) => (
              <Citation citation={citation} index={index} key={index} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BetaCard;
