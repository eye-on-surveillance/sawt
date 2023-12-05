
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
  { id: 'Accuracy', description: 'Accuracy' },
  { id: 'Helpfulness', description: 'Helpfulness' },
  { id: 'Balance', description: 'Balance' }
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

export default function ThreeCardLayout({ cards, userName }: { cards: ICard, userName: string }) {
 
  // ... other imports ...
  

     
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


  const [scores, setScores] = useState<Record<string, number>>({});

  // Function to update scores
  const handleScoreChange = (criterionId: string, score: number) => {
      setScores(prevScores => ({ ...prevScores, [criterionId]: score }));
  };

  // Function to reset scores
  const resetScores = () => {
      // Reset logic - assuming each score should reset to 1
      const resettedScores = Object.keys(scores).reduce((acc, criterionId) => {
          acc[criterionId] = 1;
          return acc;
      }, {});
      setScores(resettedScores);
  };

  //Function that sends comments to supabase under respective card.comment
  const submitCommentFeedback = async ({
    scores,
    comment,
    card
  }: {
    scores: Record<string, number>;
    comment: string;
    card: ICard;
  }) => {
    try {
      const { data: existingCard, error: fetchError } = await supabase
        .from("sawt_cards")
        .select("question_id, response_id")
        .eq("response_id", card.response_id)
        .single();

      if (fetchError) {
        throw fetchError;
      }
      const user_id = `${userName}_${Date.now()}`;



      const { data, error } = await supabase
      .from("UserFeedback")
      .insert([
        { question_id: existingCard.question_id, response_id: existingCard.response_id, user_id: user_id, comment: comment, accuracy: scores["Accuracy"], helpfulness: scores["Helpfulness"], balance: scores["Balance"] },
      ])
      .select()
        

      if (error) {
        throw error;
      }
    } catch (error) {}
  };

  return (
    <div>
    {cards && cards.map((card, index) => (
      <div className="flex justify-center space-x-4-x">

          <div key={index} className={`rounded-lg bg-blue p-6 text-primary`}>
          <h4 className="text-xl font-bold">{card.query}</h4>
  
            {/* <Link href={`${CARD_SHOW_PATH}/${card.id}`}> */}
          { /* LINK DOES the modal-- Need to change card.id to questionID to refer back to original card ID */}
              <div>
                <h6 className="text-xs">
                  <span className="text-purple">
                    {card.is_mine ? "You | " : null}
                  </span>
                </h6>

                <div>
                {card.responses.map((element, index) => (
                    
                    <p key={index} className="my-5">
                      {element.response}
                      
                    </p>
                  ))}
                </div>
              </div>
              <hr></hr>
          {/* <label className="flex justify-center mt-10 space-x-1-x">Rubric</label> */}

          <Rubric
            criteria={criteria}
            scores={scores}
            onScoreChange={handleScoreChange} />

          {/* </Link> */}

          <CommentBox
            scores={scores}
            card={card}
            onSubmit={submitCommentFeedback}
            onReset={resetScores} />
      
          
        </div>
        </div>
        ))
        }
        
      </div>

  );
}