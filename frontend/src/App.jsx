import React, { useState, useEffect, useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import SubmissionForm from "./components/submission_form"
import "./App.scss";

function App(props) {
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Hardcode this in because we don't have a full frontend
  const cognito_token = "eyJraWQiOiJcL0Fia01US1h1UitIVmtsb0N2SE1PdVJ0NXJZZStvY1VxRThFNEJMeVNBdz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiZDc0NjVhMy01N2MyLTQ1NDctYjY4ZC05MWZmM2MzYTljN2YiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9aaEhESllMNWMiLCJjbGllbnRfaWQiOiIybmx2NGdvMWpjMWE3ajV1ZXFiNWsxcnYxaSIsIm9yaWdpbl9qdGkiOiJhMjUzZTVjMC1mMGY4LTQwNmItOWY1My1hYmQ1MzQxYWQ4ZmQiLCJldmVudF9pZCI6IjJiNTU1NTgwLWUzODQtNGM1NS1hZGI1LWZhOTI3ZTdmODJmOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NjIwNTc2MzIsImV4cCI6MTY2MjA2MTIzMiwiaWF0IjoxNjYyMDU3NjMyLCJqdGkiOiJiYzU2MmJiMy0xYjJiLTQ4MjQtYjhmMC02NThkYmZkNTMwYmQiLCJ1c2VybmFtZSI6ImJkNzQ2NWEzLTU3YzItNDU0Ny1iNjhkLTkxZmYzYzNhOWM3ZiJ9.f6cCsiPbVMHWFUMH8nN9MjXEJMqrrZaxYmOvgBK7N2KlohP6_DtKpeRHoHqkxUVzZ6_yWC28My5oPoYhg1zXNNjmNwh8unOECBgcBaeD0KZQPR08yqbYxeC0hw5h959faFYq9fjPwPOAbzuIG4jh2CeCR9OVGEuLTaRalM23Lef4GMAyVC73qVX9Bk4uHSQ93VJ7BTaIt9zykK2gKoQc0VpVLHyu2welnPE0ZjHmUT5Mc2UkJY9j8L6j8RLi05eQnWfz2ldgCSRGWbdELtxCBouHVfqbfqeYf-94GmVyRqpreFt5EyclO2HXbqYcpKuYX7m7oVDEMoAzrSmtFR73Cg"

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