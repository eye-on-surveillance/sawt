"use client";

// Import statements
import { ICard } from "@/lib/api"; // Importing the interface for card objects
import { supabase } from "@/lib/supabase/supabaseClient"; // Importing the initialized Supabase client
import { createContext, useContext, useEffect, useState } from "react"; // Importing React hooks and context functions

// Defining the shape of the context for card results
type ResultsContext = {
  addMyCard: (card: ICard) => void; // Function to add a new card to the context
  fetchMoreCards: () => Promise<void>; // Function to load more cards from the database
  cards: ICard[]; // An array of card objects
  indexedCards: Map<string, ICard>; // A map to hold cards indexed by their IDs for easy retrieval
  hasMoreCards: boolean; // Boolean to indicate if there are more cards to load
  likesForCard: (cardId: string) => number; // Function to get the number of likes for a specific card
  handleLike: (cardId: string) => Promise<void>; // Function to handle liking a card
};

// Creating the context with default values
const Context = createContext<ResultsContext>({
  addMyCard: () => {}, // No-op function for adding a card
  fetchMoreCards: async () => {}, // No-op async function for fetching more cards
  cards: [], // Initially, the card list is empty
  indexedCards: new Map<string, ICard>(), // Initializing the indexed map
  hasMoreCards: true, // Initially assume there are more cards to load
  likesForCard: () => 0, // Function returning 0 likes for any card by default
  handleLike: async () => {}, // No-op async function for handling likes
});

// Utility function to compare cards by their creation date
const compareCards = (a: ICard, b: ICard) => {
  if (!a.created_at) return 1; // If 'a' doesn't have a creation date, it comes last
  if (!b.created_at) return -1; // If 'b' doesn't have a creation date, it comes last
  // Otherwise, compare by the timestamp of the creation dates
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

      if (!lastCreatedAt) {
        return;
      }

      const isoString = new Date(lastCreatedAt).toISOString();
      const formattedLastCreatedAt =
        isoString.replace("T", " ").slice(0, -1) + "+00";

      const newCards = await fetchCardsFromSupabase(formattedLastCreatedAt);

      if (!newCards || newCards.length === 0) {
        setHasMoreCards(false);
        return;
      }

      setCards((prevCards) => {
        const uniqueNewCards = newCards.filter(
          (newCard) => !prevCards.some((prevCard) => prevCard.id === newCard.id)
        );

        return [...prevCards, ...uniqueNewCards].sort(compareCards);
      });
    } catch (error) {
      console.error("Error fetching more cards:", error);
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
      }
    } catch (error) {}
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
