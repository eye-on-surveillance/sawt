import { ICard, ICitation, IResponse } from "@/lib/api";
import CardResponse from "./CardResponse";
import Citation from "./Citation";

const BetaCard = ({ card }: { card: ICard }) => {
  const responses: IResponse[] = card.responses ?? [];
  const citations: ICitation[] = card.citations ?? [];

  return (
    <div className="p-12">
      <div className="my-5">
        <h1 className="text-2xl">{card.title}</h1>
        <h1 className="text-sm">{card.created_at?.toString()}</h1>
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
