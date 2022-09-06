import React, { useState, useEffect, useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import "./App.scss";

function App(props) {
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Hardcode this because our frontend does not have Cognito login yet
  const cognito_token = "eyJraWQiOiJcL0Fia01US1h1UitIVmtsb0N2SE1PdVJ0NXJZZStvY1VxRThFNEJMeVNBdz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI2OTkwYmMzZS01ZDIwLTRkMDctYTkxZC1kNmE4NTIwOGU4MjQiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9aaEhESllMNWMiLCJjbGllbnRfaWQiOiIybmx2NGdvMWpjMWE3ajV1ZXFiNWsxcnYxaSIsIm9yaWdpbl9qdGkiOiI3NTEyZTdjMy0wZjdmLTQwNGUtYmE5Yi1mYmNmYjJiODJkMDIiLCJldmVudF9pZCI6ImM0NTIwYzYyLTM3NTAtNDE5Yi1iM2VkLTM0OTIxYzU5YzgzNCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NjI0NjM4NTYsImV4cCI6MTY2MjQ2NzQ1NiwiaWF0IjoxNjYyNDYzODU2LCJqdGkiOiIxNDJmNjY2OS0yODE5LTQ4ZmQtYTNiNy05MTMyNDc0ZTU1N2EiLCJ1c2VybmFtZSI6IjY5OTBiYzNlLTVkMjAtNGQwNy1hOTFkLWQ2YTg1MjA4ZTgyNCJ9.U6lriwokMSbrgO2yyJNt_owFaufWmNEsGx1YLp-lVPu-cvlCGMLbO5boytZdd16TrD-pg7pCM8T-VuBUcQ49pHLb4qJv_OhSGpIiEfqMAMDKOlJV3tQCgoz_FSKO-d9f6IfH5yidAt46zwBoNFOs-PuKe1Wu27KGm23YpE6w2-6wRAtUCrbn9-g-KMv4X8OIx6nojEoYcA34gJTFoj2pXvyqheflWliF6yAqoCkfmGhPEYNMeMcVyaJljTmdEgLdTwF7jQxpxrPaa7fB0nOUvG99P6LhC6ruV34xyCJ9R81C7NOd2yJsTVCxDf7QWWIioBcRSKpRmouPNS1ao1KQHw"

  const onSuccess = useCallback(async (publicToken, metadata) => {
    const firstAccountID = metadata.accounts[0].id
    setLoading(true);
    const response = await fetch("http://localhost:8000/plaid/exchange_public_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "access-token": cognito_token,
      },
      body: JSON.stringify({ public_token: publicToken, account_id: firstAccountID }),
    });
    const data = await response.json(); // Contains processor token
    console.log(JSON.stringify(data));
  }, []);

  // Creates a Link token
  const createLinkToken = React.useCallback(async () => {
    // For OAuth, use previously generated Link token
    if (window.location.href.includes("?oauth_state_id=")) {
      const linkToken = localStorage.getItem('link_token');
      setToken(linkToken);
    } else {
      const response = await fetch("http://localhost:8000/plaid/create_link_token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "access-token": cognito_token,
        },
      });
      const data = await response.json();
      const linkToken = data.link_token
      setToken(linkToken);
      localStorage.setItem("link_token", linkToken);
    }
  }, [setToken]);

  let isOauth = false;

  const config = {
    token,
    onSuccess,
    env: "sandbox",
  };

  // For OAuth, configure the received redirect URI
  if (window.location.href.includes("?oauth_state_id=")) {
    config.receivedRedirectUri = window.location.href;
    isOauth = true;
  }
  const { open, ready } = usePlaidLink(config);

  useEffect(() => {
    if (token == null) {
      createLinkToken();
    }
    if (isOauth && ready) {
      open();
    }
  }, [token, isOauth, ready, open]);
  
  return (
    <div>
      <div>
        <button onClick={() => open()
          } disabled={!ready}>
          <strong>Link account!</strong>
        </button>

        {!loading &&
          data != null &&
          Object.entries(data).map((entry, i) => (
            <pre key={i}>
              <code>{JSON.stringify(entry[1], null, 2)}</code>
            </pre>
          )
        )}
      </div>
    </div>
  );
}

export default App;