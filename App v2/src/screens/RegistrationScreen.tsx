import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Alert,
  Modal,
  FlatList,
  Platform,
} from 'react-native';
import { ActivityIndicator } from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../services/api';
import { storage } from '../services/storage';
import { useAppContext } from '../context/AppContext';
// Conditional import for DateTimePicker
let DateTimePicker: any = null;
try {
  DateTimePicker = require('@react-native-community/datetimepicker').default;
} catch (error) {
  console.log('DateTimePicker not available');
}

type RegistrationScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Registration'>;

interface Props {
  navigation: RegistrationScreenNavigationProp;
}

// Country codes data
const countryCodes = [
  { code: '+1', country: 'United States', flag: '🇺🇸' },
  { code: '+1', country: 'Canada', flag: '🇨🇦' },
  { code: '+44', country: 'United Kingdom', flag: '🇬🇧' },
  { code: '+91', country: 'India', flag: '🇮🇳' },
  { code: '+86', country: 'China', flag: '🇨🇳' },
  { code: '+81', country: 'Japan', flag: '🇯🇵' },
  { code: '+82', country: 'South Korea', flag: '🇰🇷' },
  { code: '+61', country: 'Australia', flag: '🇦🇺' },
  { code: '+49', country: 'Germany', flag: '🇩🇪' },
  { code: '+33', country: 'France', flag: '🇫🇷' },
  { code: '+39', country: 'Italy', flag: '🇮🇹' },
  { code: '+34', country: 'Spain', flag: '🇪🇸' },
  { code: '+7', country: 'Russia', flag: '🇷🇺' },
  { code: '+55', country: 'Brazil', flag: '🇧🇷' },
  { code: '+52', country: 'Mexico', flag: '🇲🇽' },
  { code: '+971', country: 'UAE', flag: '🇦🇪' },
  { code: '+966', country: 'Saudi Arabia', flag: '🇸🇦' },
  { code: '+65', country: 'Singapore', flag: '🇸🇬' },
  { code: '+60', country: 'Malaysia', flag: '🇲🇾' },
  { code: '+66', country: 'Thailand', flag: '🇹🇭' },
];

const RegistrationScreen: React.FC<Props> = ({ navigation }) => {
  const { login } = useAppContext();
  const [formData, setFormData] = useState({
    fullName: '',
    contactNumber: '',
    emergencyContactName: '',
    emergencyContactPhone: '',
    birthDate: '',
    tripStartDate: '',
    tripEndDate: '',
  });

  const [selectedCountryCode, setSelectedCountryCode] = useState(countryCodes[0]);
  const [showCountryModal, setShowCountryModal] = useState(false);
  const [showStartDatePicker, setShowStartDatePicker] = useState(false);
  const [showEndDatePicker, setShowEndDatePicker] = useState(false);
  const [showBirthDatePicker, setShowBirthDatePicker] = useState(false);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [birthDate, setBirthDate] = useState(new Date(1995, 0, 1));
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleCountrySelect = (country: any) => {
    setSelectedCountryCode(country);
    setShowCountryModal(false);
  };

  const formatDate = (d: Date) => {
    const y = d.getFullYear();
    const m = `${d.getMonth() + 1}`.padStart(2, '0');
    const day = `${d.getDate()}`.padStart(2, '0');
    return `${y}-${m}-${day}`;
  };

  const handleStartDateChange = (event: any, selectedDate?: Date) => {
    setShowStartDatePicker(false);
    if (selectedDate) {
      setStartDate(selectedDate);
      setFormData(prev => ({
        ...prev,
        tripStartDate: formatDate(selectedDate),
      }));
    }
  };

  const handleEndDateChange = (event: any, selectedDate?: Date) => {
    setShowEndDatePicker(false);
    if (selectedDate) {
      setEndDate(selectedDate);
      setFormData(prev => ({
        ...prev,
        tripEndDate: formatDate(selectedDate),
      }));
    }
  };

  const handleBirthDateChange = (event: any, selectedDate?: Date) => {
    setShowBirthDatePicker(false);
    if (selectedDate) {
      setBirthDate(selectedDate);
      setFormData(prev => ({
        ...prev,
        birthDate: formatDate(selectedDate),
      }));
    }
  };

  const handleRegister = async () => {
    if (!formData.fullName || !formData.contactNumber || !formData.emergencyContactName || 
        !formData.emergencyContactPhone || !formData.birthDate || !formData.tripStartDate || !formData.tripEndDate) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setIsLoading(true);
    try {
      // Generate a unique KYC hash per registration attempt to avoid duplicates on backend
      const kycHash = `kyc_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;

      const res = await api.register({
        name: formData.fullName,
        kyc_hash: kycHash,
        emergency_contact: { 
          name: formData.emergencyContactName, 
          phone: `${selectedCountryCode.code} ${formData.emergencyContactPhone}`,
          relation: 'Family'
        },
        trip_end_date: new Date(formData.tripEndDate).toISOString(),
      });
      
      // Use global context login instead of direct storage calls
      await login(res.tourist_id);
      
      // Still save profile data for display purposes
      await storage.setProfile({
        name: formData.fullName,
        contact: `${selectedCountryCode.code} ${formData.contactNumber}`,
        dob: formData.birthDate,
        nationality: 'N/A',
        emergency: { name: formData.emergencyContactName, phone: `${selectedCountryCode.code} ${formData.emergencyContactPhone}` },
        trip: { start: formData.tripStartDate, end: formData.tripEndDate },
      });
      
      Alert.alert('Success', 'Registration successful', [
        { text: 'Continue', onPress: () => navigation.navigate('IdentityVerification') },
      ]);
    } catch (e: any) {
      Alert.alert('Registration failed', e?.message ?? 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.formCard}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Tourist</Text>
            <Text style={styles.title}>Registration</Text>
          </View>

          {/* Form Fields */}
          <View style={styles.formContainer}>
            {/* Full Name */}
            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <Ionicons name="person" size={20} color="#7f8c8d" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  value={formData.fullName}
                  onChangeText={(value) => handleInputChange('fullName', value)}
                  placeholder="Full Name"
                  placeholderTextColor="#999"
                />
              </View>
            </View>

            {/* Contact Number */}
            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <Ionicons name="call" size={20} color="#7f8c8d" style={styles.inputIcon} />
                <TouchableOpacity 
                  style={styles.countryCodeButton}
                  onPress={() => setShowCountryModal(true)}
                >
                  <Text style={styles.countryCodeText}>{selectedCountryCode.flag} {selectedCountryCode.code}</Text>
                  <Ionicons name="chevron-down" size={16} color="#7f8c8d" />
                </TouchableOpacity>
                <TextInput
                  style={styles.input}
                  value={formData.contactNumber}
                  onChangeText={(value) => handleInputChange('contactNumber', value)}
                  placeholder="Contact number"
                  placeholderTextColor="#999"
                  keyboardType="phone-pad"
                />
              </View>
            </View>

            {/* Birth Date */}
            <View style={styles.inputContainer}>
              {Platform.OS === 'web' ? (
                <View style={styles.inputWrapper}>
                  <Ionicons name="calendar" size={20} color="#7f8c8d" style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={formData.birthDate}
                    onChangeText={(v) => handleInputChange('birthDate', v)}
                    placeholder="Birth Date (YYYY-MM-DD)"
                    placeholderTextColor="#999"
                  />
                </View>
              ) : (
                <TouchableOpacity
                  style={styles.inputWrapper}
                  onPress={() => setShowBirthDatePicker(true)}
                >
                  <Ionicons name="calendar" size={20} color="#7f8c8d" style={styles.inputIcon} />
                  <Text style={[styles.input, formData.birthDate ? styles.inputText : styles.placeholderText]}>
                    {formData.birthDate || 'Birth Date'}
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Emergency Contact Name */}
            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <Ionicons name="person" size={20} color="#7f8c8d" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  value={formData.emergencyContactName}
                  onChangeText={(value) => handleInputChange('emergencyContactName', value)}
                  placeholder="Emergency Contact Name"
                  placeholderTextColor="#999"
                />
              </View>
            </View>

            {/* Emergency Contact Phone */}
            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <Ionicons name="phone-portrait" size={20} color="#7f8c8d" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  value={formData.emergencyContactPhone}
                  onChangeText={(value) => handleInputChange('emergencyContactPhone', value)}
                  placeholder="Emergency Contact Phone"
                  placeholderTextColor="#999"
                  keyboardType="phone-pad"
                />
              </View>
            </View>

            {/* Trip Start Date */}
            <View style={styles.inputContainer}>
              {Platform.OS === 'web' ? (
                <View style={styles.inputWrapper}>
                  <Ionicons name="calendar" size={20} color="#7f8c8d" style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={formData.tripStartDate}
                    onChangeText={(v) => handleInputChange('tripStartDate', v)}
                    placeholder="Trip Start Date (YYYY-MM-DD)"
                    placeholderTextColor="#999"
                  />
                </View>
              ) : (
                <TouchableOpacity
                  style={styles.inputWrapper}
                  onPress={() => setShowStartDatePicker(true)}
                >
                  <Ionicons name="calendar" size={20} color="#7f8c8d" style={styles.inputIcon} />
                  <Text style={[styles.input, formData.tripStartDate ? styles.inputText : styles.placeholderText]}>
                    {formData.tripStartDate || 'Trip Start Date'}
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Trip End Date */}
            <View style={styles.inputContainer}>
              {Platform.OS === 'web' ? (
                <View style={styles.inputWrapper}>
                  <Ionicons name="calendar" size={20} color="#7f8c8d" style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={formData.tripEndDate}
                    onChangeText={(v) => handleInputChange('tripEndDate', v)}
                    placeholder="Trip End Date (YYYY-MM-DD)"
                    placeholderTextColor="#999"
                  />
                </View>
              ) : (
                <TouchableOpacity
                  style={styles.inputWrapper}
                  onPress={() => setShowEndDatePicker(true)}
                >
                  <Ionicons name="calendar" size={20} color="#7f8c8d" style={styles.inputIcon} />
                  <Text style={[styles.input, formData.tripEndDate ? styles.inputText : styles.placeholderText]}>
                    {formData.tripEndDate || 'Trip End Date'}
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Register Button */}
            <TouchableOpacity style={[styles.registerButton, isLoading && { opacity: 0.7 }]} disabled={isLoading} onPress={handleRegister}>
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.registerButtonText}>Register</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* Country Code Modal */}
      <Modal
        visible={showCountryModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowCountryModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Select Country Code</Text>
              <TouchableOpacity onPress={() => setShowCountryModal(false)}>
                <Ionicons name="close" size={24} color="#2c3e50" />
              </TouchableOpacity>
            </View>
            <FlatList
              data={countryCodes}
              keyExtractor={(item, index) => `${item.code}-${index}`}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.countryItem}
                  onPress={() => handleCountrySelect(item)}
                >
                  <Text style={styles.countryFlag}>{item.flag}</Text>
                  <Text style={styles.countryName}>{item.country}</Text>
                  <Text style={styles.countryCode}>{item.code}</Text>
                </TouchableOpacity>
              )}
            />
          </View>
        </View>
      </Modal>

      {/* Date Pickers */}
      {showStartDatePicker && DateTimePicker && (
        <DateTimePicker
          value={startDate}
          mode="date"
          display="default"
          onChange={handleStartDateChange}
        />
      )}

      {showEndDatePicker && DateTimePicker && (
        <DateTimePicker
          value={endDate}
          mode="date"
          display="default"
          onChange={handleEndDateChange}
        />
      )}

      {showBirthDatePicker && DateTimePicker && (
        <DateTimePicker
          value={birthDate}
          mode="date"
          display="default"
          onChange={handleBirthDateChange}
          maximumDate={new Date()} 
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#4A90E2', // Blue gradient background
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  formCard: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 30,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
  },
  formContainer: {
    width: '100%',
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e1e8ed',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#2c3e50',
    padding: 0,
  },
  dropdownIcon: {
    marginLeft: 8,
  },
  registerButton: {
    backgroundColor: '#4A90E2',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 20,
    shadowColor: '#4A90E2',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  registerButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  // Country code styles
  countryCodeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  countryCodeText: {
    fontSize: 16,
    color: '#2c3e50',
    marginRight: 4,
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 20,
    width: '90%',
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  countryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  countryFlag: {
    fontSize: 24,
    marginRight: 12,
  },
  countryName: {
    flex: 1,
    fontSize: 16,
    color: '#2c3e50',
  },
  countryCode: {
    fontSize: 16,
    color: '#7f8c8d',
    fontWeight: '600',
  },
  // Date picker styles
  inputText: {
    color: '#2c3e50',
  },
  placeholderText: {
    color: '#999',
  },
});

export default RegistrationScreen;
