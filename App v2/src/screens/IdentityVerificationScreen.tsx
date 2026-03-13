import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  Image,
  ScrollView,
  Platform,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';

type IdentityVerificationScreenNavigationProp = StackNavigationProp<RootStackParamList, 'IdentityVerification'>;

interface Props {
  navigation: IdentityVerificationScreenNavigationProp;
}

const IdentityVerificationScreen: React.FC<Props> = ({ navigation }) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);

  const documentTypes = [
    { id: 'passport', name: 'Passport', icon: 'document' },
    { id: 'drivers_license', name: 'Driver\'s License', icon: 'card' },
    { id: 'national_id', name: 'National ID', icon: 'document-text' },
  ];

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocument(documentId);
  };

  const requestCameraPermission = async () => {
    if (Platform.OS !== 'web') {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Camera permission is required to take photos');
        return false;
      }
    }
    return true;
  };

  const requestMediaLibraryPermission = async () => {
    if (Platform.OS !== 'web') {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Media library permission is required to upload photos');
        return false;
      }
    }
    return true;
  };

  const handleTakePhoto = async () => {
    if (!selectedDocument) {
      Alert.alert('Error', 'Please select a document type first');
      return;
    }

    const hasPermission = await requestCameraPermission();
    if (!hasPermission) return;

    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setCapturedImage(result.assets[0].uri);
        Alert.alert('Success', 'Photo captured successfully!');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to open camera. Please try again.');
      console.error('Camera error:', error);
    }
  };

  const handleUploadPhoto = async () => {
    if (!selectedDocument) {
      Alert.alert('Error', 'Please select a document type first');
      return;
    }

    const hasPermission = await requestMediaLibraryPermission();
    if (!hasPermission) return;

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setCapturedImage(result.assets[0].uri);
        Alert.alert('Success', 'Photo uploaded successfully!');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to open gallery. Please try again.');
      console.error('Gallery error:', error);
    }
  };

  const handleVerify = () => {
    if (!selectedDocument) {
      Alert.alert('Error', 'Please select a document type first');
      return;
    }

    if (!capturedImage) {
      Alert.alert('Error', 'Please take a photo or upload a document image');
      return;
    }

    setIsVerifying(true);
    // Simulate verification process
    setTimeout(() => {
      setIsVerifying(false);
      Alert.alert(
        'Verification Complete',
        'Your identity has been verified successfully!',
        [
          {
            text: 'Continue',
            onPress: () => navigation.navigate('Map'),
          },
        ]
      );
    }, 2000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color="#2c3e50" />
          </TouchableOpacity>
          <Text style={styles.title}>Identity Verification</Text>
          <Text style={styles.subtitle}>Secure your account with document verification</Text>
        </View>

        <View style={styles.content}>
          <View style={styles.securityInfo}>
            <View style={styles.securityIcon}>
              <Ionicons name="shield-checkmark" size={32} color="#27ae60" />
            </View>
            <Text style={styles.securityTitle}>Your Security is Our Priority</Text>
            <Text style={styles.securityDescription}>
              We use bank-level encryption to protect your personal information. 
              Your documents are processed securely and never stored permanently.
            </Text>
          </View>

          <View style={styles.documentSection}>
            <Text style={styles.sectionTitle}>Select Document Type</Text>
            <View style={styles.documentGrid}>
              {documentTypes.map((doc) => (
                <TouchableOpacity
                  key={doc.id}
                  style={[
                    styles.documentCard,
                    selectedDocument === doc.id && styles.documentCardSelected,
                  ]}
                  onPress={() => handleDocumentSelect(doc.id)}
                >
                  <Ionicons
                    name={doc.icon as any}
                    size={32}
                    color={selectedDocument === doc.id ? '#3498db' : '#7f8c8d'}
                  />
                  <Text
                    style={[
                      styles.documentName,
                      selectedDocument === doc.id && styles.documentNameSelected,
                    ]}
                  >
                    {doc.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.photoSection}>
            <Text style={styles.sectionTitle}>Upload Document Photo</Text>
            <View style={styles.photoOptions}>
              <TouchableOpacity style={styles.photoButton} onPress={handleTakePhoto}>
                <Ionicons name="camera" size={24} color="#3498db" />
                <Text style={styles.photoButtonText}>Take Photo</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.photoButton} onPress={handleUploadPhoto}>
                <Ionicons name="image" size={24} color="#3498db" />
                <Text style={styles.photoButtonText}>Upload from Gallery</Text>
              </TouchableOpacity>
            </View>

            {/* Image Preview */}
            {capturedImage && (
              <View style={styles.imagePreviewContainer}>
                <Text style={styles.imagePreviewTitle}>Document Preview</Text>
                <View style={styles.imagePreviewWrapper}>
                  <Image source={{ uri: capturedImage }} style={styles.imagePreview} />
                  <TouchableOpacity 
                    style={styles.removeImageButton}
                    onPress={() => setCapturedImage(null)}
                  >
                    <Ionicons name="close-circle" size={24} color="#e74c3c" />
                  </TouchableOpacity>
                </View>
                <Text style={styles.imagePreviewText}>Tap the X to remove this image</Text>
              </View>
            )}
          </View>

          <View style={styles.requirementsSection}>
            <Text style={styles.requirementsTitle}>Photo Requirements</Text>
            <View style={styles.requirementsList}>
              <View style={styles.requirementItem}>
                <Ionicons name="checkmark-circle" size={16} color="#27ae60" />
                <Text style={styles.requirementText}>Clear, well-lit photo</Text>
              </View>
              <View style={styles.requirementItem}>
                <Ionicons name="checkmark-circle" size={16} color="#27ae60" />
                <Text style={styles.requirementText}>All text must be readable</Text>
              </View>
              <View style={styles.requirementItem}>
                <Ionicons name="checkmark-circle" size={16} color="#27ae60" />
                <Text style={styles.requirementText}>No glare or reflections</Text>
              </View>
              <View style={styles.requirementItem}>
                <Ionicons name="checkmark-circle" size={16} color="#27ae60" />
                <Text style={styles.requirementText}>Document must be valid and current</Text>
              </View>
            </View>
          </View>
        </View>

        <View style={styles.footer}>
          <TouchableOpacity
            style={[styles.verifyButton, isVerifying && styles.verifyButtonDisabled]}
            onPress={handleVerify}
            disabled={isVerifying}
          >
            <Text style={styles.verifyButtonText}>
              {isVerifying ? 'Verifying...' : 'Verify Identity'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContainer: {
    flexGrow: 1,
  },
  header: {
    paddingTop: 20,
    paddingHorizontal: 24,
    paddingBottom: 20,
  },
  backButton: {
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    lineHeight: 24,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
  securityInfo: {
    backgroundColor: '#e8f5e8',
    borderRadius: 12,
    padding: 20,
    marginBottom: 30,
    alignItems: 'center',
  },
  securityIcon: {
    marginBottom: 12,
  },
  securityTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#27ae60',
    marginBottom: 8,
  },
  securityDescription: {
    fontSize: 14,
    color: '#2c3e50',
    textAlign: 'center',
    lineHeight: 20,
  },
  documentSection: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 16,
  },
  documentGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  documentCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    width: '30%',
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#e1e8ed',
  },
  documentCardSelected: {
    borderColor: '#3498db',
    backgroundColor: '#f0f8ff',
  },
  documentName: {
    fontSize: 12,
    color: '#7f8c8d',
    marginTop: 8,
    textAlign: 'center',
  },
  documentNameSelected: {
    color: '#3498db',
    fontWeight: '600',
  },
  photoSection: {
    marginBottom: 30,
  },
  photoOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  photoButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    width: '48%',
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  photoButtonText: {
    fontSize: 14,
    color: '#3498db',
    marginTop: 8,
    fontWeight: '600',
  },
  requirementsSection: {
    marginBottom: 30,
  },
  requirementsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 12,
  },
  requirementsList: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  requirementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  requirementText: {
    fontSize: 14,
    color: '#2c3e50',
    marginLeft: 8,
  },
  footer: {
    paddingHorizontal: 24,
    paddingBottom: 20,
  },
  verifyButton: {
    backgroundColor: '#3498db',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  verifyButtonDisabled: {
    backgroundColor: '#bdc3c7',
  },
  verifyButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  // Image preview styles
  imagePreviewContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  imagePreviewTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 12,
  },
  imagePreviewWrapper: {
    position: 'relative',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  imagePreview: {
    width: 200,
    height: 150,
    borderRadius: 12,
  },
  removeImageButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 12,
  },
  imagePreviewText: {
    fontSize: 12,
    color: '#7f8c8d',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default IdentityVerificationScreen;
