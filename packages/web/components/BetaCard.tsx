import { ICard, ICitation, IResponse } from "@/lib/api";
import moment from "moment";
import CardResponse from "./CardResponse";
import Citation from "./Citation";

const BetaCard = ({ card }: { card: ICard }) => {
  const responses: IResponse[] = card.responses ?? [];
  const citations: ICitation[] = card.citations ?? [];

  return (
    <div className="px-12 py-6">
      <div className="my-5">
        <h1 className="text-2xl">{card.title}</h1>
        <h1 className="text-sm">{moment(card.created_at!).fromNow()}</h1>
      </div>
      {responses!.map((response, index) => (
        <CardResponse response={response} key={index} />
      ))}
      <div className="text-sm">
        {citations!.map((citation, index) => (
          <Citation citation={citation} index={index} key={index} />
        ))}
      </div>
    </div>
  );
};

export default BetaCard;
