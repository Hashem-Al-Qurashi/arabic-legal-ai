/**
 * Debug test to check URL generation and MSW interception
 */

import { Platform } from 'react-native';
import { authAPI } from '@/services/api';
import { server } from './mocks/server';
import { http, HttpResponse } from 'msw';

describe('Debug URL Tests', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  afterAll(() => {
    server.close();
  });

  test('should show platform and __DEV__ values', () => {
    console.log('Platform.OS:', Platform.OS);
    console.log('__DEV__:', __DEV__);
  });

  test('should intercept axios calls properly', async () => {
    // Add a handler that logs all requests
    server.use(
      http.all('*', ({ request }) => {
        console.log('MSW intercepted request:', request.method, request.url);
        return undefined;
      })
    );

    console.log('About to make login call...');

    try {
      const result = await authAPI.login({
        email: 'test@example.com',
        password: 'password123',
      });
      console.log('Login result:', result);
    } catch (error) {
      console.log('Login error:', error);
    }
  });

  test('should use MSW handlers for login', async () => {
    console.log('Testing with working MSW handlers...');

    try {
      const result = await authAPI.login({
        email: 'test@example.com',
        password: 'password123',
      });
      console.log('Login with valid credentials:', result);

      const failResult = await authAPI.login({
        email: 'wrong@example.com',
        password: 'wrongpassword',
      });
      console.log('Login with invalid credentials:', failResult);
    } catch (error) {
      console.log('Login error:', error);
    }
  });

  test('should test direct fetch call', async () => {
    server.use(
      http.post('http://localhost:8000/api/auth/login', ({ request }) => {
        console.log('MSW: Direct fetch intercepted!', request.url);
        return HttpResponse.json({ test: 'from MSW' });
      })
    );

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test', password: 'test' }),
      });
      const data = await response.json();
      console.log('Direct fetch result:', data);
    } catch (error) {
      console.log('Direct fetch error:', error);
    }
  });
});
