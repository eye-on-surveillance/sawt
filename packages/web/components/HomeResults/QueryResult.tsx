import { ICard } from "@/lib/api";
import { CARD_SHOW_PATH } from "@/lib/paths";
import { supabase } from "@/lib/supabase/supabaseClient";
import { getThumbnail, getYouTubeEmbedUrl, isYouTubeURL } from "@/lib/utils";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import Link from "next/link";
import { useEffect, useState } from "react";
import CardActions from "../Card/CardActions";
import styles from "./homeresults.module.scss";

const MAX_CHARACTERS_PREVIEW = 20000;

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

export default function QueryResult({ card }: { card: ICard }) {
  const { created_at: createdAt, citations } = card;
  const [msgIndex, setMsgIndex] = useState(0);
  const initialLoadingState = !card.responses || card.responses.length === 0;
  const [isLoading, setIsLoading] = useState(initialLoadingState);
  const [responses, setResponses] = useState(card.responses || []);

  const prettyCreatedAt =
    !!createdAt && new Date(createdAt) < new Date()
      ? moment(createdAt).fromNow()
      : moment().fromNow();
  const thumbnail = getThumbnail(citations || []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;

    if (isLoading) {
      intervalId = setInterval(() => {
        setMsgIndex((prevIndex) => (prevIndex + 1) % LOADING_MESSAGES.length);
      }, 2500);
    }

    const channel = supabase
      .channel(`cards:id=eq.${card.id}`)
      .on(
        "postgres_changes",
        { event: "UPDATE", schema: "public" },
        (payload) => {
          if (payload.new.id === card.id && payload.new.responses) {
            const newResponses = payload.new.responses;
            if (JSON.stringify(newResponses) !== JSON.stringify(responses)) {
              setResponses(newResponses);
              setIsLoading(false);
            }
          }
        }
      )
      .subscribe();

    return () => {
      if (intervalId) clearInterval(intervalId);
      channel.unsubscribe();
    };
  }, [card.id, isLoading, responses]);

  const combinedResponses = responses.map((r) => r.response).join(" ");
  const previewText =
    combinedResponses.split(" ").slice(0, 100).join(" ") + "...";

  const CardBody = () => (
    <Link href={`${CARD_SHOW_PATH}/${card.id}`}>
      <div>
        <h4 className="text-xl font-bold">{card.title}</h4>
        <h6 className="text-xs">
          <span className="text-purple">{card.is_mine ? "You | " : ""}</span>
          <span className="text-black">{prettyCreatedAt}</span>
        </h6>
        {!isLoading ? (
          <>
            <div className="my-5 overflow-hidden" style={{ height: "4.5em" }}>
              <p>{previewText}</p>
            </div>
            {isYouTubeURL(thumbnail?.source_url) && (
              <iframe
                id="ytplayer"
                src={getYouTubeEmbedUrl(
                  thumbnail?.source_url,
                  thumbnail?.source_timestamp
                )}
                frameBorder="0"
                className="h-64 w-full lg:h-96"
              ></iframe>
            )}
          </>
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
  );

  return (
    <div id={isLoading ? "loading" : "loaded"} className={styles.card}>
      <div
        className={`my-6 space-y-4 rounded-lg bg-blue p-6 text-primary ${
          isLoading ? "border-4 border-dashed border-yellow-500" : ""
        }`}
      >
        <CardBody />
        <CardActions card={card} />
      </div>
    </div>
  );
}
