"""BTC race bot: long-biased trend rider with a trailing-stop guard.

Strategy (written from scratch for this competition):
  * Wait 30 bars, then buy with all cash unless the last 30 minutes fell
    more than 1% (do not buy into a sharp sell-off at the open).
  * While long, track the highest close since entry. Sell everything the
    moment a close falls 2.5% below that peak (trailing stop). This is the
    only exit rule: it lets a rising market run and caps the loss on any
    single position at roughly the stop width plus one fill's costs.
  * After an exit, wait 60 bars, then re-enter only on a confirmed
    resumption: a new 120-bar high, a 60-bar return of at least +0.3%,
    and price above its 240-bar EMA. This keeps the bot out of a falling
    market instead of buying every small bounce.
  * One position at a time, full size (100% of cash), at most one order
    per reply. Orders fill at the next bar's open; max slippage 200 bps
    (the dev window's largest 1-minute open-vs-previous-close move was
    under 20 bps, so this only guards against freak gaps).

Only the standard library is used. All decisions come from the bars the
harness sends (closes, cash, positions); no clock, no network, no files,
no randomness, so two runs on the same data give identical replies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# --- strategy parameters (fractions / counts, not price levels) ---
ENTRY_DELAY_BARS = 31        # bars of history before the first buy: 31 so a
                             # full 30-bar return exists for the sell-off check
ENTRY_MAX_DROP_BPS = 100     # skip the first buy while the 30-bar return < -1%
TRAIL_NUM = 975              # sell when close <= peak * 975/1000 (2.5% trail)
TRAIL_DEN = 1000
REENTRY_COOLDOWN = 60        # bars to wait after an exit before re-entering
REENTRY_NBARS = 120          # re-entry needs a new high over this many bars
REENTRY_TREND_BPS = 30       # ... plus a 60-bar return of at least +0.3%
LONG_EMA_BARS = 240          # ... plus price above its 240-bar EMA
MAX_SLIPPAGE_BPS = 200       # max move from latest close we accept on a fill


class Bot:
    """Keeps the bar history and position state for one run."""

    def __init__(self):
        self.closes = []          # closes, raw price units (ints)
        self.ema_long = None      # 240-bar EMA of closes (float)
        self.peak = 0             # highest close since the current entry
        self.last_exit_bar = -10 ** 9
        self.bought_once = False

    def _return_bps(self, n):
        """Return over the last n bars, in basis points (int math)."""
        closes = self.closes
        if len(closes) <= n:
            return None
        old = closes[-n - 1]
        if old <= 0:
            return None
        return (closes[-1] - old) * 10000 // old

    def on_batch(self, state, batch):
        if state.warming_up:
            return []
        close = state.close(SYMBOL)
        if close is None:
            return []
        self.closes.append(close)
        bar_no = len(self.closes)

        # Incremental EMA of closes (float ops are deterministic).
        if self.ema_long is None:
            self.ema_long = float(close)
        else:
            k = 2.0 / (LONG_EMA_BARS + 1)
            self.ema_long = close * k + self.ema_long * (1.0 - k)

        holding = state.positions.get(SYMBOL)
        qty = holding.qty if holding is not None else 0

        if qty > 0:
            # In a position: update the peak and check the trailing stop.
            if close > self.peak:
                self.peak = close
            if close * TRAIL_DEN <= self.peak * TRAIL_NUM:
                self.last_exit_bar = bar_no
                return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []

        # Flat: do not chase for a while after an exit.
        if bar_no - self.last_exit_bar < REENTRY_COOLDOWN:
            return []
        if state.cash < 1000000:  # less than 1 USDC: nothing to buy with
            return []

        if not self.bought_once:
            if bar_no < ENTRY_DELAY_BARS:
                return []
            ret30 = self._return_bps(30)
            if ret30 is not None and ret30 < -ENTRY_MAX_DROP_BPS:
                return []  # sharp sell-off: keep waiting
            self.bought_once = True
            self.peak = close
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]

        # Re-entry: new 120-bar high, positive 60-bar trend, above long EMA.
        if bar_no < max(REENTRY_NBARS, LONG_EMA_BARS):
            return []
        if close <= max(self.closes[-REENTRY_NBARS - 1:-1]):
            return []
        ret60 = self._return_bps(60)
        if ret60 is None or ret60 < REENTRY_TREND_BPS:
            return []
        if self.ema_long is None or close <= self.ema_long:
            return []
        self.peak = close
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def main():
    bot = Bot()
    makefun_bars.run(bot.on_batch)


if __name__ == "__main__":
    main()
