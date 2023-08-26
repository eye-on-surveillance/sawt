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
  likesForCard: (cardId: string) => number;
  handleLike: (cardId: string) => Promise<void>;
};

const Context = createContext<ResultsContext>({
  addMyCard: () => {},
  fetchMoreCards: async () => {},
  cards: [],
  indexedCards: new Map<string, ICard>(),
  hasMoreCards: true,
  likesForCard: () => 0,
  handleLike: async () => {},
});

const compareCards = (a: ICard, b: ICard) => {
  if (!a.created_at) return 1;
  if (!b.created_at) return -1;
  return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
};

const getIndexedCards = (cards: ICard[]) => {
  const indexedCards = new Map<string, ICard>();
  cards.forEach((card) => {
    indexedCards.set(card.id!, card);
  });
  return indexedCards;
};

const fetchCardsFromSupabase = async (
  lastCreatedAt?: string
): Promise<ICard[]> => {
  let query = supabase
    .from("cards")
    .select("*")
    .eq("status", "public")
    .order("created_at", { ascending: false })
    .limit(5);

  if (lastCreatedAt) {
    query = query.lt("created_at", lastCreatedAt);
  }

  const { data, error } = await query;

  if (error) {
    throw error;
  }

  return data || [];
};

const fetchLikesForCard = async (cardId: string): Promise<number> => {
  const { data, error } = await supabase
    .from("cards")
    .select("likes")
    .eq("id", cardId)
    .single();

  if (error) {
    console.error("Error fetching likes count:", error);
    throw error;
  }

  return data?.likes || 0;
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
      const lastCreatedAt = lastCard?.created_at;
      const newCards = await fetchCardsFromSupabase(lastCreatedAt?.toISOString());

      // If no new cards are fetched, update the hasMoreCards state to false
      if (!newCards || newCards.length === 0) {
        console.log("No new cards fetched.");
        setHasMoreCards(false);
        return;
      }

      setCards((prevCards) => {
        // Filter out any cards from the newCards array that already exist in our current state
        const uniqueNewCards = newCards.filter(
          (newCard) => !prevCards.some((prevCard) => prevCard.id === newCard.id)
        );

        // Combine the current set of cards with the unique new cards and sort them
        return [...prevCards, ...uniqueNewCards].sort(compareCards);
      });
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

  const handleLike = async (cardId: string) => {
    try {
      const res = await fetch("/api/v1/cards/like", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cardId }),
      });

      if (res.ok) {
        const updatedLikes = await fetchLikesForCard(cardId);
        const card = indexedCards.get(cardId);
        if (card) {
          const updatedCard = { ...card, likes: updatedLikes };
          indexedCards.set(cardId, updatedCard);
          setIndexedCards(new Map(indexedCards));
        }
      } else {
        console.error("Error liking card:", await res.json());
      }
    } catch (error) {
      console.error("Error occurred in handleLike:", error);
    }
  };

  const likesForCard = (cardId: string) => {
    const card = indexedCards.get(cardId);
    return card?.likes || 0;
  };

  const value = {
    addMyCard,
    fetchMoreCards,
    cards,
    indexedCards,
    hasMoreCards,
    likesForCard,
    handleLike,
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
