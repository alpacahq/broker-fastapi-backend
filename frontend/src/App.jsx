import React, { useState, useEffect, useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import "./App.scss";

function App(props) {
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Hardcode in these values for now
  const cognito_token = "eyJraWQiOiJcL0Fia01US1h1UitIVmtsb0N2SE1PdVJ0NXJZZStvY1VxRThFNEJMeVNBdz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJkMWQ0ZjYyMS1jMjFmLTQ0NGQtYTk4Zi1jZDllZDg5MTQ1YTQiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9aaEhESllMNWMiLCJjbGllbnRfaWQiOiIybmx2NGdvMWpjMWE3ajV1ZXFiNWsxcnYxaSIsIm9yaWdpbl9qdGkiOiI3OTJmY2I5YS0zY2JhLTRlYWQtYmNhZC1iOTE4YTlkM2ZkM2UiLCJldmVudF9pZCI6IjM4ZGJiZmQxLTFiZTItNDQzZS04ZWU5LWFhM2Y5Y2EzNTZlYSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NjE5NjU5MDIsImV4cCI6MTY2MTk2OTUwMiwiaWF0IjoxNjYxOTY1OTAyLCJqdGkiOiI2Mzc0ZjYwMS00M2MyLTQyN2ItODQ2Mi02NmVhZmQyNmQ4YWEiLCJ1c2VybmFtZSI6ImQxZDRmNjIxLWMyMWYtNDQ0ZC1hOThmLWNkOWVkODkxNDVhNCJ9.qKyT26ecWIbiMPWz7txRdj39nRvoY0azG-ZsPBvRXLmZduxHxK-PnsCQffxf-FAxwt-jwCpDLMHdhhCUV61morjebwkx2uHCqhLIu3tNQmfJq4Pqpa195nGLxXO2m2z7iuHP1xvOVkvbwgrHiF8Uv6R_U8q1TmEzl50OLlBr6-AYueixyRNc1pmLbTcAVXSvVTFLHktB-BQLjpE3yhYjtLZD2N7c1emW41hP_HIgLDQUAlsaDmWdnRiGtYYeZKn5VI4dcfhiBQHeSyyWmmKQ5Q8FpxtDAZ3-F0fNnk89pCdckYpGBlrzm7eV-ZedhdpTCiZ_fBs5FJ0WvRuZrIzVGQ"
  const user_identifier = "helluva@test.ca"

  const onSuccess = useCallback(async (publicToken, metadata) => {
    console.log("onSuccess is called")
    console.log(`publicToken: ${publicToken}`)
    console.log(`accounts: ${JSON.stringify(metadata.accounts)}`)
    const firstAccountID = metadata.accounts[0].id
    console.log(firstAccountID)
    setLoading(true);
    await fetch("http://localhost:8000/plaid/exchange_public_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "access-token": cognito_token,
      },
      body: JSON.stringify({ public_token: publicToken, account_id: firstAccountID }),
    });
    // await getBalance();
  }, []);

  // Creates a Link token
  const createLinkToken = React.useCallback(async () => {
    // For OAuth, use previously generated Link token
    if (window.location.href.includes("?oauth_state_id=")) {
      const linkToken = localStorage.getItem('link_token');
      setToken(linkToken);
    } else {
      console.log("Making post request for link token")
      const response = await fetch("http://localhost:8000/plaid/create_link_token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "access-token": cognito_token,
        },
        body: JSON.stringify({ identifier: user_identifier})
      });
      console.log("Got token, here's data:")
      const data = await response.json();
      console.log(JSON.stringify(data))
      const linkToken = data.link_token.link_token
      setToken(linkToken);
      localStorage.setItem("link_token", linkToken);
      // setToken(data.link_token);
      // localStorage.setItem("link_token", data.link_token);
    }
  }, [setToken]);

  // Fetch balance data
  // const getBalance = React.useCallback(async () => {
  //   setLoading(true);
  //   const response = await fetch("/api/balance", {});
  //   const data = await response.json();
  //   setData(data);
  //   setLoading(false);
  // }, [setData, setLoading]);

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
      console.log('Creating link token')
      createLinkToken();
    }
    if (isOauth && ready) {
      console.log('Opening link')
      open();
    }
  }, [token, isOauth, ready, open]);
  
  return (
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
  );
}

export default App;