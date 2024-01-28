import { getPageMetadata } from "@/lib/paths";
import HomeLearnMore from "../components/Footer/HomeLearnMore";
import HomeBanner from "../components/HomeBanner/HomeBanner";
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
