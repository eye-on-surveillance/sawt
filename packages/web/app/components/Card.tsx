import { ICard } from "@/lib/api";
import Response from "./Response";

const Card = (card: ICard) => (
  <div
    className="my-4 rounded-lg border bg-gray-100 p-6"
    key={crypto.randomUUID()}
  >
    <p className="font-bold text-blue-600">{card.query}</p>
    {card.responses.map(Response)}
  </div>
);

export default Card;
