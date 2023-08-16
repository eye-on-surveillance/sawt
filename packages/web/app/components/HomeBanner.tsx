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
    <div className="px-6 py-5 text-center sm:px-16">
      <h1 className="text-xl">What New Orleans city council is doing</h1>
      <h2 className="mt-3 text-4xl">
        about <span className="bg-red-300">{word}</span>
      </h2>
      <NewQuery />
    </div>
  );
}
