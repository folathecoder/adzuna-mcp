# Adzuna Jobs MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with access to the [Adzuna Job Search API](https://developer.adzuna.com/). Search for jobs, analyze salary data, and research employers across 12 countries.

## Features

- **Job Search** - Search millions of job listings with filters for location, salary, job type, and more
- **Salary Analysis** - Get salary histograms, regional comparisons, and historical trends
- **Company Research** - Find top employers by hiring volume
- **Multi-Country Support** - Access job markets in 12 countries with local currency support

## Supported Countries

| Code | Country | Currency |
|------|---------|----------|
| `gb` | United Kingdom | GBP £ |
| `us` | United States | USD $ |
| `de` | Germany | EUR € |
| `fr` | France | EUR € |
| `au` | Australia | AUD $ |
| `nz` | New Zealand | NZD $ |
| `ca` | Canada | CAD $ |
| `in` | India | INR ₹ |
| `pl` | Poland | PLN zł |
| `br` | Brazil | BRL R$ |
| `at` | Austria | EUR € |
| `za` | South Africa | ZAR R |

## Available Tools

| Tool | Description |
|------|-------------|
| `search_jobs` | Search for jobs with filters (keywords, location, salary, job type) |
| `get_categories` | Get valid job category tags for a country |
| `get_salary_histogram` | Get salary distribution data for job searches |
| `get_top_companies` | Get top employers by number of open positions |
| `get_geodata` | Get salary data broken down by geographic region |
| `get_salary_history` | Get historical salary trends over time |
| `get_api_version` | Get current Adzuna API version |

## Prerequisites

- Python 3.10+
- Adzuna API credentials (free)

## Getting Adzuna API Credentials

1. Go to [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Sign up for a free account
3. Create a new application
4. Copy your **App ID** and **App Key**

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/adzuna-mcp.git
cd adzuna-mcp
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Adzuna credentials:

```
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "command": "/path/to/adzuna-mcp/venv/bin/python",
      "args": ["/path/to/adzuna-mcp/server.py"],
      "env": {
        "ADZUNA_APP_ID": "your_app_id",
        "ADZUNA_APP_KEY": "your_app_key"
      }
    }
  }
}
```

Restart Claude Desktop after updating the configuration.

### With Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json` in your project or global config):

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "command": "/path/to/adzuna-mcp/venv/bin/python",
      "args": ["/path/to/adzuna-mcp/server.py"],
      "env": {
        "ADZUNA_APP_ID": "your_app_id",
        "ADZUNA_APP_KEY": "your_app_key"
      }
    }
  }
}
```

### With Other MCP Clients

Run the server directly:

```bash
# Activate virtual environment
source venv/bin/activate

# Run with stdio transport (default)
python server.py

# Or use FastMCP CLI
fastmcp run server.py:mcp
```

### Development Mode

FastMCP provides a dev mode with an interactive inspector:

```bash
fastmcp dev server.py
```

This opens a browser-based UI to test your tools.

## Example Prompts

Once connected, you can ask your AI assistant:

**Job Search:**
- "Find software engineer jobs in London paying over £60,000"
- "Search for remote Python developer positions in the US"
- "Show me data science jobs in Germany"

**Salary Research:**
- "What's the typical salary for a machine learning engineer in the UK?"
- "Compare software engineer salaries between London and Manchester"
- "How have data scientist salaries changed over the past year?"

**Company Research:**
- "Which companies are hiring the most software engineers in London?"
- "Show me the top employers for finance jobs in New York"

## Tool Details

### search_jobs

Search for jobs with comprehensive filtering:

```
Parameters:
- country (required): Country code (e.g., "gb", "us")
- keywords: Search terms (e.g., "python developer")
- location: City, region, or postal code
- page: Page number (starts at 1)
- results_per_page: Results per page (max 50)
- salary_min/salary_max: Annual salary filter
- full_time/part_time/contract/permanent: Job type filters
- category: Category tag from get_categories
- sort_by: "date", "salary", or "relevance"
- max_days_old: Maximum listing age in days
```

### get_categories

Get valid category tags before searching:

```
Parameters:
- country (required): Country code

Returns category tags like "it-jobs", "engineering-jobs", "finance-jobs"
```

### get_salary_histogram

Understand salary distribution:

```
Parameters:
- country (required): Country code
- keywords: Filter by job type
- location: Filter by location
- category: Filter by category
```

### get_top_companies

Find major employers:

```
Parameters:
- country (required): Country code
- keywords: Filter by job type
- location: Filter by location
- category: Filter by category
```

### get_geodata

Compare salaries across regions:

```
Parameters:
- country (required): Country code
- keywords: Filter by job type
- location: Focus on sub-regions
- category: Filter by category
```

### get_salary_history

Analyze salary trends:

```
Parameters:
- country (required): Country code
- keywords: Filter by job type
- location: Filter by location
- category: Filter by category
- months: Months of history (default 12, max ~24)
```

## Important Notes

- **Salaries are annual amounts** in the local currency of the selected country
- **Call `get_categories` first** to get valid category tags for your country
- **Many jobs don't list salaries** - salary filters will exclude these jobs
- **Rate limits apply** - the Adzuna API has usage limits on free tier

## Project Structure

```
adzuna-mcp/
├── server.py           # Main MCP server
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── .env                # Your credentials (gitignored)
├── .gitignore
└── README.md
```

## Troubleshooting

### Server not appearing in Claude Desktop

1. Check the Python path is correct in your config
2. Ensure the virtual environment has all dependencies installed
3. Restart Claude Desktop completely (Cmd+Q / Alt+F4)
4. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`

### Authentication errors

1. Verify your API credentials at [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Check the `.env` file has correct values
3. Ensure environment variables are passed in the MCP config

### No results returned

1. Try broader search terms
2. Check the country code is valid
3. Remove salary filters (many jobs don't list salaries)
4. Verify the category tag is valid for that country

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Adzuna](https://www.adzuna.com/) for providing the job search API
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework
- [Anthropic](https://www.anthropic.com/) for the Model Context Protocol specification
