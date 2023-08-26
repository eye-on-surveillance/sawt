"use client";

import { ICard } from "@/lib/api";
import { CARD_SHOW_PATH, getPageURL } from "@/lib/paths";
import { supabase } from "@/lib/supabase/supabaseClient";
import {
  faCheck,
  faComment,
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

type SupabaseRealtimePayload<T = any> = {
  old: T;
  new: T;
};

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
  // The last message will remain until processing finishes
  "Finishing up...",
];

const WAIT_MS = 2500;
const POLL_INTERVAL = 10000;

interface BiasModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { selected: string[]; feedback: string }) => void;
}

function BiasModal({ isOpen, onClose, onSubmit }: BiasModalProps) {
  const [selectedBiases, setSelectedBiases] = useState<Record<string, boolean>>(
    {}
  );
  const [feedback, setFeedback] = useState("");

  const handleCheckboxChange = (bias: string) => {
    setSelectedBiases((prevBiases) => ({
      ...prevBiases,
      [bias]: !prevBiases[bias],
    }));
  };

  const handleSubmit = () => {
    const selected = Object.keys(selectedBiases).filter(
      (key) => selectedBiases[key]
    );
    onSubmit({ selected, feedback });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed left-0 top-0 flex h-full w-full items-center justify-center bg-gray-500 bg-opacity-50">
      <div className="relative w-1/2 rounded bg-white p-4 shadow-lg">
        <button onClick={onClose} className="absolute right-2 top-2">
          <FontAwesomeIcon icon={faTimes} />
        </button>
        <h2 className="mb-4 text-lg font-bold">Report Response</h2>
        <p className="mb-4 text-sm">
          At times, SAWT might not provide perfectly accurate information. Your
          reports on any inaccuracies are invaluable in refining our system.
        </p>

        <div className="mb-4">
          {[
            "Gender-Related Bias",
            "Cultural or Ethnic Bias",
            "Racial Bias",
            "Misleading Information or Inaccuracies",
            "Uninformative Response",
            "Factually Inaccurate",
          ].map((bias) => (
            <div key={bias}>
              <input
                type="checkbox"
                id={bias}
                checked={!!selectedBiases[bias]}
                onChange={() => handleCheckboxChange(bias)}
              />
              <label htmlFor={bias} className="ml-2">
                {bias}
              </label>
            </div>
          ))}
        </div>

        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Submit a comment"
          className="mb-4 w-full"
        ></textarea>
        <button
          onClick={handleSubmit}
          className="rounded bg-blue-500 px-4 py-2 text-white"
        >
          Submit
        </button>
      </div>
    </div>
  );
}

export default function QueryResult({ card }: { card: ICard }) {
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
  const [likes, setLikes] = useState<number>(card.likes || 0);
  const [isBiasModalOpen, setBiasModalOpen] = useState(false);

  const handleBiasReport = () => {
    setBiasModalOpen(true);
  };

  useEffect(() => {
    const channel = (supabase.channel(`cards:id=eq.${card.id}`) as any)
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
        },
        (payload: SupabaseRealtimePayload<ICard>) => {
          console.log("Update:", payload);
          if (
            payload.new.id === card.id &&
            payload.new.likes !== payload.old.likes
          ) {
            // If the likes field has changed, then update the likes
            setLikes(payload.new.likes);
          }
        }
      )
      .subscribe();

    // Cleanup subscription on component unmount
    return (): void => {
      channel.unsubscribe();
    };
  }, [card.id]);

  const submitBiasFeedback = async ({
    selected,
    feedback,
  }: {
    selected: string[];
    feedback: string;
  }) => {
    try {
      const { data, error } = await supabase
        .from("cards")
        .update({ bias: { type: selected, feedback: feedback } })
        .eq("id", card.id);
      if (error) {
        throw error;
      }
      console.log("Bias feedback submitted:", data);
    } catch (error) {
      console.error("Error submitting bias feedback:", error);
    }
  };

  useInterval(
    () => {
      setMsgIndex((prevIndex) => (prevIndex + 1) % LOADING_MESSAGES.length);
    },
    isLoading ? WAIT_MS : null
  );

  useInterval(() => {
    setPrettyCreatedAt(moment(card.created_at).fromNow());
  }, 5_000);

  useInterval(
    () => {
      setRecentlyCopied(false);
    },
    recentlyCopied ? 3000 : null
  );

  const handleLikeUpdate = async () => {
    try {
      const newLikesValue = likes + 1;

      const { data, error } = await supabase
        .from("cards")
        .update({ likes: newLikesValue })
        .eq("id", card.id);

      if (error) {
        throw error;
      }
      console.log("Likes updated:", data);

      // Update the local likes state
      setLikes(newLikesValue);
    } catch (error) {
      console.error("Error occurred in handleLikeUpdate:", error);
      setLikes(likes - 1); // Revert the likes count on error
    }
  };

  const handleCardLike = () => {
    console.log("Like button clicked in QueryResult!");
    setLikes((prevLikes) => prevLikes + 1); // Optimistically update UI
    handleLikeUpdate(); // Perform the actual update operation
  };

  return (
    <div
      className={`my-6 rounded-lg bg-blue-200 p-6 ${
        isLoading ? "border-4 border-dashed border-yellow-500" : ""
      }`}
    >
      <Link href={`${CARD_SHOW_PATH}/${card.id}`}>
        <div>
          <h4 className="text-xl font-bold">{card.title}</h4>
          <h6 className="text-xs">
            <span className="text-amber-700">
              {card.is_mine ? "You | " : null}
            </span>
            {prettyCreatedAt}
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

      <div className="flex items-center justify-start text-sm">
        <span className="ml-3 cursor-pointer" onClick={handleCardLike}>
          <FontAwesomeIcon
            icon={faThumbsUp}
            className="mx-2 h-5 w-5 align-middle"
          />
          {likes}
        </span>

        <Link href={`${CARD_SHOW_PATH}/${card.id}`}>
          <span className="ml-3 cursor-pointer">
            <FontAwesomeIcon
              icon={faComment}
              className="mx-2 h-5 w-5 align-middle"
            />
            Comments
          </span>
        </Link>

        {recentlyCopied ? (
          <span className="ml-3 text-green-400">
            <FontAwesomeIcon
              icon={faCheck}
              className="mx-2 h-5 w-5 align-middle"
            />
            Copied
          </span>
        ) : (
          <span
            className="ml-3 cursor-pointer"
            onClick={() => {
              copy(currentUrl);
              setRecentlyCopied(true);
            }}
          >
            <FontAwesomeIcon
              icon={faShare}
              className="mx-2 h-5 w-5 align-middle"
            />
            Share
          </span>
        )}

        <span className="ml-3 cursor-pointer" onClick={handleBiasReport}>
          Report Response
        </span>
      </div>

      <BiasModal
        isOpen={isBiasModalOpen}
        onClose={() => setBiasModalOpen(false)}
        onSubmit={submitBiasFeedback}
      />
    </div>
  );
}
