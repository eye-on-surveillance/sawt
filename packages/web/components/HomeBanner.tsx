"use client";

import { HOMEPAGE_WORDS } from "@/lib/copy";
import { randItem } from "@/lib/utils";
import { useState } from "react";
import { useInterval } from "usehooks-ts";
import NewQuery from "./NewQuery";

export default function HomeBanner() {
  const [word, setWord] = useState(HOMEPAGE_WORDS[0]);
  useInterval(
    () => {
      setWord(randItem(HOMEPAGE_WORDS));
    },

    3500
  );

  return (
    <div className="bg-blue px-6 py-5 text-center text-primary sm:px-16 md:flex">
      <div className="md:grow"></div>
      <div className="md:w-3/4 md:max-w-2xl">
        <h1 className="text-lg">What is New Orleans City Council doing about</h1>
        <h2 className="mt-3 text-4xl">
          <span className="bg-brighter-blue text-secondary">{word}?</span>
        </h2>
        <NewQuery />
      </div>
      <div className="md:grow"></div>
    </div>
  );
}
