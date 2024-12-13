# Help Website Q&A Agent

An AI-powered question-answering agent that processes help website documentation and answers user queries using Claude Haiku.

## Features

- Crawls and processes help website documentation
- Handles different content types (text, lists, tables)
- Maintains documentation hierarchy and context
- Provides accurate answers with source references
- Clearly indicates when information is not available
- Thread-based concurrent crawling
- Robust error handling

## Requirements

- Python 3.8+
- Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd help-website-qa
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key'
```

## Usage

Run the agent with a help website URL:
```bash
python qa_agent.py --url https://help.example.com
```

The agent will:
1. Crawl and process the documentation
2. Start an interactive question-answering session
3. Provide answers based on the processed documentation

Example interaction:
```
Initializing agent with URL: https://help.example.com
Documentation processed. Ready for questions!

Enter your question (or 'quit' to exit): What integrations are available?
Answer: [Agent provides answer with source references]

Enter your question (or 'quit' to exit): quit
Exiting...
```

## Design Decisions

1. **Content Processing**
   - Uses BeautifulSoup for HTML parsing
   - Filters out navigation elements, headers, and footers
   - Maintains document structure and hierarchy
   - Chunks content for efficient processing

2. **Concurrent Crawling**
   - Implements ThreadPoolExecutor for parallel processing
   - Respects domain boundaries
   - Handles rate limiting and timeouts

3. **Claude Integration**
   - Uses Claude Haiku for fast, efficient responses
   - Structures prompts to maintain context
   - Includes source references in answers

4. **Error Handling**
   - Comprehensive error handling for network issues
   - Graceful degradation for unsupported websites
   - Clear feedback for users

## Limitations

1. **Content Access**
   - Cannot access JavaScript-rendered content
   - Limited to publicly accessible pages
   - May be blocked by some websites' robots.txt

2. **Processing**
   - Memory usage scales with documentation size
   - Processing time depends on site structure
   - May require site-specific content extraction rules

3. **Answer Generation**
   - Limited by Claude Haiku's context window
   - Answers based only on processed documentation
   - May not handle complex queries requiring multiple context pieces

## Future Improvements

1. **Technical Enhancements**
   - Implement caching mechanism
   - Add support for JavaScript-rendered content
   - Improve content chunking strategy

2. **Features**
   - Add support for multiple documentation sources
   - Implement confidence scores
   - Add API endpoint
   - Docker containerization

3. **Performance**
   - Optimize crawling strategy
   - Implement better content filtering
   - Add result caching

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Test cases cover:
- URL validation
- Content extraction
- Question answering
- Error handling
- Performance benchmarks

## Dependencies

- anthropic-sdk
- beautifulsoup4
- requests
- pytest (for testing)

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
