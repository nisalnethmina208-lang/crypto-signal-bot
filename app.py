import streamlit as st
import streamlit.components.v1 as components

# Streamlit App එකට Manifest සහ Service Worker Inject කිරීම
pwa_code = """
<script>
  // 1. Manifest injection
  const manifest = {
    "name": "My Streamlit App",
    "short_name": "App",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#ff4b4b",
    "icons": [
      {
        "src": "https://streamlit.io/images/brand/streamlit-mark-color.png",
        "sizes": "192x192",
        "type": "image/png"
      },
      {
        "src": "https://streamlit.io/images/brand/streamlit-mark-color.png",
        "sizes": "512x512",
        "type": "image/png"
      }
    ]
  };
  
  const stringManifest = JSON.stringify(manifest);
  const blob = new Blob([stringManifest], {type: 'application/json'});
  const manifestURL = URL.createObjectURL(blob);
  
  let link = document.createElement('link');
  link.rel = 'manifest';
  link.href = manifestURL;
  document.head.appendChild(link);

  // 2. Service Worker Registration
  if ('serviceWorker' in navigator) {
    const swCode = `
      self.addEventListener('install', (e) => self.skipWaiting());
      self.addEventListener('fetch', (e) => {});
    `;
    const swBlob = new Blob([swCode], {type: 'application/javascript'});
    const swURL = URL.createObjectURL(swBlob);
    
    navigator.serviceWorker.register(swURL)
      .then(reg => console.log('Service Worker Registered!', reg))
      .catch(err => console.error('Service Worker Error!', err));
  }
</script>
"""

# මෙතැනින් Code එක App එකට ඇතුළත් වේ
components.html(pwa_code, height=0)
