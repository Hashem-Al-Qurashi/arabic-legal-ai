/**
 * @format
 */

import React from 'react';
import ReactTestRenderer from 'react-test-renderer';
import { Text } from 'react-native';
import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
  useInfiniteQuery,
} from '@tanstack/react-query';

// Test component using React Query hooks
function TestQueryComponent() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['test'],
    queryFn: () => Promise.resolve({ message: 'Hello World' }),
  });

  useMutation({
    mutationFn: (data: any) => Promise.resolve(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['test'] });
    },
  });

  useInfiniteQuery({
    queryKey: ['infinite'],
    queryFn: ({ pageParam = 0 }) => Promise.resolve({
      data: [`Item ${pageParam}`],
      nextCursor: (pageParam as number) + 1,
    }),
    initialPageParam: 0,
    getNextPageParam: (lastPage: any) => lastPage.nextCursor,
  });

  return (
    <Text>
      {isLoading ? 'Loading...' : data?.message || 'No data'}
    </Text>
  );
}

describe('TanStack React Query Mocks', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient();
  });

  test('QueryClient is properly mocked', () => {
    expect(queryClient).toBeDefined();
    expect(queryClient.getQueryData).toBeDefined();
    expect(queryClient.setQueryData).toBeDefined();
    expect(queryClient.invalidateQueries).toBeDefined();

    // All methods should be mocked functions
    expect(jest.isMockFunction(queryClient.getQueryData)).toBe(true);
    expect(jest.isMockFunction(queryClient.invalidateQueries)).toBe(true);
  });

  test('useQuery returns mocked successful state', () => {
    const result = useQuery({
      queryKey: ['test'],
      queryFn: () => Promise.resolve('data'),
    });

    expect(result).toEqual({
      data: undefined,
      error: null,
      isLoading: false,
      isError: false,
      isSuccess: true,
      refetch: expect.any(Function),
    });
  });

  test('useMutation returns mocked state', () => {
    const result = useMutation({
      mutationFn: (data: any) => Promise.resolve(data),
    });

    expect(result).toEqual({
      mutate: expect.any(Function),
      mutateAsync: expect.any(Function),
      isLoading: false,
      isError: false,
      isSuccess: false,
      data: undefined,
      error: null,
      reset: expect.any(Function),
    });
  });

  test('useInfiniteQuery returns mocked state', () => {
    const result = useInfiniteQuery({
      queryKey: ['infinite'],
      queryFn: ({ pageParam = 0 }) => Promise.resolve({ data: pageParam }),
      initialPageParam: 0,
      getNextPageParam: () => undefined,
    });

    expect(result).toEqual({
      data: { pages: [], pageParams: [] },
      error: null,
      isLoading: false,
      isError: false,
      isSuccess: true,
      fetchNextPage: expect.any(Function),
      fetchPreviousPage: expect.any(Function),
      hasNextPage: false,
      hasPreviousPage: false,
      isFetchingNextPage: false,
      isFetchingPreviousPage: false,
    });
  });

  test('QueryClientProvider wrapper works', () => {
    const TestWrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const component = ReactTestRenderer.create(
      <TestWrapper>
        <Text>Test</Text>
      </TestWrapper>
    );

    expect(component).toBeDefined();
    const text = component.root.findByType('Text' as any);
    expect(text.children).toContain('Test');
  });

  test('Component with React Query hooks renders', () => {
    const component = ReactTestRenderer.create(
      <QueryClientProvider client={queryClient}>
        <TestQueryComponent />
      </QueryClientProvider>
    );

    expect(component).toBeDefined();

    const text = component.root.findByType('Text' as any);
    // With mocked hooks, isLoading is false and data is undefined
    expect(text.children).toContain('No data');
  });

  test('[LIMITATION] Cannot test actual data fetching', () => {
    // This documents that we cannot test:
    // - Actual API calls and responses
    // - Loading states during real requests
    // - Error handling from failed requests
    // - Cache invalidation and refetching
    // - Background refetching
    // - Optimistic updates

    const mockQueryFn = jest.fn(() => Promise.resolve('real data'));

    const result = useQuery({
      queryKey: ['test'],
      queryFn: mockQueryFn,
    });

    // The queryFn is never actually called due to mocking
    expect(mockQueryFn).not.toHaveBeenCalled();

    // We only get the static mocked response
    expect(result.data).toBeUndefined();
    expect(result.isLoading).toBe(false);
    expect(result.isSuccess).toBe(true);
  });

  test('[LIMITATION] Cannot test cache behavior', () => {
    // This documents that we cannot test:
    // - Query deduplication
    // - Cache persistence
    // - Stale-while-revalidate behavior
    // - Cache time and garbage collection
    // - Query invalidation effects

    const queryClient = useQueryClient();

    // These methods are mocked and don't actually affect cache
    queryClient.setQueryData(['test'], 'cached data');
    queryClient.invalidateQueries({ queryKey: ['test'] });

    // We can only verify the methods were called, not the cache effects
    expect(queryClient.setQueryData).toHaveBeenCalled();
    expect(queryClient.invalidateQueries).toHaveBeenCalled();
  });

  test('[LIMITATION] Cannot test mutation side effects', () => {
    // This documents that we cannot test:
    // - Mutation success/error callbacks
    // - Optimistic updates
    // - Cache updates after mutations
    // - Multiple mutations coordination

    const onSuccess = jest.fn();
    const onError = jest.fn();

    const result = useMutation({
      mutationFn: (data: any) => Promise.resolve(data),
      onSuccess,
      onError,
    });

    // The callbacks are never called due to mocking
    expect(onSuccess).not.toHaveBeenCalled();
    expect(onError).not.toHaveBeenCalled();

    // We only get the static mocked state
    expect(result.isSuccess).toBe(false);
    expect(result.isError).toBe(false);
  });
});
