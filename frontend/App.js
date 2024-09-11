import React from 'react';
import { View, StyleSheet } from 'react-native';
import { appStyles } from './src/components/styles/styles'; // Import styles

import Header from './src/components/Header';
import Experience from './src/components/Experience';
import Education from './src/components/Education';
import Skills from './src/components/Skills';
import Contact from './src/components/Contact';

class App extends React.Component {
  render() {
    return (
      <View style={appStyles.container}>
        <Header />
        <Experience />
        <Education />
        <Skills />
        <Contact />
      </View>
    );
  }
}

export default App;