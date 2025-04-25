document.addEventListener('DOMContentLoaded', function() {
  const searchForm = document.getElementById('searchForm');
  const searchInput = document.getElementById('searchInput');
  const resultsContainer = document.getElementById('results');
  const loadingIndicator = document.getElementById('loadingIndicator');

  if (!searchForm || !searchInput || !resultsContainer || !loadingIndicator) {
    // Show a user-friendly error if any required element is missing
    if (resultsContainer) {
      resultsContainer.innerHTML = '<p style="color:red">Error: Extension UI is misconfigured. Please reload or reinstall.</p>';
    } else {
      alert('Error: Extension UI is misconfigured. Please reload or reinstall.');
    }
    return;
  }
  
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const query = searchInput.value.trim();
    
    if (query) {
      // Show loading indicator
      loadingIndicator.style.display = 'block';
      resultsContainer.innerHTML = '';
      
      // Send search request to background script
      chrome.runtime.sendMessage(
        { action: 'search', query: query },
        function(response) {
          // Hide loading indicator
          loadingIndicator.style.display = 'none';
          
          if (response.error) {
            showError(response.error);
          } else {
            displayResults(response.results);
          }
        }
      );
    }
  });
  
  function displayResults(results) {
    if (!Array.isArray(results) || results.length === 0) {
      resultsContainer.innerHTML = '<p class="no-results">No results found</p>';
      return;
    }
    // Remove duplicate results by URL
    const unique = {};
    const deduped = [];
    for (const res of results) {
      if (res.url && !unique[res.url]) {
        unique[res.url] = true;
        deduped.push(res);
      }
    }
    // Only show top 3 results
    const topResults = deduped.slice(0, 3);
    resultsContainer.innerHTML = '';
    const cardList = document.createElement('div');
    cardList.className = 'results-card-list';
    topResults.forEach(result => {
      const card = document.createElement('div');
      card.className = 'result-card';
      // Make the whole card clickable
      card.tabIndex = 0;
      card.setAttribute('role', 'link');
      // Prevent both card and link from opening link twice
      function openInNewTab(e) {
        e.preventDefault();
        e.stopPropagation();
        chrome.tabs.create({ url: result.url, active: false });
      }
      card.addEventListener('click', openInNewTab);
      card.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          openInNewTab(e);
        }
      });
      // Favicon or fallback icon
      const favicon = document.createElement('img');
      favicon.className = 'result-favicon';
      try {
        const urlObj = new URL(result.url);
        favicon.src = urlObj.origin + '/favicon.ico';
      } catch {
        favicon.src = 'default-favicon.svg';
      }
      favicon.onerror = function() {
        favicon.src = 'default-favicon.svg';
      };
      favicon.alt = 'icon';
      // Content container
      const content = document.createElement('div');
      content.className = 'result-content';
      // Title link (for accessibility, but not only clickable area)
      const resultLink = document.createElement('a');
      resultLink.href = result.url;
      resultLink.className = 'result-link';
      resultLink.textContent = result.title;
      resultLink.target = '_blank';
      resultLink.rel = 'noopener noreferrer';
      resultLink.addEventListener('click', openInNewTab);
      // Meta info
      const resultMeta = document.createElement('div');
      resultMeta.className = 'result-meta';
      // Type
      const resultType = document.createElement('span');
      resultType.className = `result-type ${result.type}`;
      resultType.textContent = result.type;
      // Domain (optional)
      let domain = '';
      try {
        domain = new URL(result.url).hostname.replace(/^www\./, '');
      } catch {}
      if (domain) {
        const domainSpan = document.createElement('span');
        domainSpan.className = 'result-domain';
        domainSpan.textContent = domain;
        resultMeta.appendChild(domainSpan);
      }
      resultMeta.appendChild(resultType);
      content.appendChild(resultLink);
      content.appendChild(resultMeta);
      card.appendChild(favicon);
      card.appendChild(content);
      cardList.appendChild(card);
    });
    resultsContainer.appendChild(cardList);
  }

  // Search bar clear (X) button logic
  const clearBtn = document.getElementById('clearBtn');
  searchInput.addEventListener('input', function() {
    if (searchInput.value.length > 0) {
      clearBtn.style.display = 'block';
    } else {
      clearBtn.style.display = 'none';
    }
  });
  clearBtn.addEventListener('click', function() {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    searchInput.focus();
    resultsContainer.innerHTML = '';
  });

  // Close button logic
  const closeBtn = document.getElementById('closeBtn');
  if (closeBtn) {
    closeBtn.addEventListener('click', function() {
      window.close();
    });
  }

  function showError(message) {
    resultsContainer.innerHTML = `<p class="error-message">Error: ${message}</p>`;
  }
});
