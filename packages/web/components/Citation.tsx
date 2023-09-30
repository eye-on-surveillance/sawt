import "./Citation.css";

interface CitationProps {
  citation: any;
  index: number;
}

const citationKeyMap: { [key: string]: string } = {
  source_title: "Source Title",
  source_name: "Source Name",
  source_publish_date: "Source Publish Date",
  source_url: "Source URL (with timestamp)",
};

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
          {key === "source_url" && citation[key] ? ( // Check if the current key is 'source_url' and it exists
            <a href={citation[key]} target="_blank" rel="noopener noreferrer">
              {citation[key]}
            </a>
          ) : (
            citation[key]
          )}
        </div>
      ))}
    </div>
  ) : null;
};

export default Citation;
