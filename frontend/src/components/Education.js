import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import { educationStyles } from './styles/styles';  // Adjusted path to .js

const Education = () => {
  const [education, setEducation] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEducation = async () => {
      try {
        // Use the correct server URL (adjust the IP for your server)
        const response = await fetch('http://192.168.1.161:5000/api/education');
        if (!response.ok) {
          throw new Error(`Network response was not ok, status: ${response.status}`);
        }
        const data = await response.json();
        setEducation(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchEducation();
  }, []);

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text style={educationStyles.errorText}>Error: {error}</Text>;
  }

  const renderItem = ({ item }) => (
    <View style={educationStyles.item}>
      <Text style={educationStyles.school}>{item.school}</Text>
      <Text style={educationStyles.degree}>{item.degree} ({item.years})</Text>
    </View>
  );

  return (
    <View style={educationStyles.container}>
      <Text style={educationStyles.title}>Education</Text>
      <FlatList
        data={education}
        renderItem={renderItem}
        keyExtractor={(item, index) => index.toString()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
    padding: 16,
  },
  title: {
    fontSize: 24,
    color: '#ffffff',
    marginBottom: 16,
  },
  item: {
    marginBottom: 12,
    padding: 10,
    backgroundColor: '#1e1e1e',
    borderRadius: 8,
  },
  school: {
    fontSize: 18,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  degree: {
    fontSize: 16,
    color: '#b0b0b0',
  },
  errorText: {
    color: 'red',
    fontSize: 16,
    textAlign: 'center',
  },
});

export default Education;