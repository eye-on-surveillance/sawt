interface ResponseProps {
  response: { response: string };
}

const CardResponse = ({ response }: ResponseProps) => {
  return (
    <div className="response">
      <p>{response.response}</p>
    </div>
  );
};

export default CardResponse;
