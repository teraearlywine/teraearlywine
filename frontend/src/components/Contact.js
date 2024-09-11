import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { contactStyles } from './styles/styles';  // Adjusted path to headercontactStyles.js

const Contact = () => {
  return (
    <View style={contactStyles.container}>
      <Text style={contactStyles.header}>Contact</Text>
      <Text style={contactStyles.paragraph}>If you want to reach out, feel free to contact me at: your.email@example.com</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212', // Dark mode background
    padding: 20,
  },
  header: {
    fontSize: 24,
    color: '#ffffff', // White text for contrast
    marginBottom: 10,
  },
  paragraph: {
    fontSize: 16,
    color: '#b0b0b0', // Lighter text for readability
    textAlign: 'center',
  },
});

export default Contact;