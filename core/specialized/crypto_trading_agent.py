import os
import logging
from typing import Dict, Any
try:
    import ccxt
except ImportError:
    logging.warning("ccxt not found. Please install via: python -m pip install ccxt")
    ccxt = None

class CryptoTradingAgent:
    """
    JARVIS Specialized Swarm Member: The Algorithmic Trader.
    Connects to live cryptocurrency exchanges (Binance, Coinbase) via CCXT
    to read market data, check wallet balances, and execute buy/sell orders.
    """
    
    def __init__(self, exchange_id: str = "binance", sandbox_mode: bool = True):
        self.sandbox_mode = sandbox_mode
        self.exchange_id = exchange_id
        
        # Load API keys securely from environment variables
        self.api_key = os.getenv("CRYPTO_API_KEY", "MOCK_KEY")
        self.api_secret = os.getenv("CRYPTO_API_SECRET", "MOCK_SECRET")
        
        if not ccxt:
            logging.error("[Crypto Agent] CCXT library missing. Operating in dry-run mode.")
            self.exchange = None
            return

        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            self.exchange = exchange_class({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
            })
            
            # Use testnet if in sandbox mode
            if self.sandbox_mode and 'test' in self.exchange.urls:
                self.exchange.set_sandbox_mode(True)
                logging.info(f"[Crypto Agent] Initialized {self.exchange_id.upper()} in SANDBOX Mode.")
            else:
                logging.warning(f"[Crypto Agent] 🚨 LIVE TRADING ENABLED on {self.exchange_id.upper()}!")
                
        except AttributeError:
            logging.error(f"[Crypto Agent] Invalid exchange ID: {self.exchange_id}")
            self.exchange = None

    def fetch_market_price(self, symbol: str = "BTC/USDT") -> float:
        """Fetches the current live market price for a given crypto symbol."""
        if not self.exchange: return 0.0
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            logging.info(f"[Crypto Agent] Live Price for {symbol}: ${current_price}")
            return current_price
        except Exception as e:
            logging.error(f"[Crypto Agent] Failed to fetch price for {symbol}: {e}")
            return 0.0

    def check_wallet_balance(self, currency: str = "USDT") -> float:
        """Fetches the available balance of a specific currency in the connected wallet."""
        if not self.exchange: return 0.0
        try:
            balance = self.exchange.fetch_balance()
            free_balance = balance.get(currency, {}).get('free', 0.0)
            logging.info(f"[Crypto Agent] Available {currency} Balance: {free_balance}")
            return free_balance
        except Exception as e:
            logging.error(f"[Crypto Agent] Failed to fetch balance: {e}")
            return 0.0

    def execute_market_order(self, symbol: str, order_type: str, amount: float) -> Dict[str, Any]:
        """
        Executes a live market Buy or Sell order.
        order_type must be 'buy' or 'sell'.
        """
        if not self.exchange:
            return {"status": "error", "message": "Exchange not connected or CCXT missing."}
            
        logging.info(f"[Crypto Agent] Attempting to {order_type.upper()} {amount} of {symbol}...")
        
        try:
            order = self.exchange.create_market_order(symbol, order_type, amount)
            logging.info(f"💰 [Crypto Agent] TRADE SUCCESSFUL: {order}")
            return {"status": "success", "order_details": order}
        except Exception as e:
            logging.error(f"❌ [Crypto Agent] TRADE FAILED: {e}")
            return {"status": "failed", "error": str(e)}
