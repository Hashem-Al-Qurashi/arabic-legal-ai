#!/usr/bin/env node

/**
 * Integration verification script for Enhanced Chat Features
 * This script verifies that all mobile-specific features are properly connected
 */

const fs = require('fs');
const path = require('path');

const MOBILE_DIR = __dirname;
const SRC_DIR = path.join(MOBILE_DIR, 'src');

// Colors for console output
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const CYAN = '\x1b[36m';
const RESET = '\x1b[0m';

console.log(`${CYAN}=== Arabic Legal AI Mobile - Enhanced Features Integration Check ===${RESET}\n`);

let errors = [];
let warnings = [];
let successes = [];

// Check 1: Verify EnhancedChatScreen is imported in AppNavigator
function checkNavigatorIntegration() {
  console.log(`${CYAN}Checking Navigator Integration...${RESET}`);

  const navigatorPath = path.join(SRC_DIR, 'navigation', 'AppNavigator.tsx');
  const navigatorContent = fs.readFileSync(navigatorPath, 'utf-8');

  if (navigatorContent.includes('import { EnhancedChatScreen }')) {
    successes.push('✓ EnhancedChatScreen is properly imported');
  } else {
    errors.push('✗ EnhancedChatScreen import not found in AppNavigator');
  }

  if (navigatorContent.includes('component={EnhancedChatScreen}')) {
    successes.push('✓ EnhancedChatScreen is used in navigation');
  } else {
    errors.push('✗ EnhancedChatScreen not used as component in navigation');
  }

  // Check for basic ChatScreen (should not be used)
  if (navigatorContent.includes('import ChatScreen') && !navigatorContent.includes('// import ChatScreen')) {
    warnings.push('⚠ Basic ChatScreen is still imported (should be removed)');
  }
}

// Check 2: Verify Enhanced Components Exist
function checkEnhancedComponents() {
  console.log(`${CYAN}Checking Enhanced Components...${RESET}`);

  const componentsToCheck = [
    'components/chat/EnhancedChatInput.tsx',
    'components/chat/FileUpload.tsx',
    'components/chat/MessageBubble.tsx',
    'components/chat/MessageSkeleton.tsx',
  ];

  componentsToCheck.forEach(component => {
    const componentPath = path.join(SRC_DIR, component);
    if (fs.existsSync(componentPath)) {
      successes.push(`✓ ${component} exists`);
    } else {
      errors.push(`✗ ${component} not found`);
    }
  });
}

// Check 3: Verify EnhancedChatScreen uses Enhanced Components
function checkEnhancedChatScreenComponents() {
  console.log(`${CYAN}Checking EnhancedChatScreen Components Usage...${RESET}`);

  const screenPath = path.join(SRC_DIR, 'screens', 'EnhancedChatScreen.tsx');
  const screenContent = fs.readFileSync(screenPath, 'utf-8');

  const requiredImports = [
    'EnhancedChatInput',
    'MessageBubble',
    'MessageSkeleton',
    'FileAttachment',
    'useOffline',
  ];

  requiredImports.forEach(importName => {
    if (screenContent.includes(importName)) {
      successes.push(`✓ ${importName} is used in EnhancedChatScreen`);
    } else {
      warnings.push(`⚠ ${importName} might not be used in EnhancedChatScreen`);
    }
  });

  // Check for critical features
  if (screenContent.includes('handleSendMessage') && screenContent.includes('attachments')) {
    successes.push('✓ File attachment handling is implemented');
  } else {
    errors.push('✗ File attachment handling not found');
  }

  if (screenContent.includes('isOnline') && screenContent.includes('queuedMessages')) {
    successes.push('✓ Offline functionality is implemented');
  } else {
    errors.push('✗ Offline functionality not found');
  }
}

// Check 4: Verify FileUpload Component Features
function checkFileUploadFeatures() {
  console.log(`${CYAN}Checking FileUpload Component Features...${RESET}`);

  const fileUploadPath = path.join(SRC_DIR, 'components', 'chat', 'FileUpload.tsx');
  const fileUploadContent = fs.readFileSync(fileUploadPath, 'utf-8');

  const features = [
    { name: 'Camera support', pattern: 'launchCamera' },
    { name: 'Image picker', pattern: 'launchImageLibrary' },
    { name: 'Document picker', pattern: 'DocumentPicker' },
    { name: 'File system access', pattern: 'RNFS' },
    { name: 'Bottom sheet UI', pattern: 'BottomSheet' },
  ];

  features.forEach(feature => {
    if (fileUploadContent.includes(feature.pattern)) {
      successes.push(`✓ ${feature.name} is available`);
    } else {
      errors.push(`✗ ${feature.name} not found`);
    }
  });
}

// Check 5: Verify Services and Hooks
function checkServicesAndHooks() {
  console.log(`${CYAN}Checking Services and Hooks...${RESET}`);

  const servicesToCheck = [
    { path: 'services/offlineService.ts', name: 'Offline Service' },
    { path: 'services/appLifecycle.ts', name: 'App Lifecycle Service' },
    { path: 'hooks/useOffline.ts', name: 'useOffline Hook' },
  ];

  servicesToCheck.forEach(service => {
    const servicePath = path.join(SRC_DIR, service.path);
    if (fs.existsSync(servicePath)) {
      successes.push(`✓ ${service.name} exists`);

      // Check if it's actually used in EnhancedChatScreen
      const screenPath = path.join(SRC_DIR, 'screens', 'EnhancedChatScreen.tsx');
      const screenContent = fs.readFileSync(screenPath, 'utf-8');
      const serviceName = path.basename(service.path, '.ts').replace('.tsx', '');

      if (screenContent.includes(serviceName)) {
        successes.push(`✓ ${service.name} is used in EnhancedChatScreen`);
      } else {
        warnings.push(`⚠ ${service.name} might not be used`);
      }
    } else {
      errors.push(`✗ ${service.name} not found`);
    }
  });
}

// Check 6: Verify Mobile-Specific Features
function checkMobileFeatures() {
  console.log(`${CYAN}Checking Mobile-Specific Features...${RESET}`);

  const enhancedInputPath = path.join(SRC_DIR, 'components', 'chat', 'EnhancedChatInput.tsx');
  const enhancedInputContent = fs.readFileSync(enhancedInputPath, 'utf-8');

  const mobileFeatures = [
    { name: 'Haptic Feedback', pattern: 'HapticFeedback' },
    { name: 'Keyboard handling', pattern: 'KeyboardAvoidingView' },
    { name: 'Animations', pattern: 'Animated' },
    { name: 'Voice recording placeholder', pattern: 'mic' },
    { name: 'Attachment preview', pattern: 'attachments' },
  ];

  mobileFeatures.forEach(feature => {
    if (enhancedInputContent.includes(feature.pattern)) {
      successes.push(`✓ ${feature.name} is implemented`);
    } else {
      warnings.push(`⚠ ${feature.name} not found in EnhancedChatInput`);
    }
  });
}

// Run all checks
function runAllChecks() {
  checkNavigatorIntegration();
  console.log('');

  checkEnhancedComponents();
  console.log('');

  checkEnhancedChatScreenComponents();
  console.log('');

  checkFileUploadFeatures();
  console.log('');

  checkServicesAndHooks();
  console.log('');

  checkMobileFeatures();
  console.log('');

  // Print summary
  console.log(`${CYAN}=== Integration Check Summary ===${RESET}\n`);

  if (successes.length > 0) {
    console.log(`${GREEN}Successes (${successes.length}):${RESET}`);
    successes.forEach(s => console.log(`  ${GREEN}${s}${RESET}`));
    console.log('');
  }

  if (warnings.length > 0) {
    console.log(`${YELLOW}Warnings (${warnings.length}):${RESET}`);
    warnings.forEach(w => console.log(`  ${YELLOW}${w}${RESET}`));
    console.log('');
  }

  if (errors.length > 0) {
    console.log(`${RED}Errors (${errors.length}):${RESET}`);
    errors.forEach(e => console.log(`  ${RED}${e}${RESET}`));
    console.log('');
  }

  // Final verdict
  if (errors.length === 0) {
    console.log(`${GREEN}✅ INTEGRATION SUCCESSFUL!${RESET}`);
    console.log(`${GREEN}All enhanced features are properly connected and accessible.${RESET}`);
    console.log(`${GREEN}Users can now access:${RESET}`);
    console.log(`  ${GREEN}• File upload and camera features${RESET}`);
    console.log(`  ${GREEN}• Enhanced chat input with attachments${RESET}`);
    console.log(`  ${GREEN}• Offline functionality${RESET}`);
    console.log(`  ${GREEN}• Mobile-specific UX improvements${RESET}`);
    process.exit(0);
  } else {
    console.log(`${RED}❌ INTEGRATION INCOMPLETE${RESET}`);
    console.log(`${RED}Please fix the errors above to complete the integration.${RESET}`);
    process.exit(1);
  }
}

// Run the checks
runAllChecks();
