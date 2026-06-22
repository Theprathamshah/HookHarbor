import axios from 'axios';
import * as crypto from 'crypto';

export function signPayload(payload: string, secret: string, timestamp: number): string {
  const toSign = `${timestamp}.${payload}`;
  const signature = crypto
    .createHmac('sha256', secret)
    .update(toSign)
    .digest('hex');
  return `t=${timestamp},v1=${signature}`;
}

export async function forwardWebhook(
  url: string,
  payload: string,
  secret: string,
  customHeaders: Record<string, string>
): Promise<{ status: number; data: string; duration: number }> {
  const timestamp = Math.floor(Date.now() / 1000);
  const signature = signPayload(payload, secret, timestamp);

  const headers = {
    ...customHeaders,
    'Content-Type': 'application/json',
    'X-HookHarbor-Timestamp': timestamp.toString(),
    'X-HookHarbor-Signature': signature,
    'User-Agent': 'HookHarbor-Dispatcher/1.0',
  };

  const startTime = Date.now();
  try {
    const response = await axios.post(url, payload, {
      headers,
      timeout: 10000, // 10 seconds timeout
      validateStatus: () => true, // resolve promise for any HTTP status
    });
    return {
      status: response.status,
      data: typeof response.data === 'string' ? response.data : JSON.stringify(response.data),
      duration: Date.now() - startTime,
    };
  } catch (error: any) {
    return {
      status: 0,
      data: error.message || 'Network Error',
      duration: Date.now() - startTime,
    };
  }
}
