module.exports = {
  presets: ['module:@react-native/babel-preset'],
  plugins: [
    [
      'module-resolver',
      {
        root: ['./src'],
        alias: {
          '@': './src',
          '@/components': './src/components',
          '@/services': './src/services',
          '@/types': './src/types',
          '@/utils': './src/utils',
          '@/contexts': './src/contexts',
          '@/hooks': './src/hooks',
          '@/styles': './src/styles',
          '@/screens': './src/screens',
          '@/navigation': './src/navigation',
        },
      },
    ],
    'react-native-reanimated/plugin', // Must be last
  ],
};
