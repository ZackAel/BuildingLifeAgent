document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key.toLowerCase() === 's') {
      const text = window.getSelection().toString().trim();
      if (text) {
        chrome.runtime.sendMessage({type: 'annotation', text});
      }
    }
  });
  