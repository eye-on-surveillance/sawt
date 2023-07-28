import "./Citation.css";

interface CitationProps {
  citation: any;
  index: number;
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
            {"\u2022"} {key}
          </strong>
          : {citation[key]}
        </div>
      ))}
    </div>
  ) : null;
};

export default Citation;
