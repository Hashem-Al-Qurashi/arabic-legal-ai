module.exports = {
  root: true,
  extends: ['@react-native'],
  env: {
    jest: true,
    node: true,
  },
  overrides: [
    {
      files: ['*.test.{js,jsx,ts,tsx}', '*.spec.{js,jsx,ts,tsx}', 'jest.setup.js', '__tests__/**/*'],
      env: {
        jest: true,
      },
      globals: {
        jest: 'readonly',
        expect: 'readonly',
        describe: 'readonly',
        it: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
      },
    },
  ],
};
