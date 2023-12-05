
"use client";

// Import necessary modules and components
import { supabase } from '../../lib/supabase/supabaseClient';
import ThreeCardLayout from '../../components/ThreeCardLayout';
// import NextButton from '@/components/NextButton';
import { useState, useEffect } from "react";
import { ICard } from '@/lib/api';
import Rubric from '@/components/Rubric';

export const dynamic = "force-dynamic";
// export const question_idArray = Array.from({ length: 99 }, (_, index) => index);
export const question_idArray = [0,1,2];

export default function UserFeedback() {
  // const [currentIndex, setCurrentIndex] = useState<number>(randint(0,177));
  const [userName, setUserName] = useState("");
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [cardArray, setCardArray] = useState<Array<ICard> | null>(null);
  const [rubricScores, setRubricScores] = useState<Record<string, number>>({});

  const handlePrevClick = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
    // setRubricScores(createDefaultScores());
  }

  

  const handleNextClick = () => {
    if (currentIndex < question_idArray.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
    // setRubricScores(createDefaultScores());
  }

  //potentially could set rubric back to 1s
  // const createDefaultScores = () => {
  //   return criteria.reduce((acc, criterion) => {
  //     acc[criterion.id] = 1;
  //     return acc;
  //   }, {});
  // };

  const handleNameChange = (e) => {
    setUserName(e.target.value);
  }

  useEffect(() => {
    const getCards = async () => {
      try {
        const cardsArray = [];
        for (let i = 1; i <= question_idArray.length; i++) {
          const { data: cards, error } = await supabase
            .from('sawt_cards')
            .select('*')
            .eq("question_id", i);
            // .eq("questionID", currentIndex)


          if (error) {
            console.error("Error fetching cards: ", error);
            // Handle the error appropriately in your UI
          }
          cardsArray.push(cards);
        }
        setCardArray(cardsArray);

      } catch (error) {
        console.error("Error fetching cards: ", error);
        // Handle the error appropriately in your UI
      }
    };

    getCards();
  }, []); // Run this effect only once when the component mounts

  if (!cardArray) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <div className="rounded-lg bg-blue p-6 text-primary">
        <label className="block text-gray-700 text-lg font-bold mb-2">
          Please Enter Your Name:
        </label>
        <div className="flex">
          <input
            className="appearance-none rounded w-80 py-2 px-3 leading-tight text-lg focus:outline-none focus:border-blue-500"
            type="text"
            value={userName}
            onChange={handleNameChange}
            placeholder="Your Name Here"
          />
        </div>
      </div>
      <ThreeCardLayout cards={cardArray[currentIndex]} userName={userName} />
      <div>
            <div className="float-left">
                <button onClick={handlePrevClick} className= "bg-blue-500 rounded bg-secondary px-4 py-2 text-white">Previous</button>
            </div>

            <div className="float-right">
                <button onClick={handleNextClick} className= "bg-blue-500 rounded bg-secondary px-4 py-2 text-white">Next</button>
            </div>    
        </div>
    </>
  );
}
