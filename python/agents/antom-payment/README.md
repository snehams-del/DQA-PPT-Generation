# Antom Payment Agent

That integrates Ant International's Antom payment APIs, enabling AI assistants to handle payment and refund operations seamlessly.

## Overview

The Antom Payment Agent wraps Ant International's Antom payment APIs into standardized MCP tools, allowing AI assistants to securely process payment-related operations during conversations. With this server, you can create payment sessions, query transaction status, handle refunds, and more directly through AI interactions.

## Features

### 💳 Payment Operations
- **Create Payment Session** (`create_payment_session`): Generate payment sessions for client-side SDK integration
- **Query Payment Details** (`query_payment_detail`): Retrieve transaction status and information for submitted payment requests
- **Cancel Payment** (`cancel_payment`): Cancel payments when results are not returned within expected timeframes

### 💰 Refund Operations
- **Create Refund** (`create_refund`): Initiate full or partial refunds against successful payments
- **Query Refund Details** (`query_refund_detail`): Check refund status for previously submitted refund requests


## Setup and Installation


1.  **Prerequisites**

Before using the Antom Payment Agent, ensure you have:

- **Python 3.11 or higher**
- **uv** (recommended package manager) or **pip**
- **Valid Antom Merchant Account** with:
  - Merchant Client ID (CLIENT_ID)
  - Merchant RSA Private Key (MERCHANT_PRIVATE_KEY)
  - Alipay RSA Public Key (ALIPAY_PUBLIC_KEY)
  - Payment Redirect Return URL (PAYMENT_REDIRECT_URL)
  - Payment Notification Callback URL (PAYMENT_NOTIFY_URL)


2.  **Installation**


   ```bash
   # Clone this repository.
   git clone https://github.com/google/adk-samples.git
   cd adk-samples/python/agents/antom-payment
   # Install the package and dependencies.
   pip install poetry
   poetry install
   
   or
   uv venv 
   uv sync
   
   ```

3. **Configuration**

  You may set the following environment variables in your shell, or in a `python/agents/antom-payment/antom-payemnt-agent/.env` file instead.
   *   Set up Google Cloud credentials.

          GOOGLE_GENAI_USE_VERTEXAI
          GOOGLE_API_KEY


   *    your Antom config.


          GATEWAY_URL
          CLIENT_ID
          MERCHANT_PRIVATE_KEY
          ALIPAY_PUBLIC_KEY
          PAYMENT_REDIRECT_URL
          PAYMENT_NOTIFY_URL

## Running the Agent


**Using `adk`**


ADK provides convenient ways to bring up agents locally and interact with them.
You may talk to the agent using:

```bash
poetry run adk web
or
uv run adk web
```


**Try the following prompts:**


After running the agent, try the following example prompt

```
[user]: Create a payment link for an order called "Cream Puff" for $100 and think of a sentence describing Cream Puff.
```