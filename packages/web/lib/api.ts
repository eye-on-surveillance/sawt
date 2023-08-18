export const RESPONSE_TYPE_DEPTH = "in_depth";
export const RESPONSE_TYPE_GENERAL = "general";

export enum EResponseType {
  RESPONSE_TYPE_DEPTH = "in_depth",
  RESPONSE_TYPE_GENERAL = "general",
}

/**
 * Stored in the DB
 */
export type IUserQuery = {
  id?: string;
  query: string;
  response_type: EResponseType;
  response: string;
};

export type ICardOld = {
  card_type: typeof RESPONSE_TYPE_DEPTH | typeof RESPONSE_TYPE_DEPTH;
  responses: IResponse[];
  citations: any[];
  query: string;
  local_timestamp: Date;
};

/**
 * Returned by Cloud Function getanswer endpoint
 */
export type ICard = {
  id?: string;
  card_type: EResponseType;
  responses: IResponse[];
  title: string;
  subtitle?: string;
  created_at: Date;
  likes: number;
};

export type IResponse = {
  response: string;
  citations?: ICitation[];
};

export type ICitation = {
  source_title?: string;
  source_name?: string;
  source_page_number?: string;
  source_publish_date?: string;
  source_timestamp?: string;
  source_url?: string;
};
