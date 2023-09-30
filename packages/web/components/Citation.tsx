import "./Citation.css";

interface CitationProps {
  citation: any;
  index: number;
}

const citationKeyMap: { [key: string]: string } = {
  source_title: "Source Title",
  source_name: "Source Name",
  source_publish_date: "Source Publish Date",
  source_url: "Council Meeting",
};

function isYouTubeURL(url: string): boolean {
  return url.includes('youtube.com');
}

function getYouTubeThumbnail(url: string): string | null {
  const videoId = url.split("v=")[1]?.split("&")[0];
  if (!videoId) return null;
  return `https://img.youtube.com/vi/${videoId}/0.jpg`;
}

const Citation = ({ citation, index }: CitationProps) => {
  const hasMetadata = Object.values(citation).some(
    (value) => value !== null && value !== ""
  );

  return hasMetadata ? (
    <div className="citation">
      <strong>Citation {index + 1}</strong>
      {Object.keys(citation).map((key, i) => (
        <div key={i}>
          <strong>
            {"\u2022"} {citationKeyMap[key] || key} 
          </strong>
          :{" "}
          {key === "source_url" && citation[key] ? (
            isYouTubeURL(citation[key]) ? (
              <a href={citation[key]} target="_blank" rel="noopener noreferrer">
                <img src={getYouTubeThumbnail(citation[key])} alt="YouTube Thumbnail" width="200"/>
              </a>
            ) : (
              <a href={citation[key]} target="_blank" rel="noopener noreferrer">
                {citation[key]}
              </a>
            )
          ) : (
            citation[key]
          )}
        </div>
      ))}
    </div>
  ) : null;
};

export default Citation;
