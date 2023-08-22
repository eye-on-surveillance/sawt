"use client";

import { ICard } from "@/lib/api";
import { createContext, useContext, useEffect, useState } from "react";

type ResultsContext = {
  addMyCard: (card: ICard) => void;
  cards: ICard[];
  indexedCards: Map<string, ICard>;
};

const Context = createContext<ResultsContext>({
  addMyCard: () => {},
  cards: [],
  indexedCards: new Map<string, ICard>(),
});

const compareCards = (a: ICard, b: ICard) => {
  if (!a.created_at) return 1;
  if (!b.created_at) return -1;
  return new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime();
};

const getIndexedCards = (cards: ICard[]) => {
  const indexedCards = new Map<string, ICard>();
  cards.forEach((card) => {
    indexedCards.set(card.id!, card);
  });
  return indexedCards;
};

export default function CardResultsProvider({
  children,
  serverCards,
}: {
  children: React.ReactNode;
  serverCards: ICard[];
}) {
  serverCards.sort(compareCards);
  const [cards, setCards] = useState(serverCards);
  const [indexedCards, setIndexedCards] = useState(
    getIndexedCards(serverCards)
  );

  useEffect(() => {
    setIndexedCards(getIndexedCards(cards));
  }, [cards]);

  const value = {
    addMyCard: (newCard: ICard) => {
      const _cards = getIndexedCards(cards);
      // overwrite existing record, if exists
      _cards.set(newCard.id!, newCard);
      let newCards = Array.from(_cards.values());
      newCards.sort(compareCards);
      setCards(newCards);
    },
    cards,
    indexedCards,
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
