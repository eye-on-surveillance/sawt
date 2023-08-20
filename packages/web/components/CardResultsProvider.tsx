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
    addMyCard: (card: ICard) => {
      console.log("Adding card");
      console.log(card);
      setCards([card, ...cards]);
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
