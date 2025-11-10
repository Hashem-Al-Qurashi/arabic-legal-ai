/**
 * Permission management utility for React Native
 * Handles permission requests across iOS and Android
 */

import { Platform, PermissionsAndroid, Linking, Alert } from 'react-native';
import { check, request, PERMISSIONS, RESULTS, Permission } from 'react-native-permissions';

export interface PermissionStatus {
  granted: boolean;
  blocked: boolean;
  unavailable: boolean;
}

/**
 * Permission types
 */
export enum PermissionType {
  Camera = 'camera',
  PhotoLibrary = 'photo_library',
  Microphone = 'microphone',
  Storage = 'storage',
  MediaLibrary = 'media_library',
}

/**
 * Get platform-specific permission
 */
function getPlatformPermission(type: PermissionType): Permission | null {
  if (Platform.OS === 'ios') {
    switch (type) {
      case PermissionType.Camera:
        return PERMISSIONS.IOS.CAMERA;
      case PermissionType.PhotoLibrary:
        return PERMISSIONS.IOS.PHOTO_LIBRARY;
      case PermissionType.Microphone:
        return PERMISSIONS.IOS.MICROPHONE;
      case PermissionType.MediaLibrary:
        return PERMISSIONS.IOS.MEDIA_LIBRARY;
      default:
        return null;
    }
  } else if (Platform.OS === 'android') {
    const androidVersion = Platform.Version;

    switch (type) {
      case PermissionType.Camera:
        return PERMISSIONS.ANDROID.CAMERA;
      case PermissionType.Microphone:
        return PERMISSIONS.ANDROID.RECORD_AUDIO;
      case PermissionType.Storage:
      case PermissionType.PhotoLibrary:
        if (androidVersion >= 33) {
          // Android 13+
          return PERMISSIONS.ANDROID.READ_MEDIA_IMAGES;
        } else if (androidVersion >= 29) {
          // Android 10-12
          return PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
        } else {
          // Android 9 and below
          return PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
        }
      case PermissionType.MediaLibrary:
        if (androidVersion >= 33) {
          return PERMISSIONS.ANDROID.READ_MEDIA_VIDEO;
        } else {
          return PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
        }
      default:
        return null;
    }
  }

  return null;
}

/**
 * Check permission status
 */
export async function checkPermission(type: PermissionType): Promise<PermissionStatus> {
  const permission = getPlatformPermission(type);

  if (!permission) {
    return { granted: true, blocked: false, unavailable: true };
  }

  try {
    const result = await check(permission);

    return {
      granted: result === RESULTS.GRANTED,
      blocked: result === RESULTS.BLOCKED,
      unavailable: result === RESULTS.UNAVAILABLE,
    };
  } catch (error) {
    console.error('Permission check error:', error);
    return { granted: false, blocked: false, unavailable: true };
  }
}

/**
 * Request permission
 */
export async function requestPermission(type: PermissionType): Promise<PermissionStatus> {
  const permission = getPlatformPermission(type);

  if (!permission) {
    return { granted: true, blocked: false, unavailable: true };
  }

  try {
    const result = await request(permission);

    return {
      granted: result === RESULTS.GRANTED,
      blocked: result === RESULTS.BLOCKED,
      unavailable: result === RESULTS.UNAVAILABLE,
    };
  } catch (error) {
    console.error('Permission request error:', error);
    return { granted: false, blocked: false, unavailable: true };
  }
}

/**
 * Request multiple permissions
 */
export async function requestMultiplePermissions(
  types: PermissionType[]
): Promise<Record<PermissionType, PermissionStatus>> {
  const results: Record<PermissionType, PermissionStatus> = {} as any;

  for (const type of types) {
    results[type] = await requestPermission(type);
  }

  return results;
}

/**
 * Show permission denied alert with settings option
 */
export function showPermissionDeniedAlert(
  permissionName: string,
  message?: string
): void {
  Alert.alert(
    'إذن مطلوب',
    message || `يحتاج التطبيق إلى إذن ${permissionName} للمتابعة. يمكنك تفعيله من الإعدادات.`,
    [
      {
        text: 'إلغاء',
        style: 'cancel',
      },
      {
        text: 'فتح الإعدادات',
        onPress: () => Linking.openSettings(),
      },
    ],
  );
}

/**
 * Request camera permission with proper handling
 */
export async function requestCameraPermission(): Promise<boolean> {
  const status = await requestPermission(PermissionType.Camera);

  if (status.granted) {
    return true;
  }

  if (status.blocked) {
    showPermissionDeniedAlert('الكاميرا', 'يحتاج التطبيق إلى الوصول للكاميرا لالتقاط صور المستندات.');
  }

  return false;
}

/**
 * Request storage permission with proper handling
 */
export async function requestStoragePermission(): Promise<boolean> {
  const status = await requestPermission(PermissionType.Storage);

  if (status.granted) {
    return true;
  }

  if (status.blocked) {
    showPermissionDeniedAlert('التخزين', 'يحتاج التطبيق إلى الوصول للملفات لاختيار المستندات.');
  }

  return false;
}

/**
 * Request all file upload permissions
 */
export async function requestFileUploadPermissions(): Promise<boolean> {
  const permissions = [
    PermissionType.Camera,
    PermissionType.PhotoLibrary,
    PermissionType.Storage,
  ];

  const results = await requestMultiplePermissions(permissions);

  // Check if at least storage or photo library is granted
  const hasBasicAccess =
    results[PermissionType.Storage]?.granted ||
    results[PermissionType.PhotoLibrary]?.granted;

  if (!hasBasicAccess) {
    showPermissionDeniedAlert(
      'الملفات والكاميرا',
      'يحتاج التطبيق إلى أذونات الوصول للملفات والكاميرا لإرفاق المستندات.'
    );
  }

  return hasBasicAccess;
}

/**
 * Android-specific permission request using PermissionsAndroid
 */
export async function requestAndroidPermission(
  permission: typeof PermissionsAndroid.PERMISSIONS[keyof typeof PermissionsAndroid.PERMISSIONS],
  title: string,
  message: string
): Promise<boolean> {
  if (Platform.OS !== 'android') {
    return true;
  }

  try {
    const granted = await PermissionsAndroid.request(permission, {
      title,
      message,
      buttonNeutral: 'اسأل لاحقاً',
      buttonNegative: 'إلغاء',
      buttonPositive: 'موافق',
    });

    return granted === PermissionsAndroid.RESULTS.GRANTED;
  } catch (error) {
    console.error('Android permission request error:', error);
    return false;
  }
}
