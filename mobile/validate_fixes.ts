#!/usr/bin/env npx ts-node

/**
 * COMPREHENSIVE VALIDATION SCRIPT FOR CHAT IMPLEMENTATION FIXES
 * =============================================================
 *
 * This script validates all claimed fixes:
 * 1. TypeScript compilation
 * 2. Performance (useCallback memoization)
 * 3. Memory leaks (AbortController, cleanup)
 * 4. Import/type resolution
 * 5. Code quality and React best practices
 */

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

interface ValidationResult {
  test: string;
  passed: boolean;
  details: string[];
  criticalIssues: string[];
}

class ChatImplementationValidator {
  private results: ValidationResult[] = [];
  private projectRoot: string;

  constructor(projectRoot: string) {
    this.projectRoot = projectRoot;
  }

  /**
   * 1. TEST TYPESCRIPT COMPILATION
   */
  async testTypeScriptCompilation(): Promise<ValidationResult> {
    const result: ValidationResult = {
      test: 'TypeScript Compilation',
      passed: false,
      details: [],
      criticalIssues: [],
    };

    try {
      // Run TypeScript compilation
      const output = execSync('npx tsc --noEmit --pretty false', {
        cwd: this.projectRoot,
        encoding: 'utf8',
        stdio: 'pipe',
      });

      if (output.trim() === '') {
        result.passed = true;
        result.details.push('✅ TypeScript compilation successful with no errors');
      } else {
        result.details.push(`⚠️ TypeScript warnings: ${output}`);
      }
    } catch (error: any) {
      result.passed = false;
      result.criticalIssues.push('❌ TypeScript compilation FAILED');
      result.criticalIssues.push(`Error output: ${error.stdout || error.message}`);

      // Parse errors to count them
      const errorCount = (error.stdout || '').split('\n').filter((line: string) =>
        line.includes('error TS')
      ).length;

      result.criticalIssues.push(`Total TypeScript errors: ${errorCount}`);
    }

    return result;
  }

  /**
   * 2. ANALYZE USECALLBACK MEMOIZATION
   */
  async analyzePerformanceOptimizations(): Promise<ValidationResult> {
    const result: ValidationResult = {
      test: 'Performance Optimizations (useCallback)',
      passed: false,
      details: [],
      criticalIssues: [],
    };

    const chatScreenPath = join(this.projectRoot, 'src/screens/ChatScreen.tsx');

    if (!existsSync(chatScreenPath)) {
      result.criticalIssues.push('❌ ChatScreen.tsx not found');
      return result;
    }

    const content = readFileSync(chatScreenPath, 'utf8');

    // Check for useCallback usage
    const useCallbackMatches = content.match(/useCallback\(/g);
    const callbackCount = useCallbackMatches ? useCallbackMatches.length : 0;

    result.details.push(`Found ${callbackCount} useCallback implementations`);

    // Check critical functions that should be memoized
    const criticalFunctions = [
      'handleSendMessage',
      'renderMessage',
      'renderEmptyState',
      'renderLoadingIndicator',
      'renderHeader',
      'handleSuggestedQuestion',
      'startNewConversation',
    ];

    const unmemoizedFunctions: string[] = [];

    criticalFunctions.forEach(funcName => {
      // Check if function is wrapped in useCallback
      const funcRegex = new RegExp(`const\\s+${funcName}\\s*=\\s*useCallback\\(`, 'g');
      if (funcRegex.test(content)) {
        result.details.push(`✅ ${funcName} is properly memoized`);
      } else {
        unmemoizedFunctions.push(funcName);
        result.criticalIssues.push(`❌ ${funcName} is NOT memoized - performance issue`);
      }
    });

    if (unmemoizedFunctions.length === 0) {
      result.passed = true;
      result.details.push('✅ All critical functions are properly memoized');
    } else {
      result.criticalIssues.push(`${unmemoizedFunctions.length} critical functions not memoized`);
    }

    return result;
  }

  /**
   * 3. VERIFY MEMORY LEAK PREVENTION
   */
  async verifyMemoryLeakPrevention(): Promise<ValidationResult> {
    const result: ValidationResult = {
      test: 'Memory Leak Prevention',
      passed: false,
      details: [],
      criticalIssues: [],
    };

    const chatScreenPath = join(this.projectRoot, 'src/screens/ChatScreen.tsx');
    const apiPath = join(this.projectRoot, 'src/services/api.ts');

    if (!existsSync(chatScreenPath) || !existsSync(apiPath)) {
      result.criticalIssues.push('❌ Required files not found');
      return result;
    }

    const chatContent = readFileSync(chatScreenPath, 'utf8');
    const apiContent = readFileSync(apiPath, 'utf8');

    // Check for AbortController usage
    if (chatContent.includes('AbortController') && chatContent.includes('messageAbortController')) {
      result.details.push('✅ AbortController found in ChatScreen');
    } else {
      result.criticalIssues.push('❌ AbortController not properly implemented in ChatScreen');
    }

    // Check for cleanup in useEffect
    const cleanupPatterns = [
      'return () => {',
      'isCancelled = true',
      'abort()',
      'cancel()',
    ];

    let cleanupCount = 0;
    cleanupPatterns.forEach(pattern => {
      if (chatContent.includes(pattern)) {
        cleanupCount++;
      }
    });

    if (cleanupCount >= 3) {
      result.details.push('✅ Proper cleanup patterns found in useEffect hooks');
    } else {
      result.criticalIssues.push('❌ Insufficient cleanup patterns in useEffect hooks');
    }

    // Check AbortSignal in API
    if (apiContent.includes('abortSignal') && apiContent.includes('signal:')) {
      result.details.push('✅ AbortSignal properly passed to fetch requests');
    } else {
      result.criticalIssues.push('❌ AbortSignal not properly implemented in API');
    }

    // Check for proper stream cleanup
    if (apiContent.includes('reader.cancel()')) {
      result.details.push('✅ Stream reader properly cancelled on abort');
    } else {
      result.criticalIssues.push('❌ Stream reader not properly cancelled');
    }

    result.passed = result.criticalIssues.length === 0;
    return result;
  }

  /**
   * 4. CHECK IMPORT RESOLUTION AND TYPE DEFINITIONS
   */
  async checkImportResolution(): Promise<ValidationResult> {
    const result: ValidationResult = {
      test: 'Import Resolution & Type Definitions',
      passed: false,
      details: [],
      criticalIssues: [],
    };

    // Check tsconfig.json paths
    const tsconfigPath = join(this.projectRoot, 'tsconfig.json');
    if (!existsSync(tsconfigPath)) {
      result.criticalIssues.push('❌ tsconfig.json not found');
      return result;
    }

    const tsconfig = JSON.parse(readFileSync(tsconfigPath, 'utf8'));

    if (tsconfig.compilerOptions?.paths) {
      result.details.push('✅ Path mappings configured in tsconfig.json');

      // Check critical path mappings
      const requiredPaths = ['@/*', '@/components/*', '@/types', '@/services/*'];
      let missingPaths: string[] = [];

      requiredPaths.forEach(path => {
        if (!tsconfig.compilerOptions.paths[path]) {
          missingPaths.push(path);
        }
      });

      if (missingPaths.length === 0) {
        result.details.push('✅ All required path mappings present');
      } else {
        result.criticalIssues.push(`❌ Missing path mappings: ${missingPaths.join(', ')}`);
      }
    } else {
      result.criticalIssues.push('❌ No path mappings configured');
    }

    // Check types/index.ts
    const typesPath = join(this.projectRoot, 'src/types/index.ts');
    if (existsSync(typesPath)) {
      const typesContent = readFileSync(typesPath, 'utf8');

      // Check for essential types
      const requiredTypes = ['Message', 'Conversation', 'User', 'ApiResponse'];
      let missingTypes: string[] = [];

      requiredTypes.forEach(type => {
        if (!typesContent.includes(`interface ${type}`) && !typesContent.includes(`type ${type}`)) {
          missingTypes.push(type);
        }
      });

      if (missingTypes.length === 0) {
        result.details.push('✅ All essential types defined');
      } else {
        result.criticalIssues.push(`❌ Missing type definitions: ${missingTypes.join(', ')}`);
      }
    } else {
      result.criticalIssues.push('❌ types/index.ts not found');
    }

    result.passed = result.criticalIssues.length === 0;
    return result;
  }

  /**
   * 5. VALIDATE REACT BEST PRACTICES
   */
  async validateReactBestPractices(): Promise<ValidationResult> {
    const result: ValidationResult = {
      test: 'React Best Practices',
      passed: false,
      details: [],
      criticalIssues: [],
    };

    const files = [
      'src/screens/ChatScreen.tsx',
      'src/components/chat/ChatInput.tsx',
      'src/components/chat/MessageBubble.tsx',
      'src/contexts/ThemeContext.tsx',
    ];

    let totalIssues = 0;

    for (const file of files) {
      const filePath = join(this.projectRoot, file);
      if (!existsSync(filePath)) {
        result.criticalIssues.push(`❌ File not found: ${file}`);
        continue;
      }

      const content = readFileSync(filePath, 'utf8');

      // Check for React.JSX.Element return type
      if (content.includes('React.JSX.Element')) {
        result.details.push(`✅ ${file}: Proper JSX return type`);
      } else {
        result.criticalIssues.push(`❌ ${file}: Missing React.JSX.Element return type`);
        totalIssues++;
      }

      // Check for key props in lists
      if (content.includes('.map(') && !content.includes('key=')) {
        result.criticalIssues.push(`❌ ${file}: Map without key prop`);
        totalIssues++;
      }

      // Check for proper prop typing
      if (!content.includes('interface') && content.includes('Props')) {
        result.criticalIssues.push(`❌ ${file}: Props not properly typed`);
        totalIssues++;
      }
    }

    result.passed = totalIssues === 0;
    if (result.passed) {
      result.details.push('✅ All React best practices followed');
    }

    return result;
  }

  /**
   * 6. CHECK FOR NEW BUGS OR REGRESSIONS
   */
  async checkForRegressions(): Promise<ValidationResult> {
    const result: ValidationResult = {
      test: 'Regression Analysis',
      passed: false,
      details: [],
      criticalIssues: [],
    };

    // Run linting to catch potential issues
    try {
      const lintOutput = execSync('npx eslint src/ --format=compact', {
        cwd: this.projectRoot,
        encoding: 'utf8',
        stdio: 'pipe',
      });

      if (lintOutput.trim() === '') {
        result.details.push('✅ No linting errors found');
      } else {
        const errorCount = lintOutput.split('\n').filter(line =>
          line.includes('error') || line.includes('warning')
        ).length;
        result.details.push(`⚠️ ${errorCount} linting issues found`);
      }
    } catch (error: any) {
      result.criticalIssues.push('❌ Linting failed or found critical errors');
      result.criticalIssues.push(`Lint errors: ${error.stdout || error.message}`);
    }

    // Check for common anti-patterns
    const chatScreenPath = join(this.projectRoot, 'src/screens/ChatScreen.tsx');
    if (existsSync(chatScreenPath)) {
      const content = readFileSync(chatScreenPath, 'utf8');

      // Check for infinite re-render risks
      if (content.includes('useEffect(') && !content.includes('dependencies')) {
        result.criticalIssues.push('❌ useEffect without dependency array - infinite re-render risk');
      }

      // Check for state mutations
      if (content.includes('.push(') || content.includes('.pop(') || content.includes('.splice(')) {
        result.criticalIssues.push('❌ Direct state mutations detected');
      }
    }

    result.passed = result.criticalIssues.length === 0;
    return result;
  }

  /**
   * RUN ALL VALIDATIONS
   */
  async validateAll(): Promise<void> {
    console.log('🔍 STARTING COMPREHENSIVE CHAT IMPLEMENTATION VALIDATION');
    console.log('===========================================================\n');

    const tests = [
      () => this.testTypeScriptCompilation(),
      () => this.analyzePerformanceOptimizations(),
      () => this.verifyMemoryLeakPrevention(),
      () => this.checkImportResolution(),
      () => this.validateReactBestPractices(),
      () => this.checkForRegressions(),
    ];

    for (const test of tests) {
      const result = await test();
      this.results.push(result);
      this.printResult(result);
    }

    this.printSummary();
  }

  private printResult(result: ValidationResult): void {
    const status = result.passed ? '✅ PASSED' : '❌ FAILED';
    console.log(`\n${status}: ${result.test}`);
    console.log('─'.repeat(50));

    if (result.details.length > 0) {
      console.log('Details:');
      result.details.forEach(detail => console.log(`  ${detail}`));
    }

    if (result.criticalIssues.length > 0) {
      console.log('\nCRITICAL ISSUES:');
      result.criticalIssues.forEach(issue => console.log(`  ${issue}`));
    }
  }

  private printSummary(): void {
    console.log('\n\n🎯 VALIDATION SUMMARY');
    console.log('======================');

    const passed = this.results.filter(r => r.passed).length;
    const total = this.results.length;
    const criticalIssues = this.results.reduce((acc, r) => acc + r.criticalIssues.length, 0);

    console.log(`Tests Passed: ${passed}/${total}`);
    console.log(`Critical Issues: ${criticalIssues}`);

    if (passed === total && criticalIssues === 0) {
      console.log('\n🎉 ALL VALIDATIONS PASSED - IMPLEMENTATION IS READY!');
    } else {
      console.log('\n⚠️  IMPLEMENTATION IS NOT READY FOR PRODUCTION');
      console.log('\nFAILED TESTS:');
      this.results.filter(r => !r.passed).forEach(r => {
        console.log(`  ❌ ${r.test}`);
      });

      if (criticalIssues > 0) {
        console.log('\nALL CRITICAL ISSUES MUST BE FIXED BEFORE PROCEEDING');
      }
    }
  }
}

// Run validation if called directly
if (require.main === module) {
  const validator = new ChatImplementationValidator(process.cwd());
  validator.validateAll().catch(console.error);
}

export { ChatImplementationValidator };
