import { TABLES } from "@/lib/supabase/db";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import CardResultsProvider from "../../components/CardResultsProvider";
import HomeBanner from "../../components/HomeBanner";
import HomeLearnMore from "../../components/HomeLearnMore";
import HomeResults from "../../components/HomeResults";

export const dynamic = "force-dynamic";

export default async function Home() {
  const supabase = createServerComponentClient({ cookies });
  const { data: cards } = await supabase.from(TABLES.CARDS).select("*");
  console.log("homepage");
  console.log(cards);

  return (
    <>
      {/* There is no user session so the new query input in the banner
        needs to locally communicated with results in order to identify
        queries created by the current user. */}
      <CardResultsProvider serverCards={cards || []}>
        <HomeBanner />
        <HomeResults />
      </CardResultsProvider>
      <HomeLearnMore />
    </>
  );
}
