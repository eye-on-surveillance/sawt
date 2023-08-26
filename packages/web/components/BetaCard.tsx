"use client";

import { ICard, ICitation, IResponse } from "@/lib/api";
import { CARD_SHOW_PATH, getPageURL } from "@/lib/paths";
import { supabase } from "@/lib/supabase/supabaseClient";
import { faCheck, faShare } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import { useEffect, useState } from "react";
import useClipboardApi from "use-clipboard-api";
import CardResponse from "./CardResponse";
import Citation from "./Citation";

type SupabaseRealtimePayload<T = any> = {
  old: T;
  new: T;
  eventType: "INSERT" | "UPDATE" | "DELETE";
  schema: string;
  table: string;
  commit_timestamp: string;
  display_name: string;
};

type Comment = {
  display_name: string;
  content: string;
  created_at: Date;
  // ... any other fields that a comment might have
};


const BetaCard = ({ card }: { card: ICard }) => {
  const responses: IResponse[] = card.responses ?? [];
  const citations: ICitation[] = card.citations ?? [];
  const [value, copy] = useClipboardApi();
  const currentUrl = getPageURL(`${CARD_SHOW_PATH}/${card.id}`);
  const [recentlyCopied, setRecentlyCopied] = useState(false);
  const [comments, setComments] = useState<Comment[] | null>(null);
  const [commentContent, setCommentContent] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [showCitations, setShowCitations] = useState(false);

  useEffect(() => {
    const fetchComments = async () => {
      try {
        const { data, error } = await supabase
          .from("comments")
          .select("*")
          .eq("card_id", card.id)
          .order("created_at", { ascending: false });
        if (error) throw error;
        setComments(data);
      } catch (error) {
        console.error("Error fetching comments:", error);
      }
    };
    fetchComments();
  }, [card.id]);

  useEffect(() => {
    const channel = supabase
      .channel(`comments:card_id=eq.${card.id}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public"
        },
        (payload: SupabaseRealtimePayload<{
          content: string;
          display_name: string;
          card_id: number;
        }>) => {
          console.log("Update:", payload);
          if (payload.new.card_id === card.id) {
            setComments((prevComments) => [payload.new, ...prevComments]);
          }
        }
      )
      .subscribe();
  
    return () => {
      try {
        channel.unsubscribe();
      } catch (error) {
        console.error("Error unsubscribing from channel:", error);
      }
    };
  }, [card.id]);

  const handleCommentSubmit = async () => {
    const newComment = {
      card_id: card.id,
      content: commentContent,
      display_name: displayName,
    };

    try {
      const { data, error } = await supabase
        .from("comments")
        .insert([newComment]);
      if (error) throw error;
      setDisplayName(""); // Resetting display name after successful post
      setCommentContent(""); // Resetting comment content after successful post
    } catch (error) {
      console.error("Error adding comment:", error);
      // If there's an error, revert the change to the comments
      setComments((prevComments) =>
        prevComments.filter((comment) => comment !== newComment)
      );
    }
  };

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
          className="mb-2 rounded bg-blue-500 px-4 py-2 text-white"
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

      {/* Comments Section */}
      <div className="mt-6">
        <h2 className="mb-4 text-xl font-bold">Comments</h2>

        <div className="mb-2">
          <input
            className="w-full rounded border p-2"
            placeholder="Your Display Name..."
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <textarea
            className="w-full rounded border p-2"
            placeholder="Write a comment..."
            value={commentContent}
            onChange={(e) => setCommentContent(e.target.value)}
          />
        </div>

        <button
          className="rounded bg-blue-500 px-4 py-2 text-white"
          onClick={handleCommentSubmit}
        >
          Post Comment
        </button>

        {comments && comments.map((comment, index) => (
          <div
            key={index}
            className={`mb-2 mt-4 p-2 ${
              index < comments.length - 1 ? "border-b-2" : ""
            } border-black`}
          >
            <div className="flex justify-between">
              <p className="font-bold">{comment.display_name}</p>
              <span className="text-sm text-gray-500">
                {moment(comment.created_at).fromNow()}
              </span>
            </div>
            <div>
              {comment.content.split("\n").map((str, idx) =>
                idx === comment.content.split("\n").length - 1 ? (
                  str
                ) : (
                  <>
                    {str}
                    <br />
                  </>
                )
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BetaCard;