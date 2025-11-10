/**
 * Debug test to verify MSW is working
 */

import { authAPI } from '@/services/api';
import { server } from './mocks/server';

describe('Debug API Tests', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  afterAll(() => {
    server.close();
  });

  test('should make API call and get intercepted by MSW', async () => {
    console.log('Starting API call test...');

    const result = await authAPI.login({
      email: 'wrong@example.com',
      password: 'wrongpassword',
    });

    console.log('API call result:', result);

    expect(result).toBeDefined();
    expect(result.success).toBe(false);
    expect(result.error).toBe('Invalid credentials');
  });

  test('should make successful API call', async () => {
    console.log('Starting successful API call test...');

    const result = await authAPI.login({
      email: 'test@example.com',
      password: 'password123',
    });

    console.log('Successful API call result:', result);

    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
  });
});
