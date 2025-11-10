import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  Alert,
  ActivityIndicator,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import DocumentPicker from 'react-native-document-picker';
import {
  launchImageLibrary,
  launchCamera,
  ImagePickerResponse,
} from 'react-native-image-picker';
import RNFS from 'react-native-fs';
import BottomSheet from 'react-native-bottom-sheet';
import Icon from 'react-native-vector-icons/MaterialIcons';
import HapticFeedback from 'react-native-haptic-feedback';
import { useTheme } from '@/contexts/ThemeContext';
import { generateUUID, generateSecureUUID } from '@/utils/uuid';
import { storageQuota } from '@/utils/storageQuota';
import type { FileAttachment } from '@/types';

// Type definition for ImagePicker options
type PhotoQuality = 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1;

interface CameraOptions {
  mediaType: 'photo' | 'video' | 'mixed';
  includeBase64?: boolean;
  maxHeight?: number;
  maxWidth?: number;
  quality?: PhotoQuality;
}

interface ImageLibraryOptions extends CameraOptions {
  selectionLimit?: number;
}

interface FileUploadProps {
  onFilesSelected: (files: FileAttachment[]) => void;
  onUploadStart?: () => void;
  onUploadComplete?: () => void;
  maxFiles?: number;
  maxSizeBytes?: number;
  acceptedTypes?: string[];
  disabled?: boolean;
}

export function FileUpload({
  onFilesSelected,
  onUploadStart,
  onUploadComplete,
  maxFiles = 5,
  maxSizeBytes = 10 * 1024 * 1024, // 10MB default
  acceptedTypes = ['image/*', 'application/pdf', 'text/*'],
  disabled = false,
}: FileUploadProps): React.JSX.Element {
  const { colors } = useTheme();
  const [selectedFiles, setSelectedFiles] = useState<FileAttachment[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalFileSize, setTotalFileSize] = useState(0);
  const bottomSheetRef = useRef<BottomSheet>(null);
  const processingAbortController = useRef<AbortController | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cancel any ongoing processing
      if (processingAbortController.current) {
        processingAbortController.current.abort();
      }

      // Clean up temporary files
      selectedFiles.forEach(file => {
        cleanupTempFile(file.uri);
      });
    };
  }, []);

  // Cleanup temporary file
  const cleanupTempFile = async (uri: string) => {
    try {
      if (uri && uri.startsWith('file://')) {
        const exists = await RNFS.exists(uri);
        if (exists) {
          await RNFS.unlink(uri);
        }
      }
    } catch (error) {
      console.warn('Failed to cleanup temp file:', error);
    }
  };

  // Request permissions for Android
  const requestAndroidPermissions = async (): Promise<boolean> => {
    if (Platform.OS !== 'android') {return true;}

    try {
      const cameraPermission = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.CAMERA,
        {
          title: 'إذن الكاميرا',
          message: 'يحتاج التطبيق إلى الوصول للكاميرا لالتقاط صور المستندات',
          buttonNeutral: 'اسأل لاحقاً',
          buttonNegative: 'إلغاء',
          buttonPositive: 'موافق',
        },
      );

      const storagePermission = Platform.Version >= 33
        ? await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.READ_MEDIA_IMAGES,
            {
              title: 'إذن الوصول للملفات',
              message: 'يحتاج التطبيق إلى الوصول للملفات لاختيار المستندات',
              buttonNeutral: 'اسأل لاحقاً',
              buttonNegative: 'إلغاء',
              buttonPositive: 'موافق',
            },
          )
        : await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
            {
              title: 'إذن الوصول للملفات',
              message: 'يحتاج التطبيق إلى الوصول للملفات لاختيار المستندات',
              buttonNeutral: 'اسأل لاحقاً',
              buttonNegative: 'إلغاء',
              buttonPositive: 'موافق',
            },
          );

      return (
        cameraPermission === PermissionsAndroid.RESULTS.GRANTED &&
        storagePermission === PermissionsAndroid.RESULTS.GRANTED
      );
    } catch (error) {
      console.error('Permission request error:', error);
      return false;
    }
  };

  // Handle document picker
  const handleDocumentPicker = async () => {
    try {
      HapticFeedback.trigger('impactLight');

      const results = await DocumentPicker.pick({
        type: acceptedTypes.includes('*/*')
          ? [DocumentPicker.types.allFiles]
          : acceptedTypes.map(type => {
              if (type === 'image/*') {return DocumentPicker.types.images;}
              if (type === 'application/pdf') {return DocumentPicker.types.pdf;}
              if (type === 'text/*') {return DocumentPicker.types.plainText;}
              return DocumentPicker.types.allFiles;
            }),
        allowMultiSelection: maxFiles > 1,
      });

      await processSelectedFiles(results);
    } catch (err) {
      if (!DocumentPicker.isCancel(err)) {
        console.error('Document picker error:', err);
        Alert.alert('خطأ', 'فشل في اختيار الملف');
      }
    }
  };

  // Handle camera capture
  const handleCamera = async () => {
    try {
      HapticFeedback.trigger('impactLight');

      // Request permissions first
      const hasPermissions = await requestAndroidPermissions();
      if (!hasPermissions) {
        Alert.alert('الأذونات مطلوبة', 'يحتاج التطبيق إلى أذونات الكاميرا والتخزين');
        return;
      }

      const options: CameraOptions = {
        mediaType: 'photo',
        includeBase64: false,
        maxHeight: 2000,
        maxWidth: 2000,
        quality: 0.8 as PhotoQuality,
      };

      launchCamera(options, async (response: ImagePickerResponse) => {
        if (response.didCancel || response.errorCode) {
          if (response.errorCode === 'permission') {
            Alert.alert('إذن مرفوض', 'يرجى السماح بالوصول للكاميرا من إعدادات التطبيق');
          }
          return;
        }

        if (response.assets && response.assets[0]) {
          const asset = response.assets[0];
          const fileId = await generateSecureUUID();

          // Validate file size
          if (asset.fileSize && asset.fileSize > maxSizeBytes) {
            Alert.alert(
              'حجم الملف كبير',
              `حجم الصورة يتجاوز الحد المسموح (${(maxSizeBytes / 1024 / 1024).toFixed(1)} ميجابايت)`
            );
            return;
          }

          const file: FileAttachment = {
            id: fileId,
            uri: asset.uri || '',
            name: asset.fileName || `photo_${fileId}.jpg`,
            type: asset.type || 'image/jpeg',
            size: asset.fileSize || 0,
            uploadStatus: 'pending',
          };

          await processSelectedFiles([file]);
        }
      });
    } catch (err) {
      console.error('Camera error:', err);
      Alert.alert('خطأ', 'فشل في التقاط الصورة');
    }
  };

  // Handle image library
  const handleImageLibrary = async () => {
    try {
      HapticFeedback.trigger('impactLight');

      const options: ImageLibraryOptions = {
        mediaType: 'photo',
        includeBase64: false,
        maxHeight: 2000,
        maxWidth: 2000,
        quality: 0.8 as PhotoQuality,
        selectionLimit: maxFiles,
      };

      launchImageLibrary(options, async (response: ImagePickerResponse) => {
        if (response.didCancel || response.errorCode) {
          return;
        }

        if (response.assets) {
          const files: FileAttachment[] = await Promise.all(
            response.assets.map(async asset => {
              const fileId = generateUUID();
              return {
                id: fileId,
                uri: asset.uri || '',
                name: asset.fileName || `image_${fileId}.jpg`,
                type: asset.type || 'image/jpeg',
                size: asset.fileSize || 0,
                uploadStatus: 'pending' as const,
              };
            })
          );

          await processSelectedFiles(files);
        }
      });
    } catch (err) {
      console.error('Image library error:', err);
      Alert.alert('خطأ', 'فشل في اختيار الصور');
    }
  };

  // Process selected files with batch processing and memory management
  const processSelectedFiles = async (files: any[]) => {
    setIsProcessing(true);
    onUploadStart?.();

    // Create abort controller for cancellation
    processingAbortController.current = new AbortController();

    try {
      const processedFiles: FileAttachment[] = [];
      const batchSize = 3; // Process files in batches to avoid memory issues

      // Check storage quota first
      const quota = await storageQuota.getQuota();
      if (quota.percentage > 90) {
        Alert.alert(
          'مساحة التخزين منخفضة',
          'مساحة التخزين المحلية شبه ممتلئة. قد تواجه مشاكل في حفظ الملفات.',
          [{ text: 'موافق' }]
        );
      }

      // Process files in batches
      for (let i = 0; i < files.length; i += batchSize) {
        if (processingAbortController.current.signal.aborted) {
          break;
        }

        const batch = files.slice(i, i + batchSize);

        for (const file of batch) {
          // Check file size
          const fileSize = file.size || 0;
          if (fileSize > maxSizeBytes) {
            Alert.alert(
              'حجم الملف كبير',
              `الملف ${file.name} يتجاوز الحد المسموح (${(maxSizeBytes / 1024 / 1024).toFixed(1)} ميجابايت)`
            );
            continue;
          }

          // Check total size to prevent memory issues
          const newTotalSize = totalFileSize + fileSize;
          const maxTotalSize = 50 * 1024 * 1024; // 50MB total limit
          if (newTotalSize > maxTotalSize) {
            Alert.alert(
              'الحد الأقصى للحجم الإجمالي',
              'الحجم الإجمالي للملفات يتجاوز 50 ميجابايت'
            );
            break;
          }

          // Check total files limit
          if (selectedFiles.length + processedFiles.length >= maxFiles) {
            Alert.alert(
              'الحد الأقصى للملفات',
              `يمكنك إرفاق ${maxFiles} ملفات كحد أقصى`
            );
            break;
          }

          // Create file attachment object with proper ID
          const attachment: FileAttachment = {
            id: file.id || generateUUID(),
            uri: file.uri,
            name: file.name || 'file',
            type: file.type || 'application/octet-stream',
            size: fileSize,
            uploadStatus: 'pending',
          };

          processedFiles.push(attachment);
        }
      }

      if (processedFiles.length > 0) {
        const newFiles = [...selectedFiles, ...processedFiles];
        const newTotalSize = newFiles.reduce((sum, f) => sum + f.size, 0);

        setSelectedFiles(newFiles);
        setTotalFileSize(newTotalSize);
        onFilesSelected(newFiles);
        HapticFeedback.trigger('notificationSuccess');
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('File processing cancelled');
      } else {
        console.error('File processing error:', err);
        Alert.alert('خطأ', 'فشل في معالجة الملفات');
        HapticFeedback.trigger('notificationError');
      }
    } finally {
      setIsProcessing(false);
      onUploadComplete?.();
      bottomSheetRef.current?.close();
      processingAbortController.current = null;
    }
  };

  // Remove file with cleanup
  const removeFile = useCallback(async (fileId: string) => {
    HapticFeedback.trigger('impactLight');

    // Find the file to remove
    const fileToRemove = selectedFiles.find(f => f.id === fileId);
    if (fileToRemove) {
      // Clean up temp file
      await cleanupTempFile(fileToRemove.uri);
    }

    const updatedFiles = selectedFiles.filter(f => f.id !== fileId);
    const newTotalSize = updatedFiles.reduce((sum, f) => sum + f.size, 0);

    setSelectedFiles(updatedFiles);
    setTotalFileSize(newTotalSize);
    onFilesSelected(updatedFiles);
  }, [selectedFiles, onFilesSelected]);

  // Show file options bottom sheet
  const showFileOptions = () => {
    HapticFeedback.trigger('impactMedium');
    bottomSheetRef.current?.expand();
  };

  // Render file preview
  const renderFilePreview = (file: FileAttachment) => {
    const isImage = file.type.startsWith('image/');

    return (
      <View key={file.id} style={[styles.filePreview, { backgroundColor: colors.card }]}>
        {isImage ? (
          <Image source={{ uri: file.uri }} style={styles.fileImage} />
        ) : (
          <View style={styles.fileIcon}>
            <Icon
              name={file.type.includes('pdf') ? 'picture-as-pdf' : 'insert-drive-file'}
              size={24}
              color={colors.primary}
            />
          </View>
        )}

        <View style={styles.fileInfo}>
          <Text style={[styles.fileName, { color: colors.text }]} numberOfLines={1}>
            {file.name}
          </Text>
          <Text style={[styles.fileSize, { color: colors.textSecondary }]}>
            {(file.size / 1024).toFixed(1)} KB
          </Text>
        </View>

        {file.uploadStatus === 'uploading' && (
          <ActivityIndicator size="small" color={colors.primary} />
        )}

        {file.uploadStatus === 'error' && (
          <Icon name="error-outline" size={20} color={colors.error} />
        )}

        <TouchableOpacity
          onPress={() => removeFile(file.id)}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Icon name="close" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* File attachment button */}
      <TouchableOpacity
        style={[styles.attachButton, { opacity: disabled ? 0.5 : 1 }]}
        onPress={showFileOptions}
        disabled={disabled || isProcessing}
      >
        <Icon name="attach-file" size={24} color={colors.primary} />
      </TouchableOpacity>

      {/* Selected files preview */}
      {selectedFiles.length > 0 && (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.filesContainer}
        >
          {selectedFiles.map(renderFilePreview)}
        </ScrollView>
      )}

      {/* Bottom sheet for file options */}
      <BottomSheet
        ref={bottomSheetRef}
        snapPoints={[0, 280]}
        index={0}
        backgroundStyle={{ backgroundColor: colors.background }}
        handleIndicatorStyle={{ backgroundColor: colors.border }}
      >
        <View style={styles.bottomSheetContent}>
          <Text style={[styles.bottomSheetTitle, { color: colors.text }]}>
            اختر مصدر الملف
          </Text>

          <TouchableOpacity
            style={[styles.optionButton, { backgroundColor: colors.card }]}
            onPress={handleCamera}
            disabled={isProcessing}
          >
            <Icon name="photo-camera" size={28} color={colors.primary} />
            <Text style={[styles.optionText, { color: colors.text }]}>
              التقاط صورة
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.optionButton, { backgroundColor: colors.card }]}
            onPress={handleImageLibrary}
            disabled={isProcessing}
          >
            <Icon name="photo-library" size={28} color={colors.primary} />
            <Text style={[styles.optionText, { color: colors.text }]}>
              اختر من المعرض
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.optionButton, { backgroundColor: colors.card }]}
            onPress={handleDocumentPicker}
            disabled={isProcessing}
          >
            <Icon name="folder-open" size={28} color={colors.primary} />
            <Text style={[styles.optionText, { color: colors.text }]}>
              اختر ملف
            </Text>
          </TouchableOpacity>
        </View>
      </BottomSheet>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  attachButton: {
    padding: 8,
  },
  filesContainer: {
    maxHeight: 100,
    marginVertical: 8,
  },
  filePreview: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    marginHorizontal: 4,
    borderRadius: 8,
    minWidth: 200,
  },
  fileImage: {
    width: 40,
    height: 40,
    borderRadius: 4,
    marginRight: 8,
  },
  fileIcon: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  fileInfo: {
    flex: 1,
    marginRight: 8,
  },
  fileName: {
    fontSize: 14,
    fontWeight: '500',
  },
  fileSize: {
    fontSize: 12,
    marginTop: 2,
  },
  bottomSheetContent: {
    padding: 20,
  },
  bottomSheetTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 20,
    textAlign: 'center',
  },
  optionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  optionText: {
    fontSize: 16,
    marginLeft: 16,
    flex: 1,
  },
});
