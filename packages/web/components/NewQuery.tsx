import { ECardStatus, ECardType, ICard } from "@/lib/api";
import { APP_NAME } from "@/lib/copy";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { useCardResults } from "./CardResultsProvider";

export default function NewQuery() {
  const apiEndpoint = process.env.NEXT_PUBLIC_TGI_API_ENDPOINT!;
  const [query, setQuery] = useState("");
  const [cardType, setCardType] = useState(ECardType.QUERY_IN_DEPTH);
  const { addMyCard } = useCardResults();

  const insertSupabaseCard = async (): Promise<ICard> => {
    const newCard: ICard = {
      title: query,
      card_type: cardType,
    };

    const resp = await fetch("/api/v1/cards", {
      method: "POST",
      body: JSON.stringify(newCard),
    });

    console.log("Insert data");
    if (!resp.ok) {
      console.warn("Could not record query");
      console.warn(resp);
      return newCard;
    } else {
      const cardJson = await resp.json();
      console.log("Created card");
      console.log(cardJson);
      const { card: createdCard } = cardJson as { card: ICard };
      createdCard.is_mine = true;
      createdCard.status = ECardStatus.PUBLIC;

      addMyCard(createdCard);
      return createdCard;
    }
  };

  const sendQueryToFunction = async (newCard: ICard) => {
    // Start processing question
    const answerResp = await fetch(apiEndpoint, {
      method: "POST",
      // Pass responseMode to your API endpoint
      body: JSON.stringify({ query, response_type: cardType }),
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      },
    });
    let card: any = await answerResp.json();

    console.log("got response from function");
    console.log(card);

    Object.assign(card, newCard);
    console.log("after merge with known values");
    console.log(card);

    card.citations = card.citations!.map((citation: any) => {
      return {
        source_title: citation.Title,
        source_name: citation.Name,
        source_publish_date: citation.Published,
      };
    });
    card = card as ICard;
    console.log("adapted it to new form");
    console.log(card);
    addMyCard(card);

    // await updateQueryResponded(card, queryId, startedProcessingAt);
    // setCards((oldCards: any) => {
    //   const newCards = [...oldCards, card];
    //   newCards.sort(compareCards);
    //   return newCards;
    // });
    // setQuery("");
  };

  const submitQuery = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    setQuery("");
    const newCard = await insertSupabaseCard();
    await sendQueryToFunction(newCard);
  };

  return (
    <div className="my-12">
      <form onSubmit={submitQuery}>
        <div className="relative  block">
          <FontAwesomeIcon
            className="align-center absolute left-2 top-1/2 ml-2 h-[28px] w-[28px] -translate-y-1/2 transform cursor-pointer object-contain"
            icon={faMagnifyingGlass}
          />
          <input
            className="focus:shadow-outline mb-3 block w-full appearance-none rounded-lg px-16 py-2 leading-tight text-gray-700 shadow focus:outline-none"
            id="new-query"
            type="text"
            placeholder={`Ask ${APP_NAME}`}
            autoFocus
            onChange={(e: React.FormEvent<HTMLInputElement>) => {
              setQuery(e.currentTarget.value);
            }}
          ></input>
          {/* <p className="text-xs italic text-red-500">Please choose a password.</p> */}
        </div>
        <button
          className="btn w-full rounded-lg bg-blue-600 p-2 text-2xl text-white"
          type="submit"
        >
          Get answer
        </button>
      </form>
    </div>
  );
}
