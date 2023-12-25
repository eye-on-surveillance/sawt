import { getPageMetadata } from "@/lib/paths";
import HomeBanner from "../components/HomeBanner/HomeBanner";
import HomeLearnMore from "../components/HomeLearnMore";
import HomeResults from "../components/HomeResults/HomeResults";

export const dynamic = "force-dynamic";

export const metadata = getPageMetadata("Eye on Surveillance");

export default async function Home() {
  return (
    <>
      <HomeBanner />
      <HomeResults />
      <HomeLearnMore />
    </>
  );
}
