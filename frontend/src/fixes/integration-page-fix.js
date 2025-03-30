// Integration Page Fix
// This patch prevents the "TypeError: Cannot read properties of undefined (reading 'length')" error
// by ensuring response data is properly handled even when the API fails

// Find the target element - this should be run after the page is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log("Integration page fix loaded");
  
  // Override the fetch function for the integrations endpoint
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    // Check if this is a call to the integrations status endpoint
    if (args[0] && typeof args[0] === 'string' && args[0].includes('/api/integrations/status')) {
      console.log("Intercepting integrations status API call");
      
      // Call the original fetch
      return originalFetch.apply(this, args)
        .then(response => {
          // Handle error responses
          if (!response.ok) {
            console.error("Integration status API error:", response.status);
            // Create a replacement response with fallback data
            return {
              ok: true,
              json: () => Promise.resolve({
                integrations: [
                  {
                    platform: "youtube",
                    status: "disconnected",
                    last_sync: null,
                    account_name: null
                  },
                  {
                    platform: "stripe", 
                    status: "disconnected",
                    last_sync: null,
                    account_name: null
                  },
                  {
                    platform: "calendly",
                    status: "disconnected",
                    last_sync: null,
                    account_name: null
                  },
                  {
                    platform: "calcom",
                    status: "disconnected",
                    last_sync: null,
                    account_name: null
                  }
                ]
              })
            };
          }
          
          // Handle empty or malformed responses
          return {
            ...response,
            json: () => response.json()
              .then(data => {
                // Ensure the data has the expected structure
                if (!data || !data.integrations) {
                  console.error("Integration status API returned unexpected data format:", data);
                  return {
                    integrations: [
                      {
                        platform: "youtube",
                        status: "disconnected",
                        last_sync: null,
                        account_name: null
                      },
                      {
                        platform: "stripe", 
                        status: "disconnected",
                        last_sync: null,
                        account_name: null
                      },
                      {
                        platform: "calendly",
                        status: "disconnected",
                        last_sync: null,
                        account_name: null
                      },
                      {
                        platform: "calcom",
                        status: "disconnected",
                        last_sync: null,
                        account_name: null
                      }
                    ]
                  };
                }
                return data;
              })
              .catch(error => {
                console.error("Error parsing integration status API response:", error);
                // Return fallback data
                return {
                  integrations: [
                    {
                      platform: "youtube",
                      status: "disconnected",
                      last_sync: null,
                      account_name: null
                    },
                    {
                      platform: "stripe", 
                      status: "disconnected",
                      last_sync: null,
                      account_name: null
                    },
                    {
                      platform: "calendly",
                      status: "disconnected",
                      last_sync: null,
                      account_name: null
                    },
                    {
                      platform: "calcom",
                      status: "disconnected",
                      last_sync: null,
                      account_name: null
                    }
                  ]
                };
              })
          };
        })
        .catch(error => {
          console.error("Fatal error in integration status API call:", error);
          // Create a synthetic response with fallback data
          return {
            ok: true,
            json: () => Promise.resolve({
              integrations: [
                {
                  platform: "youtube",
                  status: "disconnected",
                  last_sync: null,
                  account_name: null
                },
                {
                  platform: "stripe", 
                  status: "disconnected",
                  last_sync: null,
                  account_name: null
                },
                {
                  platform: "calendly",
                  status: "disconnected",
                  last_sync: null,
                  account_name: null
                },
                {
                  platform: "calcom",
                  status: "disconnected",
                  last_sync: null,
                  account_name: null
                }
              ]
            })
          };
        });
    }
    
    // For all other requests, proceed normally
    return originalFetch.apply(this, args);
  };
}); 