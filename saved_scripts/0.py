import os
from dotenv import dotenv_values
config = dotenv_values()
os.environ["ALPACA_KEY_ID"] = config["ALPACA_KEY_ID"]
os.environ["ALPACA_SECRET_KEY"] = config["ALPACA_SECRET_KEY"]
import os
from datetime import datetime
import vectorbt as vbt

# Fetch historical data for SHEL and BP PLC on LSE
shel_data = vbt.AlpacaData.download(
    'SHEL.LON',
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    timeframe='1D',  # Corrected the timeframe to a valid value
    api_key=os.environ["ALPACA_KEY_ID"],
    secret_key=os.environ["ALPACA_SECRET_KEY"],
    feed='iex',
    limit=None,
)

bp_data = vbt.AlpacaData.download(
    'BP.LON',
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    timeframe='1D',  # Corrected the timeframe to a valid value
    api_key=os.environ["ALPACA_KEY_ID"],
    secret_key=os.environ["ALPACA_SECRET_KEY"],
    feed='iex',
    limit=None,
)

# Concatenate the data
data = shel_data.merge(bp_data, keys=['SHEL', 'BP'])

# Compute log spreads and z-scores
log_spreads = np.log(data.close['SHEL']) - np.log(data.close['BP'])
z_scores = vbt.RollingZScore.run(log_spreads, window=8).zscore

# Define the predictive signal αt = Kxt
alpha_t = z_scores * 1  # Signal scale c_alpha is 1

# Define the trading speed vt = Bxt
vt = alpha_t * np.array([10**-1, 10**-2])  # Temporary impact matrix Lambda_tilde

# Define the position sizing (shares per unit time)
position_sizing = vt

# Define the cost assumptions
proportional_spread_cost = 0.5e-4  # 0.5 basis points per unit of traded notional

# Run the backtest using vectorbt's Portfolio.from_signals method
portfolio = vbt.Portfolio.from_signals(
    close=data.close,
    signals=alpha_t > 0,  # Entry rule: trade when αt is positive
    short_signals=alpha_t < 0,  # Exit rule: no explicit discrete exit rule
    position_sizing=position_sizing,
    cost_model=vbt.PortfolioCostModel(
        slippage_model='linear',
        slippage_coef=proportional_spread_cost,
        commission_model='flat',
        commission_coef=0.001  # Assuming a flat commission of 0.1%
    ),
    cash_sharing=True
)

# Print the resulting performance stats
print(portfolio.stats())