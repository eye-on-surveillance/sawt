import HomeBanner from "../components/HomeBanner";
import HomeLearnMore from "../components/HomeLearnMore";
import HomeResults from "../components/HomeResults";
import { supabase } from '../lib/supabase/supabaseClient';

export const dynamic = "force-dynamic";

export default async function Home() {
  const { data: cards, error } = await supabase
    .from('cards')
    .select('*')
    .limit(3);

  if (error) {
    console.error("Error fetching cards:", error);
    // Handle the error appropriately in your UI
  }
    //  <ThreeCardLayout cards={cards} />

  return (
    <>
      <HomeBanner />
      <HomeResults />
      <HomeLearnMore />
    </>
  );
}
