import { ICitation } from "./api";

export const randItem = (items: any) => {
  return items[Math.floor(Math.random() * items.length)];
};

export const getThumbnail = (citations: ICitation[]) => {
  return citations
    .map((c) => {
      let score = 0;
      if (isYouTubeURL(c.source_url || "")) score = 10;
      return Object.assign(c, { score });
    })
    .sort((a, b) => b.score - a.score)
    .find(() => true);
};

export function isYouTubeURL(url: string | undefined): boolean {
  return !!url && url.includes("youtube.com");
}

export function getYouTubeThumbnail(url: string): string | undefined {
  const videoId = url.split("v=")[1]?.split("&")[0];
  if (!videoId) return undefined;
  return `https://img.youtube.com/vi/${videoId}/0.jpg`;
}

export function getYouTubeEmbedUrl(
  url: string | undefined
): string | undefined {
  if (!url) return undefined;
  const videoId = url.split("v=")[1]?.split("&")[0];
  const t = url.split("t=")[1].split("s")[0];
  if (!videoId) return undefined;
  return `https://www.youtube.com/embed/${videoId}?autoplay=0&start=${t}`;
}
