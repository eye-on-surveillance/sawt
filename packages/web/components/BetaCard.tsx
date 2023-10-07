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
};

type Comment = {
  display_name: string;
  content: string;
  created_at: Date;
  card_id: string;
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
  const [showComments, setShowComments] = useState(false);

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
      } catch (error) {}
    };
    fetchComments();
  }, [card.id]);

  useEffect(() => {
    const channel = (supabase.channel(`cards:id=eq.${card.id}`) as any)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
        },
        (payload: SupabaseRealtimePayload<Comment>) => {
          if (payload.new.card_id === card.id) {
            setComments((prevComments) => [
              payload.new,
              ...(prevComments || []),
            ]);
          }
        }
      )
      .subscribe();

    // Cleanup subscription on component unmount
    return () => {
      channel.unsubscribe();
    };
  }, [card.id]);

  const handleCommentSubmit = async () => {
    const newComment = {
      card_id: card.id,
      content: commentContent,
      display_name: displayName,
      created_at: new Date(),
    };


    setComments((prevComments) =>
      prevComments
        ? prevComments.filter((comment) => comment !== newComment)
        : null
    );

    setDisplayName(""); // Resetting display name
    setCommentContent(""); // Resetting comment content

    try {
      const { data, error } = await supabase
        .from("comments")
        .insert([newComment]);
      if (error) throw error;
      setDisplayName(""); // Resetting display name after successful post
      setCommentContent(""); // Resetting comment content after successful post
    } catch (error) {
      // If there's an error, revert the change to the comments
      setComments((prevComments) =>
        prevComments
          ? prevComments.filter((comment) => comment !== newComment)
          : null
      );
    }
  };


  return (
    <div className="w-full">
      {/* Card Header */}
      <div className="mb-4 space-y-2">
        <h1 className="text-2xl">{card.title}</h1>
        <h1 className="text-sm">{moment.utc(card.created_at!).local().fromNow()}</h1>
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
          className="text-black mb-2 rounded px-4 py-2"
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
        <button
          className="text-black mb-2 rounded px-4 py-2"
          onClick={() => setShowComments((prev) => !prev)}
        >
          {showComments ? "Hide Comments" : "Show Comments"}
        </button>

        {showComments && (
          <>
            <h2 className="mb-4 text-xl font-bold"></h2>

            <div className="mb-2">
              <input
                className="w-full rounded border p-2"
                placeholder="Please write your name/organization/community affiliation"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>
            

            <div className="mb-4">
              <textarea
                  style={{ height: '125px' }}
                  className="w-full rounded border p-2"
                  placeholder="Please write your comments here. If relevant, please include citations to news articles, social media posts, and/or other sources of information that serve to support your feedback, as this will help us improve Sawt."
                  value={commentContent}
                  onChange={(e) => setCommentContent(e.target.value)}
              />
          </div>

            <button
              className="text-black mb-2 rounded px-4 py-2"
              onClick={handleCommentSubmit}
            >
              Post Comment
            </button>

            {comments &&
              comments.map((comment, index) => (
                <div
                  key={index}
                  className={`mb-2 mt-4 p-2 ${
                    index < comments.length - 1 ? "border-b-2" : ""
                  } border-black`}
                >
                  <div className="flex justify-between">
                    <p className="font-bold">{comment.display_name}</p>
                    <span className="text-sm text-gray-500">
                      {moment.utc(comment.created_at).local().fromNow()}
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
          </>
        )}
      </div>
    </div>
);
};

export default BetaCard;
