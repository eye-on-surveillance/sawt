import Citation from "./Citation";
import Response from "./Response";

interface CardProps {
  card_type: string;
  responses: { response: string }[];
  citations: any[];
}

const Card = ({ card_type, responses, citations }: CardProps) => {
  return (
    <div className={`mb-4 rounded bg-white p-6 shadow ${card_type}`}>
      {responses.map((response, index) => (
        <Response response={response} key={index} />
      ))}
      {citations.map((citation, index) => (
        <Citation citation={citation} index={index} key={index} />
      ))}
    </div>
  );
};

export default Card;
