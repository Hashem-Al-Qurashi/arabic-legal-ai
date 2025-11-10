/**
 * Retry logic utility with exponential backoff
 * Provides robust retry mechanisms for network operations
 */

export interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
  shouldRetry?: (error: any, attemptNumber: number) => boolean;
  onRetry?: (error: any, attemptNumber: number, nextDelay: number) => void;
}

/**
 * Default retry configuration
 */
const DEFAULT_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  initialDelay: 1000, // 1 second
  maxDelay: 30000, // 30 seconds
  backoffMultiplier: 2,
  shouldRetry: (error: any) => {
    // Retry on network errors and specific status codes
    if (!error) {return false;}

    // Network errors
    if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
      return true;
    }

    // HTTP status codes that should be retried
    const retryableStatusCodes = [408, 429, 500, 502, 503, 504];
    if (error.status && retryableStatusCodes.includes(error.status)) {
      return true;
    }

    return false;
  },
  onRetry: () => {}, // No-op by default
};

/**
 * Execute a function with exponential backoff retry logic
 * @param fn Function to execute
 * @param options Retry options
 * @returns Promise with the function result
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const config = { ...DEFAULT_OPTIONS, ...options };
  let lastError: any;
  let delay = config.initialDelay;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if we should retry
      if (attempt === config.maxRetries || !config.shouldRetry(error, attempt)) {
        throw error;
      }

      // Calculate next delay with exponential backoff
      const nextDelay = Math.min(delay, config.maxDelay);

      // Add jitter to prevent thundering herd problem
      const jitter = Math.random() * 0.3 * nextDelay; // Up to 30% jitter
      const finalDelay = nextDelay + jitter;

      // Notify about retry
      config.onRetry(error, attempt + 1, finalDelay);

      // Wait before retrying
      await sleep(finalDelay);

      // Increase delay for next attempt
      delay *= config.backoffMultiplier;
    }
  }

  throw lastError;
}

/**
 * Execute a function with linear retry logic
 * @param fn Function to execute
 * @param maxRetries Maximum number of retries
 * @param delay Delay between retries in milliseconds
 * @returns Promise with the function result
 */
export async function retryLinear<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: any;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries) {
        await sleep(delay);
      }
    }
  }

  throw lastError;
}

/**
 * Create a retry wrapper for a function
 * @param fn Function to wrap
 * @param options Retry options
 * @returns Wrapped function with retry logic
 */
export function withRetry<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: RetryOptions = {}
): T {
  return (async (...args: Parameters<T>) => {
    return retryWithBackoff(() => fn(...args), options);
  }) as T;
}

/**
 * Retry with circuit breaker pattern
 */
export class CircuitBreaker {
  private failures = 0;
  private lastFailureTime = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  constructor(
    private readonly threshold: number = 5,
    private readonly timeout: number = 60000, // 1 minute
    private readonly resetTimeout: number = 30000 // 30 seconds
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Check if circuit is open
    if (this.state === 'open') {
      const now = Date.now();
      if (now - this.lastFailureTime > this.timeout) {
        this.state = 'half-open';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await fn();

      // Reset on success
      if (this.state === 'half-open') {
        this.reset();
      }

      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  private recordFailure() {
    this.failures++;
    this.lastFailureTime = Date.now();

    if (this.failures >= this.threshold) {
      this.state = 'open';

      // Schedule reset attempt
      setTimeout(() => {
        if (this.state === 'open') {
          this.state = 'half-open';
        }
      }, this.resetTimeout);
    }
  }

  private reset() {
    this.failures = 0;
    this.lastFailureTime = 0;
    this.state = 'closed';
  }

  getState() {
    return {
      state: this.state,
      failures: this.failures,
      lastFailureTime: this.lastFailureTime,
    };
  }
}

/**
 * Sleep utility
 * @param ms Milliseconds to sleep
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Debounce async function execution
 * @param fn Function to debounce
 * @param delay Debounce delay in milliseconds
 */
export function debounceAsync<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  delay: number
): T & { cancel: () => void } {
  let timeoutId: NodeJS.Timeout | null = null;
  let pending: Promise<any> | null = null;

  const debounced = (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    pending = new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await fn(...args);
          resolve(result);
        } catch (error) {
          reject(error);
        } finally {
          timeoutId = null;
          pending = null;
        }
      }, delay);
    });

    return pending;
  };

  debounced.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    pending = null;
  };

  return debounced as T & { cancel: () => void };
}
