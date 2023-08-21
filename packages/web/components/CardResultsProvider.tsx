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
      setCards(Array.from(indexedCards.values()));
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
