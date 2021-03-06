from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from cryptofeed_werks.constants import Exchange

from .base import BaseViewTest


class TradeViewTest(BaseViewTest):
    def get_url(self, exchange: Exchange = Exchange.FTX) -> str:
        """Get URL."""
        return reverse("trades", kwargs={"exchange": exchange})

    @patch("cryptofeed_werks.views.trades.api")
    def test_exchange_default_all_symbols(self, mock_command):
        """If no symbol, default all symbols."""
        params = self.get_symbols(["test-1", "test-2"])

        self.client.get(self.url)

        mock_symbols = self.get_mock_symbols(mock_command)
        self.assertEqual(params["symbol"], mock_symbols)

    @patch("cryptofeed_werks.views.trades.api")
    def test_one_symbol(self, mock_command):
        """One symbol."""
        self.get_symbols("test-1")
        params = self.get_symbols("test-2")

        self.client.get(self.url, params)

        mock_symbols = self.get_mock_symbols(mock_command)
        self.assertEqual(params["symbol"], mock_symbols)

    def test_nonexistant_exchange(self):
        """Exchange does not exist."""
        url = self.get_url("test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistant_symbol(self):
        """Symbol does not exist."""
        response = self.client.get(self.url, {"symbol": "test"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
