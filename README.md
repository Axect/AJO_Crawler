# Physics Postdoc Positions Crawler

This project crawls Academic Jobs Online for postdoctoral positions in physics and related fields, processes the data, and generates a user-friendly HTML page to display the results.

## Features

- Crawls Academic Jobs Online for postdoctoral positions containing keywords: physics, artificial, natural
- Extracts detailed information about each position
- Processes and cleans the data
- Generates an interactive HTML page for easy browsing of positions

## Scripts

1. `crawling.py`: Crawls the website and saves raw data
2. `post_process.py`: Processes and cleans the crawled data
3. `render.py`: Generates an HTML page from the processed data
4. `main.py`: Orchestrates the execution of the above scripts in sequence

## Requirements

- Python 3.x
- Required Python packages:
  - requests
  - beautifulsoup4
  - jinja2

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Axect/AJO_Crawler
   cd AJO_Crawler
   ```

2. Install required packages:
   ```
   pip install requests beautifulsoup4 jinja2
   ```

## Usage

Run the main script:

```
python main.py
```

This will execute the crawling, processing, and rendering steps in sequence. The final output will be an HTML file named `physics_postdocs_positions.html`.

## Output

- `data/physics_postdocs.json`: Raw crawled data
- `data/physics_postdocs_updated.json`: Processed data
- `physics_postdocs_positions.html`: Final HTML output for browsing positions

## Features of the HTML Output

- Filter positions by application materials
- Include/exclude fellowships
- Sort by deadline or country
- Mark favorite positions
- Toggle between list and table views

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/physics-postdoc-crawler/issues) if you want to contribute.

## License

[MIT](LICENSE)

## Disclaimer

This tool is for educational purposes only. Please respect the terms of service of the websites you are crawling.
