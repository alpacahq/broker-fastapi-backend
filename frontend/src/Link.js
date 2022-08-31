import React, { Component } from "react";
import PlaidLink from "react-plaid-link";
import axios from "axios";

class Link extends Component {
  constructor() {
    super();

    this.state = {
      transactions: []
    };

    this.handleClick = this.handleClick.bind(this);
  }

  handleOnSuccess(public_token, metadata) {
    // send token to client server
    axios.post("http://localhost:8000/plaid/create_link_token", {
      public_token: public_token
    });
  }

  handleOnExit() {
    // handle the case when your user exits Link
    // For the sake of this tutorial, we're not going to be doing anything here.
  }

  handleClick(res) {
    axios.get("/transactions").then(res => {
      this.setState({ transactions: res.data });
    });
  }

  render() {
    return (
      <div>
        <PlaidLink
          clientName="React Plaid Setup"
          env="sandbox"
          product={["auth", "transactions"]}
          publicKey="add your public key here"
          onExit={this.handleOnExit}
          onSuccess={this.handleOnSuccess}
          className="test"
        >
          Open Link and connect your bank!
        </PlaidLink>
        <div>
          <button onClick={this.handleClick}>Get Transactions</button>
        </div>
      </div>
    );
  }
}

export default Link;