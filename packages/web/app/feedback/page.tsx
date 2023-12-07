"use client";

// Import necessary modules and components
import ThreeCardLayout from "../../components/ThreeCardLayout";
import { supabase } from "../../lib/supabase/supabaseClient";
// import NextButton from '@/components/NextButton';
import { ICard } from "@/lib/api";
import { TABLES } from "@/lib/supabase/db";
import { useEffect, useState } from "react";

export const dynamic = "force-dynamic";

export default function UserFeedback() {
  // const [currentIndex, setCurrentIndex] = useState<number>(randint(0,177));
  const [userName, setUserName] = useState("");
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [answered, setAnswered] = useState<Set<number>>(new Set());
  const [fullData, setFullData] = useState<Array<Array<ICard>> | null>(null);

  const [cardArray, setCardArray] = useState<Array<Array<ICard>> | null>(null);

  // Not the best way to do it-- we really should make each of these a new page and the next/prev buttons
  // should be linked to the next/prev page. But this is a quick fix for now.
  const question_idArray = Array.from({ length: 98 }, (_, index) => index);

  // const handlePrevClick = () => {
  //   if (fullData) {
  //     setCardArray(fullData);
  //     //wraps around
  //     setCurrentIndex(
  //       (currentIndex - 1 + question_idArray.length) % question_idArray.length
  //     );
  //   } else {
  //     alert("Please wait for the rest of the cards to finish loading...");
  //   }
  // };

  const handleNextClick = () => {
    if (fullData) {
      setCardArray(fullData);
      //wraps around
      setCurrentIndex((currentIndex + 1) % question_idArray.length);
      setAnswered(new Set());
    } else {
      alert("Please wait for the rest of the cards to finish loading...");
    }
  };

  //const handleNameChange = (e) => {
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserName(e.target.value);
  };

  useEffect(() => {
    const getCard = async () => {
      try {
        const cardsArray: Array<Array<ICard>> = [];
        const { data: cards, error } = await supabase
          .from(TABLES.FEEDBACK_CARDS)
          .select("*")
          .eq("question_id", 0);
        if (cards) {
          cardsArray.push(cards);
        }
        setCardArray(cardsArray);
        console.log(cards);
      } catch (error) {
        console.error("Error fetching cards: ", error);
        // Handle the error appropriately in your UI
      }
      getCards();
    };
    getCard();
  }, []); // Run this effect only once when the component mounts

  const getCards = async () => {
    const cardsArray: Array<Array<ICard>> = [];
    try {
      for (let i = 1; i <= question_idArray.length; i++) {
        const { data: cards, error } = await supabase
          .from(TABLES.FEEDBACK_CARDS)
          .select("*")
          .eq("question_id", i);

        if (error) {
          console.error("Error fetching cards: ", error);
          // Handle the error appropriately in your UI
        }
        console.log(cards);

        if (cards) {
          cardsArray.push(cards);
        }
      }
      setFullData(cardsArray);
      // console.log(fullData);
      //setCurrentIndex(Math.floor(Math.random() * cardsArray.length));
    } catch (error) {
      console.error("Error fetching cards: ", error);
      // Handle the error appropriately in your UI
    }
  };

  if (!cardArray) {
    return <div>Loading...</div>;
  }

  return (
    <div className="h-full bg-blue px-6 text-primary md:flex">
      <div className="md:grow"></div>
      <div className="pb-24 md:w-3/4 md:max-w-2xl">
        <div className="rounded-lg bg-blue p-6 text-primary">
          <label className="mb-2 block text-lg font-bold text-gray-700">
            Please Enter Your Name:
          </label>
          <div className="flex">
            <input
              className="focus:border-blue-500 w-80 appearance-none rounded px-3 py-2 text-lg leading-tight focus:outline-none"
              type="text"
              value={userName}
              onChange={handleNameChange}
              placeholder="Your Name Here"
            />
          </div>
        </div>
        <ThreeCardLayout
          cards={cardArray[currentIndex]}
          userName={userName}
          answered={answered}
          setAnswered={setAnswered}
        />
        {answered.size === 3 && (
          <button
            onClick={handleNextClick}
            className="bg-blue-500 w-full rounded bg-secondary px-4 py-2 text-lg text-white"
          >
            Next question
          </button>
        )}
      </div>
      <div className="md:grow"></div>
    </div>
  );
}
