import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from '../App';
import { AppRegistry } from 'react-native';

// Register the main application component for React Native
AppRegistry.registerComponent('MyApp', () => App);

// Render the application for web
const rootElement = document.getElementById('root');
if (rootElement) {
  ReactDOM.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
    rootElement
  );
}

// Ensure compatibility with React Native
AppRegistry.runApplication('MyApp', {
  initialProps: {},
  rootTag: rootElement,
});

// TODO: Add error boundaries for better error handling
// TODO: Implement service worker for offline capabilities

// Commenting for clarity
// The above code initializes the React application for both web and React Native environments.
// It ensures that the application can be rendered in a web browser while also being registered for mobile platforms.