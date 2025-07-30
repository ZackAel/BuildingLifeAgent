const DISTRACTING_SITES = [
    'reddit.com',
    'facebook.com',
    'twitter.com',
    'youtube.com'
  ];
  
  let activeTabId = null;
  let activeStart = Date.now();
  const timeSpent = {};
  
  function getDomain(url) {
    try {
      return new URL(url).hostname;
    } catch {
      return null;
    }
  }
  
  async function logTime(tabId) {
    if (activeTabId === null) return;
    const tab = await chrome.tabs.get(activeTabId).catch(() => null);
    if (!tab || !tab.url) return;
    const domain = getDomain(tab.url);
    const delta = Date.now() - activeStart;
    if (!domain) return;
    timeSpent[domain] = (timeSpent[domain] || 0) + delta;
    if (DISTRACTING_SITES.includes(domain) && timeSpent[domain] > 20 * 60 * 1000) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: 'Time to focus',
        message: `You've been on ${domain} for 20 mins, ready to get back to work?`
      });
      timeSpent[domain] = 0;
    }
  }
  
  chrome.tabs.onActivated.addListener(async info => {
    await logTime();
    activeTabId = info.tabId;
    activeStart = Date.now();
  });
  
  chrome.tabs.onRemoved.addListener(async (tabId) => {
    if (tabId === activeTabId) {
      await logTime();
      activeTabId = null;
    }
  });
  
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (tab.active && changeInfo.status === 'complete') {
      if (/meet.google.com|zoom.us/.test(tab.url || '')) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon.png',
          title: 'Meeting detected',
          message: 'Would you like me to take notes?'
        });
      } else if (/mail.google.com/.test(tab.url || '')) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon.png',
          title: 'Gmail reminder',
          message: "Don't forget to reply to Sarah."
        });
      } else if (/linkedin.com/.test(tab.url || '')) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon.png',
          title: 'LinkedIn check-in',
          message: 'Time to check in with your network.'
        });
      }
    }
  });
  
  setInterval(() => {
    chrome.tabs.query({}, tabs => {
      const distracting = tabs.filter(t => DISTRACTING_SITES.some(d => (t.url || '').includes(d)));
      if (distracting.length > 0) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon.png',
          title: 'Tab reminder',
          message: 'Consider closing distracting tabs during focus time.'
        });
      }
    });
  }, 10 * 60 * 1000);
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'annotation') {
      chrome.storage.local.get({notes: []}, data => {
        data.notes.push(request.text);
        chrome.storage.local.set({notes: data.notes});
      });
    }
  });
  