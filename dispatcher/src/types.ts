export interface WebhookJob {
  id: string;
  endpoint_id: string;
  target_url: string;
  secret: string;
  payload: string;
  headers: Record<string, string>;
  attempt_number: number;
  max_retries: number;
}

export interface DeliveryLog {
  endpoint_id: string;
  request_payload: string;
  request_headers: Record<string, string>;
  response_code?: number;
  response_body?: string;
  status: 'SUCCESS' | 'FAILED' | 'RETRYING';
  attempt_number: number;
  duration_ms: number;
}
