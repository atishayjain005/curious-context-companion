document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    // Ensure popup has rounded corners
    document.documentElement.classList.add('extension-popup');
    document.body.classList.add('extension-popup');
    
    // Force rounded corners via inline style for the popup container
    const styleTag = document.createElement('style');
    styleTag.textContent = `
        :host, :root, html, body {
            border-radius: 12px !important;
            overflow: hidden !important;
        }
    `;
    document.head.appendChild(styleTag);

    // --- Element References ---
    const summarizeBtn = document.getElementById('summarize-btn');
    const summaryOutput = document.getElementById('summary-output');
    const copySummaryBtn = document.getElementById('copy-summary-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessageDiv = document.getElementById('error-message');
    const summaryOptionsDiv = document.getElementById('summary-options'); // Keep reference if needed, but visibility less controlled by JS now
    const summaryLengthSlider = document.getElementById('summary-length');
    const summaryLengthValueSpan = document.getElementById('summary-length-value');
    const summaryFooter = document.querySelector('.summary-footer'); // Container for copy button

    // --- Constants ---
    const BACKEND_URL = 'http://localhost:5001'; // Ensure this matches your backend

    // --- Utility Functions ---
    function showLoading(message = "Processing...") {
        console.log("Showing loading indicator...");
        loadingIndicator.querySelector('span').textContent = message;
        loadingIndicator.style.display = 'flex';
        hideError(); // Hide any previous errors
        // Hide results while loading
        summaryOutput.style.display = 'none';
        copySummaryBtn.style.display = 'none';
    }

    function hideLoading() {
        console.log("Hiding loading indicator.");
        loadingIndicator.style.display = 'none';
    }

    function showError(message) {
        console.error("Displaying error:", message);
        errorMessageDiv.textContent = message;
        errorMessageDiv.style.display = 'block';
        hideLoading(); // Hide loading indicator when error occurs
        // Ensure summary/copy button are hidden on error
        summaryOutput.style.display = 'none';
        copySummaryBtn.style.display = 'none';
    }

    function hideError() {
        errorMessageDiv.style.display = 'none';
        errorMessageDiv.textContent = '';
    }

    async function getCurrentTabContent() {
        console.log("Attempting to get current tab content...");
        return new Promise((resolve, reject) => {
            chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
                if (chrome.runtime.lastError) {
                    console.error("Error querying tabs:", chrome.runtime.lastError.message);
                    return reject(new Error(`Error querying tabs: ${chrome.runtime.lastError.message}`));
                }
                if (!tabs || tabs.length === 0 || !tabs[0].id) {
                    console.error("No active tab found or tab ID missing.");
                    return reject(new Error('Could not get active tab ID.'));
                }
                const tabId = tabs[0].id;
                console.log(`Found active tab ID: ${tabId}`);

                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    function: () => document.body.innerText // Consider more robust content extraction if needed
                }, (results) => {
                    if (chrome.runtime.lastError) {
                        console.error("Error executing script:", chrome.runtime.lastError.message);
                        let errorMsg = `Error extracting content: ${chrome.runtime.lastError.message}.`;
                        if (chrome.runtime.lastError.message.includes('Cannot access contents of url')) {
                            errorMsg += ' This often happens on special pages like chrome:// URLs or the Chrome Web Store.';
                        } else if (chrome.runtime.lastError.message.includes('No frame with id')) {
                             errorMsg += ' The tab might have been closed or navigated away.';
                        }
                        return reject(new Error(errorMsg));
                    }
                    // Check result structure carefully
                    if (!results || !Array.isArray(results) || results.length === 0 || !results[0] || typeof results[0].result !== 'string') {
                        console.warn("Script executed but no valid text content found. Page might be complex, empty, or script failed silently.");
                        // Try to get *something*, e.g., title, as fallback? Or just report error.
                        return reject(new Error('Could not extract readable text content from the page.'));
                    }
                    console.log("Successfully extracted page content.");
                    resolve(results[0].result);
                });
            });
        });
    }

    // --- Core Functionality ---
    async function fetchSummary() {
        hideError();
        summaryOutput.textContent = ''; // Clear previous summary
        summaryOutput.style.display = 'none'; // Hide output area
        copySummaryBtn.style.display = 'none'; // Hide copy button
        summarizeBtn.disabled = true;
        showLoading("Fetching page content...");

        try {
            const pageText = await getCurrentTabContent();
            if (!pageText || pageText.trim().length === 0) {
                // Error handled by getCurrentTabContent rejection
                // showError('Could not get text content from the current page.');
                // summarizeBtn.disabled = false; // Done in finally block
                return; // Exit if content extraction failed
            }

            const desiredLength = parseInt(summaryLengthSlider.value, 10);
            const minLength = Math.max(30, Math.round(desiredLength * 0.7));
            const maxLength = Math.min(500, Math.round(desiredLength * 1.3));

            console.log(`Requesting summary with approx length: ${desiredLength} (min: ${minLength}, max: ${maxLength})`);
            showLoading("Generating summary..."); // Updated message

            const response = await fetch(`${BACKEND_URL}/summarize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: pageText,
                    min_length: minLength,
                    max_length: maxLength,
                    model: 'llama3.2' // Explicitly mention model
                }),
            });

            const data = await response.json();
            hideLoading(); // Hide loading indicator *before* showing results/errors

            if (!response.ok) {
                console.error("Backend Error:", data);
                let errorMessage = 'Unknown error from backend';
                
                if (data && data.error) {
                    // Make sure we display the actual error message
                    errorMessage = `Error: ${data.error}`;
                } else if (data && typeof data === 'object') {
                    // If we have an object but no error property, stringify it
                    try {
                        errorMessage = `Error: ${JSON.stringify(data)}`;
                    } catch (e) {
                        errorMessage = `Error ${response.status}: Could not parse error details`;
                    }
                } else {
                    errorMessage = `Error ${response.status}: ${data || 'Unknown error'}`;
                }
                
                showError(errorMessage);
            } else if (data.summary && data.summary.trim() !== '') {
                console.log("Summary received.");
                // Clear previous content
                summaryOutput.innerHTML = '';
                
                // Handle formatted summary with line breaks
                const summaryText = data.summary.trim();
                
                // Convert line breaks to HTML
                const paragraphs = summaryText.split('\n\n');
                
                paragraphs.forEach(paragraph => {
                    if (paragraph.trim()) {
                        // Check if this is a single-line paragraph (likely a heading)
                        if (!paragraph.includes('\n')) {
                            const heading = document.createElement('h3');
                            heading.textContent = paragraph;
                            heading.style.fontWeight = 'bold';
                            heading.style.marginTop = '10px';
                            heading.style.marginBottom = '5px';
                            summaryOutput.appendChild(heading);
                        } else {
                            // Handle multi-line paragraphs that may contain subheadings
                            const lines = paragraph.split('\n');
                            
                            lines.forEach(line => {
                                if (line.trim()) {
                                    // If line ends with colon or matches heading pattern, treat as subheading
                                    if (line.trim().endsWith(':') || 
                                        /\b(key points|highlights|summary|conclusion|findings|results)\b/i.test(line.trim())) {
                                        const subheading = document.createElement('h4');
                                        subheading.textContent = line.trim();
                                        subheading.style.fontWeight = '600';
                                        subheading.style.marginTop = '8px';
                                        subheading.style.marginBottom = '2px';
                                        summaryOutput.appendChild(subheading);
                                    } else {
                                        const text = document.createElement('p');
                                        text.textContent = line.trim();
                                        text.style.margin = '4px 0';
                                        summaryOutput.appendChild(text);
                                    }
                                }
                            });
                        }
                    }
                });
                
                summaryOutput.style.display = 'block'; // Show output area
                copySummaryBtn.style.display = 'block'; // Show copy button
            } else {
                console.warn("Received empty or blank summary from backend.");
                showError('Backend returned an empty summary.');
            }

        } catch (error) {
            console.error("Error during fetchSummary process:", error);
            hideLoading(); // Ensure loading is hidden on error
            let errorMsg = error.message;
            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                 errorMsg = `Network error: Could not connect to backend at ${BACKEND_URL}. Is the backend running?`;
            }
            showError(errorMsg);
        } finally {
            summarizeBtn.disabled = false; // Re-enable button regardless of outcome
        }
    }

    function copySummaryToClipboard() {
        // With the new HTML structure, we need to extract text content with line breaks
        const extractFormattedText = (element) => {
            let result = '';
            const children = element.childNodes;
            
            for (let i = 0; i < children.length; i++) {
                const node = children[i];
                
                // Handle different node types
                if (node.nodeType === Node.TEXT_NODE) {
                    result += node.textContent;
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    // Handle headings and paragraphs with appropriate spacing
                    if (node.tagName === 'H3') {
                        result += node.textContent + '\n\n';
                    } else if (node.tagName === 'H4') {
                        result += node.textContent + '\n';
                    } else if (node.tagName === 'P') {
                        result += node.textContent + '\n';
                    } else {
                        // Recursively process other elements
                        result += extractFormattedText(node);
                    }
                }
            }
            
            return result;
        };
        
        const textToCopy = extractFormattedText(summaryOutput);
        
        if (!textToCopy.trim()) {
            console.warn("Attempted to copy empty summary text.");
            return; // Should not happen if button is only visible with content
        }
        
        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                console.log("Summary copied to clipboard.");
                copySummaryBtn.textContent = 'Copied!';
                copySummaryBtn.disabled = true;
                setTimeout(() => {
                    copySummaryBtn.textContent = 'Copy Summary';
                    copySummaryBtn.disabled = false;
                }, 1500);
            })
            .catch(err => {
                console.error('Failed to copy summary: ', err);
                showError('Failed to copy summary. See console for details.'); // Show error in the UI
                copySummaryBtn.textContent = 'Copy Failed';
                setTimeout(() => { copySummaryBtn.textContent = 'Copy Summary'; }, 2000);
            });
    }

    // --- Event Listeners ---
    summarizeBtn.addEventListener('click', fetchSummary);
    copySummaryBtn.addEventListener('click', copySummaryToClipboard);

    summaryLengthSlider.addEventListener('input', () => {
        summaryLengthValueSpan.textContent = summaryLengthSlider.value;
    });

    // --- Initial State Setup ---
    hideLoading();
    hideError();
    summaryOutput.style.display = 'none'; // Explicitly hide output
    copySummaryBtn.style.display = 'none'; // Hide copy button initially
    summaryLengthValueSpan.textContent = summaryLengthSlider.value; // Initial slider value display

    console.log("Popup script initialized with new UI logic.");

});
