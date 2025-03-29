/**
 * Integrations Page Fix
 * 
 * This script patches the application to prevent a TypeError when
 * the backend API is not available. It provides fallback data for
 * the integrations status endpoint.
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('[Integration Fix] Script loaded');
  
  // Store the original fetch function
  const originalFetch = window.fetch;
  
  // Override the fetch function
  window.fetch = function(url, options) {
    // Check if this is a call to the integrations status endpoint
    if (url && typeof url === 'string' && url.includes('/api/integrations/status')) {
      console.log('[Integration Fix] Intercepted API call to integrations status');
      
      // Call the original fetch
      return originalFetch(url, options)
        .then(response => {
          console.log('[Integration Fix] Response status:', response.status);
          
          // If the response is not ok (e.g., 404, 500, etc.)
          if (!response.ok) {
            console.warn('[Integration Fix] API error, providing fallback data');
            
            // Return a fake successful response with fallback data
            return {
              ok: true,
              status: 200,
              json: () => Promise.resolve({
                integrations: [
                  { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
                  { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
                  { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
                  { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
                ]
              })
            };
          }
          
          // If the response is ok, clone it and check if it contains valid data
          return response.clone().json()
            .then(data => {
              if (!data || !data.integrations || !Array.isArray(data.integrations)) {
                console.warn('[Integration Fix] Invalid response format, providing fallback data');
                
                // Return a fake successful response with fallback data
                return {
                  ok: true,
                  status: 200,
                  json: () => Promise.resolve({
                    integrations: [
                      { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
                      { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
                      { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
                      { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
                    ]
                  })
                };
              }
              
              // If the response contains valid data, return the original response
              return response;
            })
            .catch(error => {
              console.error('[Integration Fix] Error parsing response:', error);
              
              // Return a fake successful response with fallback data
              return {
                ok: true,
                status: 200,
                json: () => Promise.resolve({
                  integrations: [
                    { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
                    { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
                    { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
                    { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
                  ]
                })
              };
            });
        })
        .catch(error => {
          console.error('[Integration Fix] Network error:', error);
          
          // Return a fake successful response with fallback data
          return {
            ok: true,
            status: 200,
            json: () => Promise.resolve({
              integrations: [
                { platform: "youtube", status: "disconnected", account_name: null, last_sync: null },
                { platform: "stripe", status: "disconnected", account_name: null, last_sync: null },
                { platform: "calendly", status: "disconnected", account_name: null, last_sync: null },
                { platform: "calcom", status: "disconnected", account_name: null, last_sync: null }
              ]
            })
          };
        });
    }
    
    // For all other requests, use the original fetch
    return originalFetch(url, options);
  };
  
  console.log('[Integration Fix] Fetch function patched');
}); 