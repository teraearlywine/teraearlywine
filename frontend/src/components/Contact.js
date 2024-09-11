import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { contactStyles } from './styles/styles';  // Adjusted path to headercontactStyles.js

const Contact = () => {
  return (
    <View style={contactStyles.container}>
      <Text style={contactStyles.header}>Contact</Text>
      <Text style={contactStyles.paragraph}>If you want to reach out, feel free to contact me at: info@teraearlywine.com</Text>
    </View>
  );
};

export default Contact;