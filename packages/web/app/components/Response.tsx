import { IResponse } from "@/lib/api";

const renderSourceInfo = (
  label: string,
  info: any,
  is_link: boolean = false
) => {
  if (!info) return null;
  if (is_link) {
    return (
      <li>
        {label}:{" "}
        <a href={info} target="_blank">
          {info}
        </a>
      </li>
    );
  }
  return (
    <li>
      {label}: {info}
    </li>
  );
};

const Response = (response: IResponse) => (
  <div key={crypto.randomUUID()} className="my-4">
    <p>
      <strong>{response.response}</strong>
    </p>

    {response.source_title && (
      <div className="text-left text-sm">
        <p className="mt-2">
          <u>Citation</u>
        </p>
        <ul className="list-inside list-disc">
          {renderSourceInfo("Title", response.source_title)}
          {renderSourceInfo("Published", response.source_publish_date)}
          {renderSourceInfo("URL", response.source_url, true)}
          {renderSourceInfo("Video timestamp", response.source_timestamp)}
          {renderSourceInfo("Page number", response.source_page_number)}
          {renderSourceInfo("Name", response.source_name)}
        </ul>
      </div>
    )}
  </div>
);

export default Response;
