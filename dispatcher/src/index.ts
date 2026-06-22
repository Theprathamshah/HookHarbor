import * as dotenv from 'dotenv';
dotenv.config();

import { QueueClient } from './queue';
import { forwardWebhook } from './httpClient';
import { logDelivery } from './db';
import { WebhookJob } from './types';

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@localhost:5672/';
const JOBS_QUEUE = 'webhook.jobsQueue';
const RETRY_EXCHANGE = 'webhook.retryExchange';
const DLQ_QUEUE = 'webhook.dlq';

async function start() {
  console.log('HookHarbor Dispatcher Worker starting up...');
  const queue = new QueueClient(RABBITMQ_URL);
  await queue.connect();

  await queue.consume(JOBS_QUEUE, async (msg) => {
    const job: WebhookJob = JSON.parse(msg.content.toString());
    console.log(`Processing Webhook Job ${job.id} for Endpoint ${job.endpoint_id} (Attempt ${job.attempt_number})`);

    const result = await forwardWebhook(
      job.target_url,
      job.payload,
      job.secret,
      job.headers
    );

    const isSuccess = result.status >= 200 && result.status < 300;

    if (isSuccess) {
      console.log(`Job ${job.id} Succeeded with status ${result.status}`);
      await logDelivery({
        endpoint_id: job.endpoint_id,
        request_payload: job.payload,
        request_headers: job.headers,
        response_code: result.status,
        response_body: result.data,
        status: 'SUCCESS',
        attempt_number: job.attempt_number,
        duration_ms: result.duration,
      });
    } else {
      console.log(`Job ${job.id} Failed with status ${result.status}`);
      
      if (job.attempt_number >= job.max_retries) {
        console.warn(`Job ${job.id} exceeded max retries (${job.max_retries}). Routing to DLQ.`);
        await logDelivery({
          endpoint_id: job.endpoint_id,
          request_payload: job.payload,
          request_headers: job.headers,
          response_code: result.status,
          response_body: result.data,
          status: 'FAILED',
          attempt_number: job.attempt_number,
          duration_ms: result.duration,
        });

        // Send to Dead Letter Queue (durable publish)
        await queue.publishToExchange('', DLQ_QUEUE, msg.content);
      } else {
        const nextAttempt = job.attempt_number + 1;
        console.log(`Scheduling retry ${nextAttempt} for Job ${job.id}`);
        await logDelivery({
          endpoint_id: job.endpoint_id,
          request_payload: job.payload,
          request_headers: job.headers,
          response_code: result.status,
          response_body: result.data,
          status: 'RETRYING',
          attempt_number: job.attempt_number,
          duration_ms: result.duration,
        });

        // Calculate appropriate TTL delay exchange routing key
        let routingKey = 'retry.15m';
        if (nextAttempt === 2) routingKey = 'retry.1m';
        else if (nextAttempt === 3) routingKey = 'retry.5m';

        const updatedJob: WebhookJob = {
          ...job,
          attempt_number: nextAttempt,
        };

        // Publish to retry delay exchange
        await queue.publishToExchange(RETRY_EXCHANGE, routingKey, Buffer.from(JSON.stringify(updatedJob)));
      }
    }
  });

  console.log(`Worker connected and listening on queue "${JOBS_QUEUE}"`);
}

start().catch((err) => {
  console.error('Fatal worker error:', err);
  process.exit(1);
});
