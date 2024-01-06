import { ECardStatus, ECardType, ICard } from "@/lib/api";
import { APP_NAME } from "@/lib/copy";
import { ABOUT_BETA_PATH, API_NEW_CARD_PATH } from "@/lib/paths";
import { TABLES } from "@/lib/supabase/db";
import { supabase } from "@/lib/supabase/supabaseClient";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useCardResults } from "../CardResultsProvider";
import styles from "./homebanner.module.scss";

type SupabaseRealtimePayload<T = any> = {
  old: T;
  new: T;
};

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
  const [submissionStarted, setSubmissionStarted] = useState(false);
  const [processingComplete, setProcessingComplete] = useState(false);
  const [currentCardId, setCurrentCardId] = useState<string | null>(null);
  const [pollingIntervalId, setPollingIntervalId] = useState<number | null>(
    null
  );

  const submitQuery = async (e?: React.FormEvent<HTMLFormElement>) => {
    e?.preventDefault();

    if (query.length <= 10) return;

    setIsProcessing(true);
    const newCard = await insertSupabaseCard();
    if (newCard) {
      await sendQueryToFunction(newCard);
      setCurrentCardId(newCard.id ?? null);
      setQuery("");
    }
  };

  const scrollToQuery = () => {
    setTimeout(() => {
      const element = document.getElementById("loading");
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 1500); // Adjust the delay duration (in milliseconds) as needed
  };

  const clearQuery = () => {
    setQuery("");
  };

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
      setCurrentCardId(createdCard.id ?? null);
      return createdCard;
    }
  };

  const sendQueryToFunction = async (newCard: ICard) => {
    setIsProcessing(true);

    try {
      const response = await fetch(apiEndpoint, {
        method: "POST",
        body: JSON.stringify({
          query,
          response_type: cardType,
          card_id: newCard.id,
        }),
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // Start polling Supabase for updates
      const interval = setInterval(async () => {
        const { data, error } = await supabase
          .from(TABLES.CARDS)
          .select("*")
          .eq("id", newCard.id)
          .single();

        if (error) {
          console.error("Error fetching updated card:", error);
          clearInterval(interval);
          setIsProcessing(false);
          return;
        }

        if (data && data.responses && data.citations) {
          setCard(data);
          addMyCard(data);
          clearInterval(interval);
          setIsProcessing(false);
        }
      }, 5000);

      setPollingIntervalId(interval as unknown as number);
    } catch (error) {
      console.error("There was a problem with the fetch operation: ", error);
      if (pollingIntervalId !== null) {
        clearInterval(pollingIntervalId);
      }
      setIsProcessing(false);
    }
  };

  useEffect(() => {
    return () => {
      if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
      }
    };
  }, [pollingIntervalId]);

  return (
    <div className="my-12">
      <form onSubmit={submitQuery}>
        <div className="relative block">
          <FontAwesomeIcon
            className="absolute left-2 top-9 ml-2 h-[24px] w-[24px] -translate-y-1/2 cursor-pointer object-contain"
            icon={faMagnifyingGlass}
          />
          <input
            className="mb-3 block w-full appearance-none rounded-lg px-16 py-2 leading-tight text-black shadow focus:shadow-lg focus:outline-none"
            id="new-query"
            type="text"
            value={query}
            placeholder={`Ask ${APP_NAME} a question about New Orleans' City Council`}
            autoFocus
            disabled={isProcessing}
            onChange={(e) => setQuery(e.currentTarget.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                submitQuery();
              }
            }}
          />
          {query && (
            <button
              onClick={clearQuery}
              className="absolute right-2 top-4 cursor-pointer p-2"
            >
              X
            </button>
          )}
        </div>
        {isProcessing ? (
          <div className={styles["lds-facebook"]}>
            <div></div>
            <div></div>
            <div></div>
          </div>
        ) : (
          <button
            className={`w-full rounded-lg md:w-1/2 ${
              isProcessing ? "cursor-wait bg-primary" : "bg-primary"
            } p-2 text-2xl text-blue`}
            onClick={() => scrollToQuery()}
            type="submit"
            disabled={isProcessing}
          >
            Get answer from Sawt
          </button>
        )}
      </form>

      <p className="text-left font-light">
        This tool is under active development. Responses may be inaccurate.{" "}
        <Link href={ABOUT_BETA_PATH} className="underline">
          Learn more
        </Link>
      </p>
    </div>
  );
}
