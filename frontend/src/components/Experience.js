import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { experienceStyles } from './styles/styles';  // Adjusted path to .js

const Experience = () => {
  const [experience, setExperience] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExperience = async () => {
      try {
        // Use the correct server URL (adjust the IP for your server)
        const response = await fetch('http://192.168.1.161:5000/api/experience');
        if (!response.ok) {
          throw new Error(`Network response was not ok, status: ${response.status}`);
        }
        const data = await response.json();
        setExperience(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchExperience();
  }, []);

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text style={experienceStyles.errorText}>Error: {error}</Text>;
  }

  return (
    <View style={experienceStyles.container}>
      <Text style={experienceStyles.heading}>Experience</Text>
      {experience.map((exp, index) => (
        <View key={index} style={experienceStyles.item}>
          <Text style={experienceStyles.company}>{exp.company}</Text>
          <Text style={experienceStyles.role}>{exp.role} ({exp.years})</Text>
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#121212',
  },
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#ffffff',
  },
  item: {
    marginBottom: 12,
    padding: 10,
    backgroundColor: '#1e1e1e',
    borderRadius: 8,
  },
  company: {
    fontSize: 18,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  errorText: {
    color: 'red',
    fontSize: 16,
    textAlign: 'center',
  },
});

export default Experience;