from datetime import datetime

import httpx
import pandas as pd
from pandas import DataFrame

from cryptofeed_werks.lib import candles_to_data_frame

from .candles import get_candles
from .constants import S3_URL


class BybitMixin:
    """Bybit mixin."""

    def get_candles(
        self, timestamp_from: datetime, timestamp_to: datetime
    ) -> DataFrame:
        """Get candles from Exchange API."""
        candles = get_candles(
            self.symbol.api_symbol,
            timestamp_from,
            timestamp_to,
            interval="1",
            limit=60,
            log_format=f"{self.log_format} validating",
        )
        return candles_to_data_frame(timestamp_from, timestamp_to, candles)


class BybitS3Mixin(BybitMixin):
    """Bybit S3 mixin."""

    def get_url(self, date):
        """Get URL."""
        symbol = self.symbol.api_symbol
        directory = f"{S3_URL}{symbol}/"
        response = httpx.get(directory)
        if response.status_code == 200:
            return f"{S3_URL}{symbol}/{symbol}{date.isoformat()}.csv.gz"
        else:
            print(f"{symbol}: No data")

    def parse_dtypes_and_strip_columns(self, data_frame: DataFrame) -> DataFrame:
        """Parse dtypes and strip unnecessary columns."""
        data_frame["timestamp"] = pd.to_datetime(data_frame["timestamp"], unit="s")
        # Bybit is reversed.
        # data_frame = data_frame.iloc[::-1]
        # data_frame["index"] = data_frame.index.values[::-1]
        first_row = data_frame.iloc[0]
        last_row = data_frame.iloc[-1]
        assert first_row.timestamp < last_row.timestamp
        data_frame = data_frame.rename(columns={"trdMatchID": "uid", "size": "volume"})
        return super().parse_dtypes_and_strip_columns(data_frame)
