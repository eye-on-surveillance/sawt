"use client";

import { ICard } from "@/lib/api";
import { supabase } from "@/lib/supabase/supabaseClient";
import { createContext, useContext, useEffect, useState } from "react";

type ResultsContext = {
  addMyCard: (card: ICard) => void;
  fetchMoreCards: () => Promise<void>;
  cards: ICard[];
  indexedCards: Map<string, ICard>;
  hasMoreCards: boolean;
};

const Context = createContext<ResultsContext>({
  addMyCard: () => {},
  fetchMoreCards: async () => {},
  cards: [],
  indexedCards: new Map<string, ICard>(),
  hasMoreCards: true,
});

const compareCards = (a: ICard, b: ICard) => {
  if (!a.id) return 1;
  if (!b.id) return -1;
  return parseInt(b.id!) - parseInt(a.id!);
};

const getIndexedCards = (cards: ICard[]) => {
  const indexedCards = new Map<string, ICard>();
  cards.forEach((card) => {
    indexedCards.set(card.id!, card);
  });
  return indexedCards;
};

const fetchCardsFromSupabase = async (lastId?: string): Promise<ICard[]> => {
  let query = supabase
    .from("cards")
    .select("*")
    .eq("status", "public")
    .limit(5);

  if (lastId) {
    query = query.lt("id", lastId);
  }

  const { data, error } = await query;

  if (error) {
    throw error;
  }

  return data || [];
};

export default function CardResultsProvider({
  children,
  serverCards,
}: {
  children: React.ReactNode;
  serverCards: ICard[];
}) {
  serverCards.sort(compareCards);
  const [cards, setCards] = useState(serverCards.slice(0, 5));
  const [indexedCards, setIndexedCards] = useState(
    getIndexedCards(serverCards)
  );
  const [hasMoreCards, setHasMoreCards] = useState(true);

  const fetchMoreCards = async () => {
    try {
      const lastCard = cards[cards.length - 1];
      const newCards = await fetchCardsFromSupabase(lastCard?.id);
      console.log("Fetched new cards:", newCards);

      if (newCards.length === 0) {
        setHasMoreCards(false);
      } else {
        setCards((prevCards) => {
          const updatedCards = [...prevCards, ...newCards];
          console.log("Updated cards list:", updatedCards);
          return updatedCards;
        });
      }
    } catch (error) {
      console.error("Failed to fetch more cards:", error);
    }
  };

  useEffect(() => {
    setIndexedCards(getIndexedCards(cards));
  }, [cards]);

  const addMyCard = (newCard: ICard) => {
    const _cards = getIndexedCards(cards);
    _cards.set(newCard.id!, newCard);
    let newCards = Array.from(_cards.values());
    newCards.sort(compareCards);
    setCards(newCards);
  };

  const value = {
    addMyCard,
    fetchMoreCards,
    cards,
    indexedCards,
    hasMoreCards,
  };

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export const useCardResults = () => {
  const context = useContext(Context);

  if (context === undefined) {
    throw new Error("useCardResults must be used inside CardResultsProvider");
  }

  return context;
};
