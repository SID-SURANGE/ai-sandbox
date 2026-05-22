// Configuration
const API_URL = 'http://localhost:8000';

// Initialize on installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed. Setting up indexing...');
  
  // Set up daily indexing
  chrome.alarms.create('dailyIndexing', { periodInMinutes: 1440 });
  
  // Perform initial indexing
  indexAllPages();
});

// Handle alarm events
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'dailyIndexing') {
    console.log('Running daily indexing...');
    indexNewPages();
  }
});

// Get all bookmarks recursively
async function getAllBookmarks() {
  return new Promise((resolve) => {
    chrome.bookmarks.getTree((bookmarkTreeNodes) => {
      const bookmarks = [];
      
      function processNode(node) {
        if (node.url) {
          bookmarks.push({
            id: node.id,
            url: node.url,
            title: node.title || node.url,
            dateAdded: node.dateAdded
          });
        }
        
        if (node.children) {
          for (const child of node.children) {
            processNode(child);
          }
        }
      }
      
      for (const node of bookmarkTreeNodes) {
        processNode(node);
      }
      
      resolve(bookmarks);
    });
  });
}

// Get recent history
async function getRecentHistory(days) {
  const startTime = new Date();
  startTime.setDate(startTime.getDate() - days);
  
  return new Promise((resolve) => {
    chrome.history.search({
      text: '',
      startTime: startTime.getTime(),
      maxResults: 10000
    }, (historyItems) => {
      resolve(historyItems);
    });
  });
}

// Format bookmarks for indexing
function formatBookmarks(bookmarks) {
  return bookmarks.map(bookmark => ({
    url: bookmark.url,
    title: bookmark.title,
    content: `${bookmark.title} ${new URL(bookmark.url).hostname}`,
    type: 'bookmark'
  }));
}

// Format history items for indexing
function formatHistory(historyItems) {
  return historyItems.map(item => ({
    url: item.url,
    title: item.title || item.url,
    content: `${item.title} ${new URL(item.url).hostname}`,
    type: 'history'
  }));
}

// List of domains/keywords to skip for PII
const PII_KEYWORDS = [
  'mail', 'gmail', 'outlook', 'yahoo', 'hotmail', 'protonmail',
  'bank', 'paypal', 'stripe', 'paytm', 'icicibank', 'hdfcbank',
  'sbi', 'axisbank', 'kotak', 'citibank', 'americanexpress', 'chase', 'capitalone',
  'auth', 'login', 'signin', 'secure'
];

// Returns true if the URL should be skipped
function isPIISite(url) {
  try {
    const hostname = new URL(url).hostname.toLowerCase();
    return PII_KEYWORDS.some(keyword => hostname.includes(keyword));
  } catch {
    return false;
  }
}

// Send pages to backend for indexing
async function sendPagesToBackend(pages) {
  try {
    console.log(`Sending ${pages.length} pages to backend for indexing...`);
    
    const response = await fetch(`${API_URL}/index_pages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(pages)
    });
    
    const result = await response.json();
    console.log('Indexing result:', result);
    
    return result;
  } catch (error) {
    console.error('Error sending pages to backend:', error);
    return { status: 'error', message: error.message };
  }
}

// Index all pages (bookmarks and history)
async function indexAllPages() {
  console.log('Starting full indexing...');
  
  // Get bookmarks
  const bookmarks = await getAllBookmarks();
  console.log(`Found ${bookmarks.length} bookmarks`);
  
  // Get history (last 30 days)
  const history = await getRecentHistory(30);
  console.log(`Found ${history.length} history items`);
  
  // Format data for indexing
  const pages = [
    ...formatBookmarks(bookmarks),
    ...formatHistory(history)
  ];
  
  // Send to backend in batches of 1000, filtering out PII sites
  const batchSize = 1000;
  for (let i = 0; i < pages.length; i += batchSize) {
    const batch = pages.slice(i, i + batchSize).filter(page => !isPIISite(page.url));
    await sendPagesToBackend(batch);
    console.log(`Indexed batch ${i/batchSize + 1} of ${Math.ceil(pages.length/batchSize)}`);
  }
  
  console.log('Full indexing completed');
}

// Index new pages since last indexing
async function indexNewPages() {
  // For simplicity, we're just indexing the last day's history
  const history = await getRecentHistory(1);
  console.log(`Found ${history.length} recent history items`);
  
  if (history.length > 0) {
    const pages = formatHistory(history).filter(page => !isPIISite(page.url));
    await sendPagesToBackend(pages);
  }
  
  console.log('Daily indexing completed');
}

// Expose search function for popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'search') {
    searchPages(request.query)
      .then(results => sendResponse(results))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Required for async sendResponse
  }
});

// Search function
async function searchPages(query) {
  try {
    const response = await fetch(`${API_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        limit: 10
      })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error searching pages:', error);
    return { results: [] };
  }
}
