import {
  getYouTubeEmbedUrl,
  getYouTubeThumbnail,
  isYouTubeURL,
} from "@/lib/utils";
import moment from "moment";
import "./Citation.css";

interface CitationProps {
  citation: any;
  index: number;
}

const citationKeyMap: { [key: string]: string } = {
  source_title: "Source Title",
  source_name: "Source Name",
  source_publish_date: "Source Publish Date",
  source_url: "Source URL",
};

const Citation = ({ citation: originalCitation, index }: CitationProps) => {
  const hasMetadata = Object.values(originalCitation).some(
    (value) => value !== null && value !== ""
  );
  if (!hasMetadata) return null;

  const {
    source_title: title,
    source_url,
    source_name: name,
    score: ignore,
    source_publish_date: publishedAt,
    ...citation
  } = originalCitation;

  const isYoutube = isYouTubeURL(source_url) && getYouTubeThumbnail(source_url);
  return (
    <div className="mb-6 w-full space-y-1 rounded-2xl p-2 text-primary lg:w-1/2">
      <div>
        <p className="font-bold lg:text-lg">
          #{index + 1}: {title}
        </p>
        <p className="text-secondary">{moment(publishedAt).fromNow()}</p>
      </div>

      <div>
        {isYoutube ? (
          <iframe
            id="ytplayer"
            src={getYouTubeEmbedUrl(source_url)}
            frameBorder="0"
            className="h-64 w-full lg:h-96"
          ></iframe>
        ) : (
          <a href={source_url} target="_blank" rel="noopener noreferrer">
            {source_url}
          </a>
        )}
      </div>

      <div>
        {Object.keys(citation).map((key, i) => (
          <div key={i}>
            <strong>
              {"\u2022"} {citationKeyMap[key] || key}
            </strong>
            : {citation[key]}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Citation;
