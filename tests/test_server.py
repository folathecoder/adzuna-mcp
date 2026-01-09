"""
Tests for the Adzuna MCP Server.

These tests use mocked HTTP responses to avoid hitting the real API.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set test environment variables before importing server
os.environ["ADZUNA_APP_ID"] = "test_app_id"
os.environ["ADZUNA_APP_KEY"] = "test_app_key"

# Import after setting env vars
from server import (
    BASE_URL,
    SUPPORTED_COUNTRIES,
    get_auth_params,
    make_request,
)


class TestAuthParams:
    """Test authentication parameter handling."""

    def test_get_auth_params_returns_credentials(self):
        """Auth params should include app_id and app_key."""
        params = get_auth_params()
        assert "app_id" in params
        assert "app_key" in params
        assert params["app_id"] == "test_app_id"
        assert params["app_key"] == "test_app_key"


class TestSupportedCountries:
    """Test country configuration."""

    def test_all_countries_present(self):
        """All 12 supported countries should be configured."""
        expected_countries = [
            "gb",
            "us",
            "de",
            "fr",
            "au",
            "nz",
            "ca",
            "in",
            "pl",
            "br",
            "at",
            "za",
        ]
        for country in expected_countries:
            assert country in SUPPORTED_COUNTRIES

    def test_country_count(self):
        """Should have exactly 12 supported countries."""
        assert len(SUPPORTED_COUNTRIES) == 12

    def test_countries_have_currency_info(self):
        """Each country should have currency information."""
        for description in SUPPORTED_COUNTRIES.values():
            # Description should contain currency symbol or code
            assert any(c in description for c in ["$", "£", "€", "₹", "R", "zł"])


class TestBaseUrl:
    """Test API base URL configuration."""

    def test_base_url_is_https(self):
        """Base URL should use HTTPS."""
        assert BASE_URL.startswith("https://")

    def test_base_url_points_to_adzuna(self):
        """Base URL should point to Adzuna API."""
        assert "adzuna.com" in BASE_URL


class TestMakeRequest:
    """Test the HTTP request helper function."""

    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Successful API request should return JSON data."""
        mock_response_data = {"count": 100, "results": []}

        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        # Create mock client that returns mock response
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        # Mock the AsyncClient context manager
        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/gb/search/1", {"what": "python"})

            assert result == mock_response_data
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_includes_auth(self):
        """Request should include authentication parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            await make_request("jobs/gb/search/1")

            # Check that auth params were included
            call_kwargs = mock_client.get.call_args[1]
            assert "app_id" in call_kwargs["params"]
            assert "app_key" in call_kwargs["params"]

    @pytest.mark.asyncio
    async def test_make_request_error_raises_exception(self):
        """Failed API request should raise an exception with details."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"display": "Invalid credentials"}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(Exception) as exc_info:
                await make_request("jobs/gb/search/1")

            assert "API Error 401" in str(exc_info.value)
            assert "Invalid credentials" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self):
        """Rate limit error should be properly reported."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"display": "Too many requests"}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(Exception) as exc_info:
                await make_request("jobs/gb/search/1")

            assert "API Error 429" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_builds_correct_url(self):
        """Request should build the correct URL from endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            await make_request("jobs/gb/categories")

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            assert f"{BASE_URL}/jobs/gb/categories" == url

    @pytest.mark.asyncio
    async def test_make_request_merges_params(self):
        """Request should merge custom params with auth params."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            await make_request("jobs/gb/search/1", {"what": "python", "where": "London"})

            call_kwargs = mock_client.get.call_args[1]
            params = call_kwargs["params"]

            # Check custom params
            assert params["what"] == "python"
            assert params["where"] == "London"

            # Check auth params still present
            assert "app_id" in params
            assert "app_key" in params


class TestEndpointBuilding:
    """Test that endpoints are built correctly for different tools."""

    @pytest.mark.asyncio
    async def test_search_endpoint_format(self):
        """Search endpoint should include country and page."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 0, "results": []}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            await make_request("jobs/us/search/5")

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            assert "jobs/us/search/5" in url

    @pytest.mark.asyncio
    async def test_categories_endpoint_format(self):
        """Categories endpoint should include country."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            await make_request("jobs/de/categories")

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            assert "jobs/de/categories" in url

    @pytest.mark.asyncio
    async def test_histogram_endpoint_format(self):
        """Histogram endpoint should include country."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"histogram": {}}

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            await make_request("jobs/fr/histogram")

            call_args = mock_client.get.call_args
            url = call_args[0][0]
            assert "jobs/fr/histogram" in url


class TestResponseParsing:
    """Test that responses are properly parsed."""

    @pytest.mark.asyncio
    async def test_search_response_structure(self):
        """Search response should contain count and results."""
        mock_response_data = {
            "count": 150,
            "results": [
                {
                    "id": "12345",
                    "title": "Software Engineer",
                    "company": {"display_name": "Tech Corp"},
                    "location": {"display_name": "London"},
                    "salary_min": 50000,
                    "salary_max": 70000,
                    "redirect_url": "https://www.adzuna.co.uk/...",
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/gb/search/1")

            assert "count" in result
            assert "results" in result
            assert result["count"] == 150
            assert len(result["results"]) == 1
            assert result["results"][0]["title"] == "Software Engineer"

    @pytest.mark.asyncio
    async def test_categories_response_structure(self):
        """Categories response should contain results with tag and label."""
        mock_response_data = {
            "results": [
                {"tag": "it-jobs", "label": "IT Jobs"},
                {"tag": "engineering-jobs", "label": "Engineering Jobs"},
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/gb/categories")

            assert "results" in result
            assert len(result["results"]) == 2
            assert result["results"][0]["tag"] == "it-jobs"

    @pytest.mark.asyncio
    async def test_histogram_response_structure(self):
        """Histogram response should contain salary buckets."""
        mock_response_data = {
            "histogram": {
                "30000": 100,
                "40000": 250,
                "50000": 300,
            }
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/gb/histogram")

            assert "histogram" in result
            assert "30000" in result["histogram"]
            assert result["histogram"]["40000"] == 250

    @pytest.mark.asyncio
    async def test_top_companies_response_structure(self):
        """Top companies response should contain leaderboard."""
        mock_response_data = {
            "leaderboard": [
                {"canonical_name": "Google", "count": 500, "average_salary": 95000},
                {"canonical_name": "Amazon", "count": 400, "average_salary": 85000},
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/us/top_companies")

            assert "leaderboard" in result
            assert len(result["leaderboard"]) == 2
            assert result["leaderboard"][0]["canonical_name"] == "Google"

    @pytest.mark.asyncio
    async def test_geodata_response_structure(self):
        """Geodata response should contain locations."""
        mock_response_data = {
            "locations": [
                {
                    "location": {"display_name": "London", "area": ["UK", "London"]},
                    "count": 5000,
                    "average_salary": 65000,
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/gb/geodata")

            assert "locations" in result
            assert result["locations"][0]["location"]["display_name"] == "London"

    @pytest.mark.asyncio
    async def test_history_response_structure(self):
        """History response should contain monthly salary data."""
        mock_response_data = {
            "month": [
                {"month": "2024-01", "salary": 52000},
                {"month": "2024-02", "salary": 53000},
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("server.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_async_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await make_request("jobs/gb/history")

            assert "month" in result
            assert len(result["month"]) == 2
            assert result["month"][0]["month"] == "2024-01"
