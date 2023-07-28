import React from "react";
import Response from "./Response";
import Citation from "./Citation";

interface CardProps {
  card_type: string;
  responses: { response: string }[];
  citations: any[];
}

const Card = ({ card_type, responses, citations }: CardProps) => {
  return (
    <div className={`card ${card_type} border border-gray-500 p-4 mb-4`}>
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
