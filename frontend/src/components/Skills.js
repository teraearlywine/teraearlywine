import React, { useEffect, useState } from 'react';
import { FlatList, Text, View, StyleSheet, ActivityIndicator } from 'react-native';
import { skillStyles } from './styles/styles';  // Adjusted path to .js

const Skills = () => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        // Use the correct server URL (replace with your local IP or backend server)
        const response = await fetch('http://192.168.1.161:5000/api/skills'); // Replace with your server URL
        if (!response.ok) {
          throw new Error(`Network response was not ok, status: ${response.status}`);
        }

        const data = await response.json();
        if (!Array.isArray(data)) {
          throw new Error('Invalid data format, expected an array');
        }

        setSkills(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, []);

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text style={skillStyles.errorText}>Error: {error}</Text>;
  }

  return (
    <View style={skillStyles.container}>
      <Text style={skillStyles.heading}>Skills</Text>
      <FlatList
        horizontal
        data={skills}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <Text style={skillStyles.skillItem}>{item}</Text>
        )}
      />
    </View>
  );
};

export default Skills;