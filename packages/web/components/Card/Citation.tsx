import { getYouTubeEmbedUrl, getYouTubeThumbnail, isYouTubeURL } from "@/lib/utils";
import moment from "moment";
import "./Citation.css";

interface CitationProps {
  citation: any;
  index: number;
  fullscreen?: boolean;
}

const Citation = ({
  citation: originalCitation,
  index,
  fullscreen = false,
}: CitationProps) => {
  const {
    source_title: title,
    source_url,
    source_page_number: pageNumber,
    source_publish_date: publishedAt,
    source_timestamp: timestamp,
    score: ignore,
    ...otherMetadata
  } = originalCitation;

  const isYoutube = source_url && isYouTubeURL(source_url) && getYouTubeThumbnail(source_url);
  const isUrlAvailable = source_url && source_url !== "url not available";

  return (
    <div
      className={`mb-6 w-full space-y-1 rounded-2xl p-2 text-primary ${
        fullscreen ? "" : "lg:w-1/2"
      }`}
    >
      <div>
        <p className="font-bold lg:text-lg">#{index + 1}: {title}</p>
        <p className="text-black">{moment(publishedAt).fromNow()}</p>
      </div>

      {isUrlAvailable && (
        <div>
          {isYoutube ? (
            <iframe
              id="ytplayer"
              src={getYouTubeEmbedUrl(source_url, timestamp)}
              frameBorder="0"
              className="h-64 w-full lg:h-96"
            ></iframe>
          ) : (
            <a href={source_url} target="_blank" rel="noopener noreferrer">
              {source_url}
            </a>
          )}
        </div>
      )}

      {!isUrlAvailable && (
        <div>
          <div>
            <strong>Source Title</strong>: {title}
          </div>
          {pageNumber && (
            <div>
              <strong>Page Number</strong>: {pageNumber}
            </div>
          )}
          {publishedAt && (
            <div>
              <strong>Published Date</strong>: {publishedAt}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Citation;