export const RESPONSE_TYPE_DEPTH = "in_depth";
export const RESPONSE_TYPE_GENERAL = "general";

export enum ECardType {
  QUERY_IN_DEPTH = "in_depth",
  QUERY_GENERAL = "general",
}

export enum ECardStatus {
  PUBLIC = "public",
  NEW = "new",
  ARCHIVED = "archived",
}

export type ICard = {
  id?: string;
  card_type: ECardType;
  title: string;
  subtitle?: string;
  likes?: number;
  status?: ECardStatus;
  created_at?: Date;
  responses?: IResponse[];
  citations?: ICitation[];
  // Only used client-side, because there aren't userIds for ownership
  is_mine?: boolean;
};

export type IResponse = {
  response: string;
  citations?: ICitation[];
  processing_time_ms?: number;
  card_id?: string;
};

export type ICitation = {
  source_title?: string;
  source_name?: string;
  source_page_number?: string;
  source_publish_date?: string;
  source_timestamp?: string;
  source_url?: string;
  response_id?: string;
};

/**
 * Deprecated: How data was stored in v1
 */
export type IUserQuery = {
  id?: string;
  query: string;
  response_type: ECardType;
  response: string;
};

export type ICardOld = {
  card_type: typeof RESPONSE_TYPE_DEPTH | typeof RESPONSE_TYPE_DEPTH;
  responses: IResponse[];
  citations: any[];
  query: string;
  local_timestamp: Date;
};
