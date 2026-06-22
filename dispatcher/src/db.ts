import { Pool } from 'pg';
import { DeliveryLog } from './types';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/hookharbor?sslmode=disable',
});

export async function logDelivery(log: DeliveryLog): Promise<void> {
  const query = `
    INSERT INTO delivery_logs (
      endpoint_id, request_payload, request_headers, response_code, response_body, status, attempt_number, duration_ms
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
  `;
  const values = [
    log.endpoint_id,
    log.request_payload,
    JSON.stringify(log.request_headers),
    log.response_code,
    log.response_body,
    log.status,
    log.attempt_number,
    log.duration_ms
  ];

  await pool.query(query, values);
}
