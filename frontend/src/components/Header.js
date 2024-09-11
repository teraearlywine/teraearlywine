import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { headerStyles } from './styles/styles';  // Adjusted path to headerStyles.js

const Header = () => {
  return (
    <View style={headerStyles.header}>
      <Text style={headerStyles.title}>Tera Earlywine</Text>
      <Text style={headerStyles.subtitle}>Full Stack Data Engineer</Text>
      {/* <Text style={headerStyles.email}>Email: your.email@example.com | LinkedIn: /your-profile</Text> */}
    </View>
  );
};

export default Header;