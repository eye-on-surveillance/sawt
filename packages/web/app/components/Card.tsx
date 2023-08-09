import Citation from "./Citation";
import Response from "./Response";

interface CardProps {
  card_type: string;
  responses: { response: string }[];
  citations: any[];
  query: string;
}

const Card = ({ card_type, responses, citations, query }: CardProps) => {
  return (
    <div className={`mb-4 rounded bg-white p-6 shadow ${card_type}`}>
      <h2 className="mb-4 text-xl font-bold">{query}</h2>{" "}
      {/* Display the user's query */}
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
