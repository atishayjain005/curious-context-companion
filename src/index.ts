
// This file serves as the main entry point for the project
// It imports and re-exports components from the extension and backend

// Export Chrome extension components
export * from './extension/popup';

// Re-export backend services (placeholder - actual backend is Python)
export const backendServices = {
  summarize: 'http://localhost:5000/summarize',
  recommend: 'http://localhost:5000/recommend',
  citation: 'http://localhost:5000/citation'
};
