import os
from dotenv import dotenv_values
config = dotenv_values()
os.environ["ALPACA_KEY_ID"] = config["ALPACA_KEY_ID"]
os.environ["ALPACA_SECRET_KEY"] = config["ALPACA_SECRET_KEY"]

import os
from datetime import datetime
import vectorbt as vbt
import numpy as np

# Fetch historical OHLCV data for SHEL and BP PLC equities on the London Stock Exchange (LSE)
shel_data = vbt.YFData.download(
    'SHEL.LON',
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    interval='1d'
)

bp_data = vbt.YFData.download(
    'BP.LON',
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    interval='1d'
)

# Compute the entry/exit signals
def compute_signals(data):
    if data.empty:
        return np.nan * np.zeros_like(data['Close'])
    log_spread = np.log(data['Close'] / data['Close'].shift(1))
    z_score = vbt.RollingZScore.run(log_spread, window=8).zscore
    alpha = z_score * 1  # signal_scale_c_alpha is 1
    vt = B @ alpha  # Trading speed vt = Bxt
    return vt

shel_signals = compute_signals(shel_data)
bp_signals = compute_signals(bp_data)

# Run the backtest with vectorbt using the stated position sizing/cost assumptions
portfolio = vbt.Portfolio.from_signals(
    close=np.vstack((shel_data['Close'], bp_data['Close'])),
    signals=np.vstack((shel_signals, bp_signals)),
    freq='1d',
    initial_cash=100000,
    cost_model=vbt.PortfolioCostModel.slippage_and_commission(
        slippage=vbt.OptimizedSlippage.from_twap(shel_data['High'], shel_data['Low']),
        commission=vbt.Commission.flat(0.5e-4)
    )
)

# Print the resulting performance stats
print(portfolio.stats())