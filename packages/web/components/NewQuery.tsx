import { ECardStatus, ECardType, ICard } from "@/lib/api";
import { APP_NAME } from "@/lib/copy";
import { API_NEW_CARD_PATH } from "@/lib/paths";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { useCardResults } from "./CardResultsProvider";
import { ABOUT_BETA_PATH } from "@/lib/paths";
import Link from "next/link";

function YouTubeEmbed({ url }: { url: string }) {
  const videoId = url.split("v=")[1]?.split("&")[0];
  if (!videoId) return null;

  return (
    <iframe 
      width="560" 
      height="315" 
      src={`https://www.youtube.com/embed/${videoId}`} 
      frameBorder="0" 
      title="YouTube Video"
      allowFullScreen
    ></iframe>
  );
}

function YouTubeThumbnail({ url }: { url: string }) {
  const videoId = url.split("v=")[1]?.split("&")[0];
  if (!videoId) return null;

  return (
    <a href={url} target="_blank" rel="noopener noreferrer">
      <img 
        width="560" 
        height="315" 
        src={`https://img.youtube.com/vi/${videoId}/0.jpg`} 
        alt="YouTube Thumbnail"
      />
    </a>
  );
}

export default function NewQuery() {
  const apiEndpoint = process.env.NEXT_PUBLIC_TGI_API_ENDPOINT!;
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [cardType, setCardType] = useState(ECardType.QUERY_IN_DEPTH);
  const { addMyCard } = useCardResults();
  const [card, setCard] = useState<ICard | null>(null);  


  const insertSupabaseCard = async (): Promise<ICard> => {
    const newCard: ICard = {
      title: query,
      card_type: cardType,
    };

    const resp = await fetch(API_NEW_CARD_PATH, {
      method: "POST",
      body: JSON.stringify(newCard),
    });

    if (!resp.ok) {
      return newCard;
    } else {
      const cardJson = await resp.json();
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

    card = Object.assign({}, newCard, card);

    card.citations = card.citations!.map((citation: any) => {
      return {
        source_title: citation.Title,
        source_name: citation.Name,
        source_publish_date: citation.Published,
        source_url: citation.URL, 
      };
    });
    card = card as ICard;
    setQuery("");
    setIsProcessing(false);
    return card;
  };

  const updateQueryResponded = async (
    card: ICard,
    startedProcessingAt: number
  ) => {
    const genResponseMs = Math.ceil(Date.now() - startedProcessingAt);
    const queryUpdate = {
      responses: card.responses,
      citations: card.citations,
      processing_time_ms: genResponseMs,
    };
    const { error } = await supabase
      .from(TABLES.CARDS)
      .update(queryUpdate)
      .eq("id", card.id);

    if (error) {
      console.warn("Could not record query");
      console.warn(error);
      return;
    } else {
    }
  };

  const submitQuery = async (e?: React.FormEvent<HTMLFormElement>) => {
    e?.preventDefault();

    if (query.length <= 10) return;

    const startedProcessingAt = Date.now();
    setIsProcessing(true);
    const newCard = await insertSupabaseCard();
    const cardWResp = await sendQueryToFunction(newCard);
    addMyCard(cardWResp);
    await updateQueryResponded(cardWResp, startedProcessingAt);  
  };

  return (
    <div className="my-12">
      <form onSubmit={submitQuery}>
        <div className="relative block">
          <FontAwesomeIcon
            className="absolute left-2 top-1/2 ml-2 h-[24px] w-[24px] -translate-y-1/2 cursor-pointer object-contain"
            icon={faMagnifyingGlass}
          />
          <input
            className="mb-3 block w-full appearance-none rounded-lg px-16 py-2 leading-tight text-secondary shadow focus:shadow-lg focus:outline-none"
            id="new-query"
            type="text"
            value={query}
            placeholder={`Ask ${APP_NAME} a question about New Orleans' City Council`}
            autoFocus
            disabled={isProcessing}
            onChange={(e) => setQuery(e.currentTarget.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault(); 
                submitQuery();
              }
            }}
          />
        </div>
      </form>

        <p>
          This tool is under active development. Responses may be inaccurate.{" "}
          <Link href={ABOUT_BETA_PATH} className="underline">
            Learn more
          </Link>
        </p>

      <div className="mt-10">
        {card?.citations?.map((citation, index) => (
          <div key={index}>
            <p>{citation.source_title}</p>
            {citation.source_url && citation.source_url.includes("youtube.com") && 
              <YouTubeThumbnail url={citation.source_url} />}
          </div>
        ))}
      </div>
    </div>
  );
}
