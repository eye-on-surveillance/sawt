export const RESPONSE_TYPE_DEPTH = "in_depth";
export const RESPONSE_TYPE_GENERAL = "general";

/**
 * Stored in the DB
 */
export type IUserQuery = {
  id?: string;
  query: string;
  response_type: typeof RESPONSE_TYPE_DEPTH | typeof RESPONSE_TYPE_DEPTH;
  response: string;
};

/**
 * Returned by Cloud Function getanswer endpoint
 */
export type ICard = {
  card_type: typeof RESPONSE_TYPE_DEPTH | typeof RESPONSE_TYPE_DEPTH;
  responses: IResponse[];
  query: string;
  local_timestamp: Date;
};

export type IResponse = {
  response: string;
  source_title?: string;
  source_name?: string;
  source_page_number?: string;
  source_publish_date?: string;
  source_timestamp?: string;
  source_url?: string;
};
