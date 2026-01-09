"""
Adzuna Job Search MCP Server

This MCP server provides tools to search for jobs and get salary data
using the Adzuna API.
"""

import os
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import Optional

load_dotenv()

BASE_URL = "https://api.adzuna.com/v1/api"

# Supported countries with their currencies (ISO 3166-1 alpha-2 codes)
SUPPORTED_COUNTRIES = {
    "gb": "United Kingdom (GBP £)",
    "us": "United States (USD $)",
    "de": "Germany (EUR €)",
    "fr": "France (EUR €)",
    "au": "Australia (AUD $)",
    "nz": "New Zealand (NZD $)",
    "ca": "Canada (CAD $)",
    "in": "India (INR ₹)",
    "pl": "Poland (PLN zł)",
    "br": "Brazil (BRL R$)",
    "at": "Austria (EUR €)",
    "za": "South Africa (ZAR R)",
}

# Get API credentials from environment variables
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Validate credentials are set
if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    raise ValueError(
        "Missing Adzuna API credentials. "
        "Please set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file."
    )

# Create the FastMCP server instance with detailed instructions
mcp = FastMCP(
    "Adzuna Jobs",
    instructions="""
        Adzuna Jobs API - Search jobs and access labour market data across 12 countries.

        IMPORTANT NOTES:
        - All salary figures are ANNUAL amounts in LOCAL CURRENCY (GBP for UK, USD for US, EUR for Germany/France, etc.)
        - Country codes use ISO 3166-1 alpha-2 standard (e.g., "gb", "us", "de")

        SUPPORTED COUNTRIES:
        - gb: United Kingdom (GBP £)
        - us: United States (USD $)
        - de: Germany (EUR €)
        - fr: France (EUR €)
        - au: Australia (AUD $)
        - nz: New Zealand (NZD $)
        - ca: Canada (CAD $)
        - in: India (INR ₹)
        - pl: Poland (PLN zł)
        - br: Brazil (BRL R$)
        - at: Austria (EUR €)
        - za: South Africa (ZAR R)

        RECOMMENDED WORKFLOWS:
        1. Job Search: get_categories → search_jobs (get valid category tags first)
        2. Salary Research: get_salary_histogram + get_geodata + get_salary_history
        3. Company Research: get_top_companies
        """,
)


def get_auth_params():
    """Returns authentication parameters for Adzuna API calls."""
    return {"app_id": ADZUNA_APP_ID, "app_key": ADZUNA_APP_KEY}


async def make_request(endpoint: str, params: str = None) -> dict:
    """Makes an HTTP GET request to the Adzuna API."""

    auth_params = get_auth_params()

    if params:
        auth_params.update(params)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/{endpoint}", params=auth_params, timeout=30.0
        )

        if response.status_code != 200:
            error_data = response.json()
            raise Exception(
                f"API Error {response.status_code}: {error_data.get('display', 'Unknown error')}"
            )

        return response.json()


@mcp.tool
async def search_jobs(
    country: str,
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    results_per_page: int = 10,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    full_time: Optional[bool] = None,
    part_time: Optional[bool] = None,
    contract: Optional[bool] = None,
    permanent: Optional[bool] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    max_days_old: Optional[int] = None,
) -> dict:
    """
    Search for jobs on Adzuna across 12 supported countries.

    IMPORTANT: All salary figures are ANNUAL amounts in LOCAL CURRENCY.

    Args:
        country: ISO 3166-1 alpha-2 country code. Determines job market AND currency.
            Supported: "gb" (UK/GBP), "us" (USA/USD), "de" (Germany/EUR), "fr" (France/EUR),
            "au" (Australia/AUD), "nz" (New Zealand/NZD), "ca" (Canada/CAD), "in" (India/INR),
            "pl" (Poland/PLN), "br" (Brazil/BRL), "at" (Austria/EUR), "za" (South Africa/ZAR)

        keywords: Space-separated search terms matched against job title and description.
            - Terms are OR'd together (more matches = higher ranking)
            - Case insensitive
            - No boolean operators (AND/OR/NOT not supported)
            Examples: "python developer", "machine learning engineer", "senior react"

        location: Geographic filter with fuzzy matching.
            Accepts: city names, regions, postal code prefixes.
            Examples: "London", "Manchester", "SW1" (UK), "New York", "10001" (US)
            Leave empty for country-wide search. For remote jobs, include "remote" in keywords.

        page: Page number for pagination (starts at 1, not 0).

        results_per_page: Results per page (default 10, max 50).

        salary_min: Minimum ANNUAL salary filter in LOCAL CURRENCY (e.g., 50000 not 50).
            Note: Jobs without listed salaries are excluded when using this filter.

        salary_max: Maximum ANNUAL salary filter in LOCAL CURRENCY.

        full_time: Set True to show ONLY full-time jobs.

        part_time: Set True to show ONLY part-time jobs.

        contract: Set True to show ONLY contract/freelance jobs.

        permanent: Set True to show ONLY permanent positions.

        category: Job category tag from get_categories tool.
            Common tags: "it-jobs", "engineering-jobs", "finance-jobs", "sales-jobs"
            IMPORTANT: Call get_categories(country) first to get valid tags.

        sort_by: Sort order - "date" (newest first), "salary" (highest first),
            "relevance" (best match, default).

        max_days_old: Maximum age of listings in days (e.g., 7 for last week).

    Returns:
        dict: Search results containing:
            - count (int): Total matching jobs (for pagination)
            - results (list): Job listings, each with:
                - id: Unique job identifier
                - title: Job title
                - company.display_name: Employer name
                - location.display_name: Job location
                - description: Truncated job description (~150 chars)
                - redirect_url: URL to apply (via Adzuna redirect)
                - created: ISO 8601 posting date
                - salary_min, salary_max: Annual salary range (may be null)
                - salary_is_predicted: "1" if Adzuna estimated the salary from job description,
                    "0" if the employer explicitly listed the salary. Predicted salaries are
                    less reliable for negotiation.
                - contract_type: "permanent", "contract", etc.
                - contract_time: "full_time", "part_time"
                - category.tag: Category identifier

    Example response:
        {
            "count": 523,
            "results": [{
                "id": "4123456789",
                "title": "Senior Software Engineer",
                "company": {"display_name": "Tech Corp"},
                "location": {"display_name": "London"},
                "salary_min": 70000,
                "salary_max": 90000,
                "redirect_url": "https://www.adzuna.co.uk/..."
            }]
        }

    Errors:
        - Invalid country code: "API Error 400: Invalid country"
        - Invalid category: "API Error 400: Invalid category tag"
        - Rate limit exceeded: "API Error 429: Too many requests"
        - Authentication failure: "API Error 401: Invalid credentials"
    """
    # Build query parameters
    params = {"results_per_page": results_per_page}

    if keywords:
        params["what"] = keywords
    if location:
        params["where"] = location
    if salary_min:
        params["salary_min"] = salary_min
    if salary_max:
        params["salary_max"] = salary_max
    if full_time:
        params["full_time"] = "1"
    if part_time:
        params["part_time"] = "1"
    if contract:
        params["contract"] = "1"
    if permanent:
        params["permanent"] = "1"
    if category:
        params["category"] = category
    if sort_by:
        params["sort_by"] = sort_by
    if max_days_old:
        params["max_days_old"] = max_days_old

    endpoint = f"jobs/{country}/search/{page}"
    return await make_request(endpoint, params)


@mcp.tool
async def get_categories(country: str) -> dict:
    """
    Get valid job category tags for a specific country.

    PURPOSE: Use this BEFORE search_jobs to get valid 'category' parameter values.
    Category tags are COUNTRY-SPECIFIC - always use the same country code here
    as you will in search_jobs.

    Args:
        country: ISO 3166-1 alpha-2 country code.
            Supported: "gb", "us", "de", "fr", "au", "nz", "ca", "in", "pl", "br", "at", "za"

    Returns:
        dict: Contains "results" array of category objects:
            - tag: Use THIS value in search_jobs category parameter (e.g., "it-jobs")
            - label: Human-readable name for display (e.g., "IT Jobs")

    Common category tags (vary by country):
        - "it-jobs": Technology, software, IT support
        - "engineering-jobs": Mechanical, electrical, civil
        - "finance-jobs": Accounting, banking, financial services
        - "sales-jobs": Sales, business development
        - "healthcare-nursing-jobs": Medical, nursing
        - "admin-jobs": Administration, office support
        - "marketing-jobs": Marketing, PR, communications

    Example response:
        {
            "results": [
                {"tag": "it-jobs", "label": "IT Jobs"},
                {"tag": "engineering-jobs", "label": "Engineering Jobs"},
                {"tag": "finance-jobs", "label": "Accounting & Finance Jobs"}
            ]
        }

    Usage:
        categories = get_categories("gb")
        search_jobs(country="gb", category="it-jobs")  # Use tag, not label

    Errors:
        - Invalid country code: "API Error 400: Invalid country"
        - Rate limit exceeded: "API Error 429: Too many requests"
        - Authentication failure: "API Error 401: Invalid credentials"
    """
    endpoint = f"jobs/{country}/categories"
    return await make_request(endpoint)


@mcp.tool
async def get_salary_histogram(
    country: str,
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """
    Get salary distribution histogram for jobs matching search criteria.

    PURPOSE: Understand salary ranges in a job market. Useful for:
        - "What's the typical salary for X role?"
        - Salary negotiation research
        - Market positioning analysis

    IMPORTANT: Only includes jobs WITH listed salaries. Many jobs don't list salary.

    Args:
        country: ISO 3166-1 alpha-2 country code. Determines currency.
            Supported: "gb", "us", "de", "fr", "au", "nz", "ca", "in", "pl", "br", "at", "za"

        keywords: Search terms to filter jobs (e.g., "software engineer", "data scientist").

        location: Location filter (e.g., "London", "New York").

        category: Category tag from get_categories (e.g., "it-jobs").

    Returns:
        dict: Contains "histogram" object with salary buckets:
            - Keys: Salary values as strings (e.g., "30000", "35000")
            - Values: Number of jobs at that salary point

    Example response:
        {
            "histogram": {
                "25000": 89,
                "30000": 234,
                "35000": 456,
                "40000": 567,
                "45000": 489,
                "50000": 378,
                "55000": 245,
                "60000": 167
            }
        }

    How to interpret:
        - Keys are ANNUAL salaries in LOCAL CURRENCY
        - Buckets are typically £5,000 / $5,000 increments
        - Peak of distribution = most common salary
        - To find median: find salary where cumulative count reaches 50%

    Errors:
        - Invalid country code: "API Error 400: Invalid country"
        - Invalid category: "API Error 400: Invalid category tag"
        - Rate limit exceeded: "API Error 429: Too many requests"
        - Authentication failure: "API Error 401: Invalid credentials"
    """
    params = {}
    if keywords:
        params["what"] = keywords
    if location:
        params["where"] = location
    if category:
        params["category"] = category

    endpoint = f"jobs/{country}/histogram"
    return await make_request(endpoint, params)


@mcp.tool
async def get_top_companies(
    country: str,
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """
    Get top employers currently hiring, ranked by number of open positions.

    PURPOSE: Identify major employers in a field. Useful for:
        - "Which companies are hiring the most engineers?"
        - Researching potential employers
        - Understanding market leaders by hiring volume

    NOTE: Shows hiring VOLUME, not company quality. Smaller great companies may not appear.

    Args:
        country: ISO 3166-1 alpha-2 country code.
            Supported: "gb", "us", "de", "fr", "au", "nz", "ca", "in", "pl", "br", "at", "za"

        keywords: Filter to specific roles (e.g., "software engineer", "data scientist").

        location: Location filter (e.g., "London" for London-based employers).

        category: Category tag from get_categories (e.g., "it-jobs").

    Returns:
        dict: Contains "leaderboard" array of company objects:
            - canonical_name: Company name (normalized)
            - count: Number of open positions
            - average_salary: Average salary across listings (may be null)

    Example response:
        {
            "leaderboard": [
                {"canonical_name": "NHS", "count": 1245, "average_salary": 42000},
                {"canonical_name": "Amazon", "count": 567, "average_salary": 65000},
                {"canonical_name": "Google", "count": 234, "average_salary": 95000}
            ]
        }

    Notes:
        - Ranked by job count (most positions first)
        - Typically returns 10-20 companies
        - average_salary is ANNUAL in LOCAL CURRENCY (may be null)

    Errors:
        - Invalid country code: "API Error 400: Invalid country"
        - Invalid category: "API Error 400: Invalid category tag"
        - Rate limit exceeded: "API Error 429: Too many requests"
        - Authentication failure: "API Error 401: Invalid credentials"
    """
    params = {}
    if keywords:
        params["what"] = keywords
    if location:
        params["where"] = location
    if category:
        params["category"] = category

    endpoint = f"jobs/{country}/top_companies"
    return await make_request(endpoint, params)


@mcp.tool
async def get_geodata(
    country: str,
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """
    Get salary and job count data broken down by geographic region.

    PURPOSE: Compare salaries and job availability across areas. Useful for:
        - "Where are the highest paying X jobs?"
        - "Which cities have the most opportunities?"
        - Relocation decisions

    Args:
        country: ISO 3166-1 alpha-2 country code.
            Supported: "gb", "us", "de", "fr", "au", "nz", "ca", "in", "pl", "br", "at", "za"

        keywords: Filter to specific roles (e.g., "software engineer").

        location: Focus on a region for sub-area breakdown.
            - Empty: National breakdown (London, Manchester, etc.)
            - "London": Breakdown within London (City, Canary Wharf, etc.)

        category: Category tag from get_categories (e.g., "it-jobs").

    Returns:
        dict: Contains "locations" array of region objects:
            - location.display_name: Region name
            - location.area: Geographic hierarchy array
            - count: Number of jobs in region
            - average_salary: Average salary (may be null)

    Example response:
        {
            "locations": [
                {
                    "location": {"display_name": "London", "area": ["UK", "London"]},
                    "count": 15678,
                    "average_salary": 62000
                },
                {
                    "location": {"display_name": "Manchester", "area": ["UK", "Manchester"]},
                    "count": 3456,
                    "average_salary": 48000
                }
            ]
        }

    Notes:
        - Results ordered by job count (most jobs first)
        - average_salary is ANNUAL in LOCAL CURRENCY
        - Typically returns 10-20 top regions

    Errors:
        - Invalid country code: "API Error 400: Invalid country"
        - Invalid category: "API Error 400: Invalid category tag"
        - Rate limit exceeded: "API Error 429: Too many requests"
        - Authentication failure: "API Error 401: Invalid credentials"
    """
    params = {}
    if keywords:
        params["what"] = keywords
    if location:
        params["where"] = location
    if category:
        params["category"] = category

    endpoint = f"jobs/{country}/geodata"
    return await make_request(endpoint, params)


@mcp.tool
async def get_salary_history(
    country: str,
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
    months: Optional[int] = None,
) -> dict:
    """
    Get historical salary trends over time for matching jobs.

    PURPOSE: Analyze how salaries have changed. Useful for:
        - "Are X salaries going up or down?"
        - Trend analysis for negotiations
        - Market timing for job searches

    Args:
        country: ISO 3166-1 alpha-2 country code.
            Supported: "gb", "us", "de", "fr", "au", "nz", "ca", "in", "pl", "br", "at", "za"

        keywords: Filter to specific roles (e.g., "software engineer").

        location: Location filter (e.g., "London").

        category: Category tag from get_categories (e.g., "it-jobs").

        months: Number of months of history (default 12, max ~24).
            - 6: Recent trend
            - 12: Year-over-year comparison
            - 24: Longer-term view

    Returns:
        dict: Contains "month" array of data points:
            - month: Year-month string (YYYY-MM format)
            - salary: Average salary that month (annual, local currency)

    Example response:
        {
            "month": [
                {"month": "2024-01", "salary": 52000},
                {"month": "2024-02", "salary": 52500},
                {"month": "2024-03", "salary": 53000}
            ]
        }

    How to analyze:
        - Compare first vs last month for overall change
        - Calculate % change: ((last - first) / first) * 100
        - Look for consistent direction vs volatility

    Errors:
        - Invalid country code: "API Error 400: Invalid country"
        - Invalid category: "API Error 400: Invalid category tag"
        - Rate limit exceeded: "API Error 429: Too many requests"
        - Authentication failure: "API Error 401: Invalid credentials"
    """
    params = {}
    if keywords:
        params["what"] = keywords
    if location:
        params["where"] = location
    if category:
        params["category"] = category
    if months:
        params["months"] = months

    endpoint = f"jobs/{country}/history"
    return await make_request(endpoint, params)


@mcp.tool
async def get_api_version() -> dict:
    """
    Get the current Adzuna API version.

    Returns:
        API version information
    """
    return await make_request("version")


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
