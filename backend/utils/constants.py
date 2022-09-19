from alpaca.broker.enums import JournalEntryType
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

journal_entry_types = {
    "JNLC": JournalEntryType.CASH,
    "JNLS": JournalEntryType.SECURITY,
}

order_types = {
    "market": OrderType.MARKET,
    "limit": OrderType.LIMIT,
    "stop": OrderType.STOP,
    "stop_limit": OrderType.STOP_LIMIT,
    "trailing_stop": OrderType.TRAILING_STOP,
}

order_sides = {
    "buy": OrderSide.BUY,
    "sell": OrderSide.SELL,
}

time_in_forces = {
    "day": TimeInForce.DAY,
    "gtc": TimeInForce.GTC,
    "opg": TimeInForce.OPG,
    "cls": TimeInForce.CLS,
    "ioc": TimeInForce.IOC,
    "fok": TimeInForce.FOK
}