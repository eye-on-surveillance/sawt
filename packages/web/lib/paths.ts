export const ABOUT_BETA_PATH = "/about";
export const TIPS_PATH = "/tips";
export const CARD_SHOW_PATH = "/s";
export const HOME_PATH = "/";
export const USER_FEEDBACK = "/feedback";


export const API_NEW_CARD_PATH = "/api/v1/cards";

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
