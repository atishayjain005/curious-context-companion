
// Initialize extension when installed
chrome.runtime.onInstalled.addListener(() => {
  console.log("Contextual Research Assistant installed");
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Handle any async messaging between components here
  return true; // Keep the message channel open for async responses
});
