import React from 'react';
import { View, StyleSheet } from 'react-native';
import Header from './src/components/Header';
import Experience from './src/components/Experience';
import Education from './src/components/Education';
import Skills from './src/components/Skills';
import Contact from './src/components/Contact';

class App extends React.Component {
  render() {
    return (
      <View style={styles.container}>
        <Header />
        <Experience />
        <Education />
        <Skills />
        <Contact />
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#121212', // Dark mode background
  },
});

export default App;