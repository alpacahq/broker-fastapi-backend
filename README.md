# broker-fastapi-backend
A Python reference backend for Alpaca's Broker API utilizing FastAPI.

[Implemented features](https://alpaca.markets/docs/python-sdk/broker.html#broker):

- [x] Database (PostgreSQL)
- [x] Accounts API
- [x] Funding API
- [x] Plaid API integration
- [x] Journals API
- [ ] Trading API

## How to run the backend server
1. Start up your database if applicable
2. Navigate to the root of this project
3. Run `uvicorn backend.main:app --reload`
4. Server will now be running on `http://127.0.0.1:8000`
