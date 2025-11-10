/**
 * UUID generation utility for React Native
 * Provides secure, collision-resistant unique identifiers
 */

import { randomBytes } from 'react-native-randombytes';

/**
 * Generate a cryptographically secure UUID v4
 * @returns Promise<string> UUID in standard format
 */
export async function generateSecureUUID(): Promise<string> {
  return new Promise((resolve, reject) => {
    randomBytes(16, (error: Error | null, bytes: Buffer) => {
      if (error) {
        reject(error);
        return;
      }

      // Set version (4) and variant bits according to UUID v4 spec
      bytes[6] = (bytes[6] & 0x0f) | 0x40;
      bytes[8] = (bytes[8] & 0x3f) | 0x80;

      // Format as UUID string
      const hex = bytes.toString('hex');
      const uuid = [
        hex.slice(0, 8),
        hex.slice(8, 12),
        hex.slice(12, 16),
        hex.slice(16, 20),
        hex.slice(20, 32),
      ].join('-');

      resolve(uuid);
    });
  });
}

/**
 * Generate a synchronous UUID v4 (less secure, use only when async not possible)
 * @returns string UUID in standard format
 */
export function generateUUID(): string {
  // Fallback to timestamp + random for synchronous generation
  // Less secure but better than Date.now() + Math.random()
  const timestamp = Date.now();
  const random1 = Math.random() * 0xffffffff | 0;
  const random2 = Math.random() * 0xffffffff | 0;
  const random3 = Math.random() * 0xffffffff | 0;
  const random4 = Math.random() * 0xffffffff | 0;

  const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c, index) => {
    let r: number;
    if (index < 8) {
      r = (timestamp >> (index * 4)) & 0xf;
    } else if (index < 16) {
      r = (random1 >> ((index - 8) * 4)) & 0xf;
    } else if (index < 24) {
      r = (random2 >> ((index - 16) * 4)) & 0xf;
    } else if (index < 32) {
      r = (random3 >> ((index - 24) * 4)) & 0xf;
    } else {
      r = (random4 >> ((index - 32) * 4)) & 0xf;
    }

    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });

  return uuid;
}

/**
 * Generate a short ID suitable for temporary identifiers
 * @param length Length of the ID (default: 12)
 * @returns string Short random ID
 */
export function generateShortId(length: number = 12): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';

  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
}

/**
 * Generate a timestamp-based ID with random suffix
 * Useful for sorting by creation time
 * @returns string Timestamp-based ID
 */
export function generateTimestampId(): string {
  const timestamp = Date.now().toString(36);
  const randomSuffix = Math.random().toString(36).substr(2, 9);
  return `${timestamp}-${randomSuffix}`;
}

/**
 * Validate if a string is a valid UUID v4
 * @param uuid String to validate
 * @returns boolean True if valid UUID v4
 */
export function isValidUUID(uuid: string): boolean {
  const uuidV4Regex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidV4Regex.test(uuid);
}
