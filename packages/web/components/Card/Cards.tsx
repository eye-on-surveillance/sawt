import { ICardOld } from "@/lib/api";
import Card from "./Card";

const Cards = (cards: ICardOld[], clearHistory: any) => (
  <div className="mt-10">
    <div className="text-justify">{cards.map(Card)}</div>
    <button
      onClick={clearHistory}
      className="mt-4 text-center text-sm text-red-500 underline"
    >
      Clear History
    </button>
  </div>
);

export default Cards;
