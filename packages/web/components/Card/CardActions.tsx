"use client";

import { ICard } from "@/lib/api";
import { CARD_SHOW_PATH, getPageURL } from "@/lib/paths";
import { supabase } from "@/lib/supabase/supabaseClient";
import {
  faBook,
  faCheck,
  faFlag,
  faShare,
  faThumbsUp,
  faTimes,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useState } from "react";
import useClipboardApi from "use-clipboard-api";
import { useInterval } from "usehooks-ts";
import { v4 as uuidv4 } from "uuid";
import styles from "./card.module.scss"

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

interface BiasModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { selected: string[]; comment: string }) => void;
}

function BiasModal({ isOpen, onClose, onSubmit }: BiasModalProps) {
  const [selectedBiases, setSelectedBiases] = useState<Record<string, boolean>>(
    {}
  );
  const [comment, setComment] = useState<string>("");

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
    onSubmit({ selected, comment });
    onClose();

    setSelectedBiases({});
    setComment("");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed left-0 top-0 flex h-full w-full items-center justify-center bg-gray-500 bg-opacity-50">
      <div className="relative w-1/2 rounded bg-blue p-4 shadow-lg">
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
          <label htmlFor="comment" className="mb-2 mt-4 block">
            Comments:
          </label>
          <textarea
            id="comment"
            className="h-20 w-full rounded border p-2"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add additional feedback here"
          ></textarea>
        </div>
        <button
          onClick={handleSubmit}
          className="bg-blue-500 rounded bg-secondary px-4 py-2 text-white"
        >
          Submit
        </button>
      </div>
    </div>
  );
}

type SupabaseRealtimePayload<T = any> = {
  old: T;
  new: T;
};

const CardActions = ({ card }: { card: ICard }) => {
  const { citations, id: cardId } = card;
  const [likes, setLikes] = useState<number>(card.likes || 0);
  const [recentlyCopied, setRecentlyCopied] = useState(false);

  const [isBiasModalOpen, setBiasModalOpen] = useState(false);
  const [value, copy] = useClipboardApi();
  const currentUrl = getPageURL(`${CARD_SHOW_PATH}/${cardId}`);
  const handleBiasReport = () => {
    setBiasModalOpen(true);
  };

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
      setLikes(newLikesValue);
    } catch (error) {
      setLikes(likes - 1);
    }
  };

  const handleCardLike = () => {
    if (card.id) {
      if (!hasLikedCardBefore(card.id)) {
        setLikes((prevLikes) => prevLikes + 1);
        handleLikeUpdate();
        markCardAsLiked(card.id);
      } else {
        console.warn("You've already liked this card!");
      }
    }
  };

  const submitBiasFeedback = async ({
    selected,
    comment,
  }: {
    selected: string[];
    comment: string;
  }) => {
    try {
      const { data: existingCard, error: fetchError } = await supabase
        .from("cards")
        .select("bias")
        .eq("id", card.id)
        .single();

      if (fetchError) {
        throw fetchError;
      }

      const newFeedbackId = uuidv4();

      const newBias = { id: newFeedbackId, type: selected, comment };

      const existingBiases =
        existingCard.bias && Array.isArray(existingCard.bias)
          ? existingCard.bias
          : [];
      const updatedBiases = [...existingBiases, newBias];

      const { data, error } = await supabase
        .from("cards")
        .update({ bias: updatedBiases })
        .eq("id", card.id);

      if (error) {
        throw error;
      }
    } catch (error) {}
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
          if (
            payload.new.id === card.id &&
            payload.new.likes !== payload.old.likes
          ) {
            setLikes(payload.new.likes || 0);
          }
        }
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [card.id]);

  useInterval(
    () => {
      setRecentlyCopied(false);
    },
    recentlyCopied ? 3000 : null
  );

  return (
    <div className={styles["icons"]}>
      <div className="flex flex-wrap items-center justify-start space-x-1 text-sm text-secondary md:space-x-3">
        <div className="my-2">
          <span
            className={
              hasLikedCardBefore(card.id)
                ? "cursor-not-allowed"
                : "cursor-pointer"
            }
            onClick={handleCardLike}
          >
            <FontAwesomeIcon
              icon={faThumbsUp}
              className={`mx-2 h-5 w-5 align-middle ${
                hasLikedCardBefore(card.id) ? "text-primary" : ""
              }`}
            />
            {likes}
          </span>
        </div>

        <div className="my-2">
          {recentlyCopied ? (
            <span className="text-primary">
              <FontAwesomeIcon
                icon={faCheck}
                className="mx-2 h-5 w-5 align-middle"
              />
              Link copied
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
                className="mx-2 h-5 w-5 align-middle"
              />
              Share
            </span>
          )}
        </div>

        <span className="my-2">
          <FontAwesomeIcon
            icon={faBook}
            className="mx-2 h-5 w-5 align-middle"
          />
          {citations?.length}
        </span>

        <span className="my-2 cursor-pointer" onClick={handleBiasReport}>
          <FontAwesomeIcon
            icon={faFlag}
            className="mx-2 h-5 w-5 align-middle"
          />
          Report
        </span>
      </div>
      <BiasModal
        isOpen={isBiasModalOpen}
        onClose={() => setBiasModalOpen(false)}
        onSubmit={submitBiasFeedback}
      />
    </div>
  );
};

export default CardActions;
