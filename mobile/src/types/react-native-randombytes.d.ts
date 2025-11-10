declare module 'react-native-randombytes' {
  export function randomBytes(
    size: number,
    callback: (error: Error | null, bytes: Buffer) => void
  ): void;

  export function randomBytesAsync(size: number): Promise<Buffer>;
}
