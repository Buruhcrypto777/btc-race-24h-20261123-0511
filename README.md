# btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/Buruhcrypto777/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/Buruhcrypto777/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A long-biased trend-riding bot that trades Coinbase Wrapped BTC (cbBTC) against USDC minute by minute on live on-chain prices. It buys with all cash after 31 bars unless the last 30 minutes fell more than 1%, rides the trend with a 2.5% trailing stop, and re-enters only on a confirmed resumption (new 120-bar high, 60-bar return of at least +0.3%, price above its 240-bar EMA). Pure Python standard library, deterministic, no network, no clock. Dev-window net PnL +$36.31 on $1,000 of paper money (1 trade, max drawdown 1.98%).

## Run it

```sh
python3 -P -s main.py
```

The bot speaks agent-fun/bars-replay/v1 (newline-delimited JSON on stdin/stdout) and is driven by the make.fun harness; `vendor/makefun_bars.py` is the kit's SDK shim.

---

Entered on [make.fun](https://make.fun/?ref=1dmvtzwc&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards
