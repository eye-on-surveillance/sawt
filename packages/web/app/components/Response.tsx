import React from "react";

interface ResponseProps {
  response: { response: string };
}

const Response = ({ response }: ResponseProps) => {
  return (
    <div className="response">
      <p>{response.response}</p>
    </div>
  );
};

export default Response;
