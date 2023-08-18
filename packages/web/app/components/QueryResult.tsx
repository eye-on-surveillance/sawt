import { ICard } from "@/lib/api";
import { faShare, faThumbsUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const MAX_CHARACTERS_PREVIEW = 200;

type QueryResultParams = {
  card: ICard;
};

export default function QueryResult(queryResultParams: QueryResultParams) {
  const { card } = queryResultParams;
  const response = card.responses[0].response;
  return (
    <div className="my-6 rounded-lg bg-blue-200 p-6">
      <h4 className="text-xl font-bold">{card.title}</h4>
      <h6 className="text-xs">{card.created_at.toString()}</h6>
      <p className="my-3">
        {response.substring(0, MAX_CHARACTERS_PREVIEW)}
        {response.length > MAX_CHARACTERS_PREVIEW ? "..." : null}
      </p>
      <div className="text-sm">
        <span>
          <FontAwesomeIcon
            icon={faThumbsUp}
            className="mx-2 h-5 w-5 align-middle"
          />
          {card.likes}
        </span>

        <span className="ml-3">
          <FontAwesomeIcon
            icon={faShare}
            className="mx-2 h-5 w-5 align-middle"
          />
          Share
        </span>
      </div>
    </div>
  );
}
