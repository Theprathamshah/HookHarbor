import amqp from 'amqplib';

export class QueueClient {
  private conn?: amqp.Connection;
  private channel?: amqp.Channel;

  constructor(private url: string) {}

  async connect(): Promise<void> {
    this.conn = await amqp.connect(this.url);
    this.channel = await this.conn.createChannel();
  }

  async consume(queue: string, onMessage: (msg: amqp.ConsumeMessage) => Promise<void>): Promise<void> {
    if (!this.channel) throw new Error('Channel not initialized. Run connect() first.');
    
    await this.channel.assertQueue(queue, { durable: true });
    await this.channel.prefetch(10); // Limit unacknowledged messages per worker

    await this.channel.consume(queue, async (msg) => {
      if (msg) {
        try {
          await onMessage(msg);
          this.channel?.ack(msg);
        } catch (err) {
          console.error('Error handling message:', err);
          // Worker code handles manual nack/ack, this is a fallback
          this.channel?.nack(msg, false, true);
        }
      }
    });
  }

  async publishToExchange(exchange: string, routingKey: string, content: Buffer): Promise<void> {
    if (!this.channel) throw new Error('Channel not initialized.');
    await this.channel.publish(exchange, routingKey, content, { persistent: true });
  }

  async close(): Promise<void> {
    await this.channel?.close();
    await this.conn?.close();
  }
}
