from futures_claude_client import FuturesClaudeClient
from futures_mcp_client import FuturesMCPClient
from futures_config import *
from futures_backtester import FuturesBacktester
from futures_backtester import generate_futures_data
from futures_session_monitor import SessionMonitor

# Define a class for managing futures trading strategies
class FuturesTradingManager:
    def __init__(self, config_file):
        # Load configuration
        self.config = self.load_config(config_file)

        # Initialize clients
        self.claude_client = FuturesClaudeClient(self.config['claude_api_key'])
        self.mcp_client = FuturesMCPClient(self.config['mcp_api_url'])

        # Initialize backtester
        self.backtester = FuturesBacktester(self.config['backtester_settings'])

        # Initialize session monitor
        self.session_monitor = SessionMonitor(self.config['session_monitor_settings'])

    def load_config(self, config_file):
        # In a real application, this would load from a file (e.g., JSON, YAML)
        # For demonstration, we'll use the imported config
        return futures_config.config_data

    def run_backtest(self, strategy_params):
        # Generate data for backtesting
        backtest_data = generate_futures_data(self.config['data_generation_params'])

        # Run the backtest
        results = self.backtester.run(backtest_data, strategy_params)
        return results

    def monitor_session(self):
        # Monitor the trading session
        status = self.session_monitor.check_status()
        return status

    def execute_trade(self, trade_details):
        # Execute a trade using MCP client
        response = self.mcp_client.execute_order(trade_details)
        return response

    def get_market_data(self, symbol):
        # Get market data using Claude client
        data = self.claude_client.get_latest_data(symbol)
        return data

# Example usage:
if __name__ == "__main__":
    # Assuming futures_config.config_data is available and populated
    # Example:
    # futures_config.config_data = {
    #     'claude_api_key': 'YOUR_CLAUDE_API_KEY',
    #     'mcp_api_url': 'http://example.com/mcp',
    #     'backtester_settings': {'start_date': '2023-01-01', 'end_date': '2023-12-31'},
    #     'session_monitor_settings': {'check_interval': 60},
    #     'data_generation_params': {'num_data_points': 1000}
    # }

    trading_manager = FuturesTradingManager('futures_config.py') # Passing the config file name

    # Example: Run a backtest
    strategy_parameters = {'moving_average_period': 20}
    backtest_results = trading_manager.run_backtest(strategy_parameters)
    print("Backtest Results:", backtest_results)

    # Example: Monitor session
    session_status = trading_manager.monitor_session()
    print("Session Status:", session_status)

    # Example: Execute a trade
    trade_info = {'symbol': 'BTC-USD', 'amount': 0.1, 'side': 'buy'}
    trade_response = trading_manager.execute_trade(trade_info)
    print("Trade Execution Response:", trade_response)

    # Example: Get market data
    market_data = trading_manager.get_market_data('ETH-USD')
    print("Market Data:", market_data)