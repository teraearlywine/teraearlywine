import { StyleSheet, ScrollView, View } from 'react-native';

export const appStyles = StyleSheet.create({

  container: {
    flex: 1,
    flexGrow: 1,
    padding: 10,
    paddingTop: 50, // Add padding from the top
    paddingBottom: 50, // Add padding from the bottom
    backgroundColor: '#1e1e1e', // Dark mode background
  },
});

export const headerStyles = StyleSheet.create({
  header: {
    borderRadius: 15, // Add rounded edges with a radius of 15
    padding: 20,
    backgroundColor: '#1e1e1e', // Dark mode background for header
    color: '#ffffff',
    alignItems: 'center',
    marginBottom: 20, // Add space below the header
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    backgroundColor: '#1e1e1e',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 18,
    backgroundColor: '#1e1e1e',
    color: '#ffffff',
  },
});

export const experienceStyles = StyleSheet.create({
  container: {
    flex: 1,
    flexGrow: 1,
    padding: 25,
    backgroundColor: '#1e1e1e',
    color: '#ffffff',
    // marginBottom: 20, // Add space below the experience section
  },
  heading: {
    padding: 10,
    fontSize: 24,
    // marginBottom: 12,
    color: '#ffffff',
  },
  item: {
    padding: 10,
    // marginBottom: 12,
    backgroundColor: '#1e1e1e',
    borderRadius: 8,
  },
  company: {
    fontSize: 18,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  role: {
    fontSize: 16,
    color: '#b0b0b0',
  },
});

export const educationStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1e1e1e',
    color: '#ffffff', // White text for contrast
    padding: 25,
    // marginBottom: 20, // Add space below the education section
  },
  title: {
    fontSize: 24,
    // marginBottom: 12,
    color: '#ffffff',
  },
  item: {
    // marginBottom: 12,
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

export const skillStyles = StyleSheet.create({
  container: {
    flex: 1,
    margin: 20,
    justifyContent: 'center', // Center content while loading
    marginBottom: 20, // Add space below the skills section
  },
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#fff', // Assuming dark mode styling
  },
  skillItem: {
    padding: 10,
    fontSize: 18,
    color: '#fff', // Lighter text for readability in dark mode
  },
  errorText: {
    color: 'red',
    fontSize: 16,
    textAlign: 'center',
  },
});

export const contactStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1e1e1e',
    color: '#ffffff', // White text for contrast
    padding: 20,
    marginBottom: 20, // Add space below the contact section
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