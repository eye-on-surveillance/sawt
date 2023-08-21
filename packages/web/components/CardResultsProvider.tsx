"use client";

import { ICard } from "@/lib/api";
import { createContext, useContext, useState } from "react";

type ResultsContext = {
  addMyCard: (card: ICard) => void;
  cards: ICard[];
};

const Context = createContext<ResultsContext>({
  addMyCard: () => {},
  cards: [],
});

const compareCards = (a: ICard, b: ICard) => {
  console.log("comparing two cards");
  console.log(a);
  console.log(b);
  if (!a.created_at) return 1;
  if (!b.created_at) return -1;
  return new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime();
};

export default function CardResultsProvider({
  children,
  serverCards,
}: {
  children: React.ReactNode;
  serverCards: ICard[];
}) {
  const [cards, setCards] = useState(serverCards);

  const value = {
    addMyCard: (newCard: ICard) => {
      let copy = console.log("Adding card");
      console.log(newCard);
      const indexedCards = new Map<string, ICard>();
      cards.forEach((card) => {
        indexedCards.set(card.id!, card);
      });

      // overwrite existing record, if exists
      indexedCards.set(newCard.id!, newCard);
      let newCards = Array.from(indexedCards.values());
      newCards.sort(compareCards);
      setCards(newCards);
    },
    cards,
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
