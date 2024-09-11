import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { headerStyles } from './styles/styles';  // Adjusted path to headerStyles.js

const Header = () => {
  return (
    <View style={headerStyles.header}>
      <Text style={headerStyles.title}>Your Name</Text>
      <Text style={headerStyles.subtitle}>Full Stack Data Engineer</Text>
      <Text>Email: your.email@example.com | LinkedIn: /your-profile</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: 20,
    backgroundColor: '#f8f8f8',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 18,
  },
});

export default Header;