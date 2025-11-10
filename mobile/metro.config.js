const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');
const path = require('path');

/**
 * Metro configuration for Arabic Legal AI Mobile
 * Optimized for production performance, bundle size, and fast startup
 * https://reactnative.dev/docs/metro
 *
 * @type {import('@react-native/metro-config').MetroConfig}
 */
const config = {
  resolver: {
    // Add TypeScript support and path aliases
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/services': path.resolve(__dirname, 'src/services'),
      '@/types': path.resolve(__dirname, 'src/types'),
      '@/utils': path.resolve(__dirname, 'src/utils'),
      '@/contexts': path.resolve(__dirname, 'src/contexts'),
      '@/hooks': path.resolve(__dirname, 'src/hooks'),
      '@/styles': path.resolve(__dirname, 'src/styles'),
      '@/screens': path.resolve(__dirname, 'src/screens'),
      '@/navigation': path.resolve(__dirname, 'src/navigation'),
    },
    // Support for various file extensions
    sourceExts: ['jsx', 'js', 'ts', 'tsx', 'json', 'svg'],
    // Asset file extensions including Arabic fonts
    assetExts: [
      'ttf',
      'otf',
      'woff',
      'woff2',
      'eot',
      'png',
      'jpg',
      'jpeg',
      'gif',
      'webp',
      'pdf',
      'zip',
      'mp3',
      'mp4',
      'mov',
    ],
    // Block files to reduce bundle size
    blockList: [
      /.*\.test\.(js|jsx|ts|tsx)$/,
      /.*\/__tests__\/.*/,
      /.*\/__mocks__\/.*/,
      /.*\.spec\.(js|jsx|ts|tsx)$/,
      /.*\.stories\.(js|jsx|ts|tsx)$/,
      /.*\.(md|MD)$/,
      /.*\.(map)$/,
      /\.git\/.*/,
      /node_modules\/.*\/test\/.*/,
    ],
    // Node modules to transpile
    nodeModulesPaths: [],
    // Improve module resolution performance
    resolverMainFields: ['react-native', 'browser', 'main'],
    // Platform-specific extensions
    platforms: ['ios', 'android'],
  },
  transformer: {
    // Enable SVG support
    babelTransformerPath: require.resolve('react-native-svg-transformer'),
    // Get transformer options
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true, // Enable inline requires for better performance
      },
    }),
    // Optimize for production builds
    minifierPath: require.resolve('metro-minify-terser'),
    minifierConfig: {
      ecma: 8,
      keep_classnames: false,
      keep_fnames: false,
      module: true,
      mangle: {
        module: true,
        keep_classnames: false,
        keep_fnames: false,
        reserved: [], // Add reserved words if needed
      },
      compress: {
        // Enable all safe optimizations
        arrows: true,
        arguments: true,
        booleans: true,
        booleans_as_integers: true,
        collapse_vars: true,
        comparisons: true,
        computed_props: true,
        conditionals: true,
        dead_code: true,
        directives: true,
        drop_console: !__DEV__, // Remove console logs in production
        drop_debugger: true,
        ecma: 8,
        evaluate: true,
        expression: true,
        global_defs: {
          __DEV__: false, // Set to false for production
        },
        hoist_funs: true,
        hoist_props: true,
        hoist_vars: false,
        if_return: true,
        inline: true,
        join_vars: true,
        keep_infinity: false,
        loops: true,
        module: true,
        negate_iife: true,
        passes: 2, // Run compress twice for better optimization
        properties: true,
        pure_getters: true,
        pure_funcs: [
          'console.log',
          'console.info',
          'console.debug',
          'console.warn',
        ],
        reduce_funcs: true,
        reduce_vars: true,
        sequences: true,
        side_effects: true,
        switches: true,
        toplevel: false,
        typeofs: true,
        unused: true,
        warnings: false,
      },
      output: {
        ascii_only: true,
        comments: false,
        indent_level: 0,
        ecma: 8,
      },
    },
    // Asset plugins for optimization
    assetPlugins: [
      // Add asset optimization plugins here if needed
    ],
  },
  serializer: {
    // Create module ID factory for consistent hashing
    createModuleIdFactory: function () {
      const projectRoot = __dirname;
      return function (path) {
        let name = '';
        if (path.indexOf(projectRoot) === 0) {
          name = path.substr(projectRoot.length + 1);
        }
        return require('crypto').createHash('sha1').update(name).digest('hex');
      };
    },
    // Process module filter for excluding dev dependencies
    processModuleFilter: function (module) {
      if (module.path.indexOf('__tests__') >= 0) {
        return false;
      }
      if (module.path.indexOf('__mocks__') >= 0) {
        return false;
      }
      if (module.path.indexOf('.test.') >= 0) {
        return false;
      }
      if (module.path.indexOf('.spec.') >= 0) {
        return false;
      }
      return true;
    },
  },
  server: {
    // Improve server performance
    enhanceMiddleware: (middleware) => {
      return middleware;
    },
    // Use worker threads for better performance
    useGlobalHotkey: true,
    // Port configuration
    port: 8081,
  },
  // Watcher configuration for better performance
  watchFolders: [
    // Add any additional folders to watch
  ],
  // Reset cache on start for development
  resetCache: __DEV__,
  // Maximum number of workers
  maxWorkers: 4,
  // Cache configuration
  cacheVersion: '1.0.0',
  // Project root
  projectRoot: __dirname,
  // Transformer cache key
  transformerPath: require.resolve('metro-react-native-babel-transformer'),
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);