export const ABOUT_BETA_PATH = "/about";
export const TIPS_PATH = "/tips";
export const CARD_SHOW_PATH = "/s";
export const HOME_PATH = "/";

export const API_NEW_CARD_PATH = "/api/v1/cards";

export const BRAND = "SAWT";
export const getPageMetadata = (
  subtitle: string,
  overrideTitle: boolean = false
) => {
  const title = overrideTitle ? subtitle : `${BRAND} - ${subtitle}`;
  return {
    title,
    description:
      "Find out what's happening in New Orleans City Council, using AI. Powered by Eye on Surveillance",
    keywords: [
      "city council",
      "new orleans",
      "nola",
      "ai",
      "llm",
      "surveillance",
      "transparency",
    ],
    creator: "Eye on Surveillance",
  };
};

export const getURL = () => {
  let url =
    process?.env?.NEXT_PUBLIC_SITE_URL ?? // Set this to your site URL in production env.
    process?.env?.NEXT_PUBLIC_VERCEL_URL ?? // Automatically set by Vercel.
    "http://localhost:3000";
  // Make sure to include `https://` when not localhost.
  url = url.includes("http") ? url : `https://${url}`;
  // Make sure to including trailing `/`.
  // url = url.charAt(url.length - 1) === "/" ? url : `${url}/`;
  return url;
};

export const getPageURL = (page: string) => {
  return `${getURL()}${page}/`;
};
