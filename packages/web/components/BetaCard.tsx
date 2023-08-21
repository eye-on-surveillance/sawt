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
  // Temporarirly show that url copied to clipboard
  const [recentlyCopied, setRecentlyCopied] = useState(false);

  return (
    <div>
      <div className="mb-4 space-y-2">
        <h1 className="text-2xl">{card.title}</h1>
        <h1 className="text-sm">{moment(card.created_at!).fromNow()}</h1>
        {recentlyCopied ? (
          <span className=" text-green-400">
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

      {responses!.map((response, index) => (
        <CardResponse response={response} key={index} />
      ))}
      <div className="text-sm">
        {citations!.map((citation, index) => (
          <Citation citation={citation} index={index} key={index} />
        ))}
      </div>
    </div>
  );
};

export default BetaCard;
