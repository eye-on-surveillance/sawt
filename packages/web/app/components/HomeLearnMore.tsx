"use client";

import { HOMEPAGE_WORDS } from "@/lib/copy";
import { ABOUT_BETA_PATH } from "@/lib/paths";
import { randItem } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";
import { useInterval } from "usehooks-ts";

export default function HomeLearnMore() {
  const [word, setWord] = useState(HOMEPAGE_WORDS[0]);
  useInterval(
    () => {
      setWord(randItem(HOMEPAGE_WORDS));
    },

    3500
  );

  return (
    <div className="bg-violet-800 px-6 py-24 text-center sm:px-16 md:flex">
      <div className="md:grow"></div>
      <div className="md:w-3/4 md:max-w-2xl">
        <h1 className="rounded-lg bg-blue-200 py-4 text-4xl">
          <Link href={ABOUT_BETA_PATH} target="_blank">
            Learn more about SAWT
          </Link>
        </h1>
      </div>
      <div className="md:grow"></div>
    </div>
  );
}
