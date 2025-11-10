/**
 * Investigation test to understand error response structure
 */

import { authAPI } from '@/services/api';
import { server } from './mocks/server';

describe('Error Investigation', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  afterAll(() => {
    server.close();
  });

  test('should investigate error response structure', async () => {
    console.log('Starting error investigation...');

    try {
      const result = await authAPI.login({
        email: 'wrong@example.com',
        password: 'wrongpassword',
      });

      console.log('Error result full structure:', JSON.stringify(result, null, 2));

      expect(result.success).toBe(false);

    } catch (error: any) {
      console.log('Caught error:', error);
      console.log('Error response:', error.response?.data);
      console.log('Error message:', error.message);
    }
  });
});
