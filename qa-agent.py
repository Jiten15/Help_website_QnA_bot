import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import anthropic
from typing import List, Dict, Set, Optional
import json
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor
import time



import os


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@dataclass
class DocumentChunk:
    """Represents a chunk of documentation content"""
    content: str
    url: str
    title: str

class DocumentProcessor:
    """Handles document crawling and processing"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.visited_urls: Set[str] = set()
        self.chunks: List[DocumentChunk] = []
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the same domain and is a valid documentation page"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(self.base_url)
            return (parsed.netloc == base_parsed.netloc and
                   not any(ext in url for ext in ['.png', '.jpg', '.css', '.js']))
        except Exception:
            return False

    def extract_content(self, soup: BeautifulSoup, url: str) -> Optional[DocumentChunk]:
        """Extract meaningful content from HTML while filtering navigation elements"""
        try:
            # Remove navigation, headers, footers
            for elem in soup.select('nav, header, footer, script, style'):
                elem.decompose()
            
            # Get main content area (adjust selectors based on common help site structures)
            main_content = soup.select_one('main, article, .content, .documentation')
            if not main_content:
                main_content = soup.select_one('body')
            
            if not main_content:
                return None
            
            title = soup.title.string if soup.title else url
            content = ' '.join(main_content.stripped_strings)
            
            return DocumentChunk(content=content, url=url, title=title)
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def crawl_page(self, url: str) -> None:
        """Crawl a single page and extract its content"""
        if url in self.visited_urls or not self.is_valid_url(url):
            return
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and store content
            chunk = self.extract_content(soup, url)
            if chunk:
                self.chunks.append(chunk)
            
            # Find and crawl links
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                self.crawl_page(next_url)
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")

    def process_documentation(self) -> None:
        """Process the entire documentation website"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.submit(self.crawl_page, self.base_url)

class QAAgent:
    """Main QA agent class that handles user interaction and Claude integration"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.processor: Optional[DocumentProcessor] = None
        
    def initialize_with_url(self, url: str) -> None:
        """Initialize the agent with a help website URL"""
        try:
            self.processor = DocumentProcessor(url)
            logger.info(f"Starting documentation processing for {url}")
            self.processor.process_documentation()
            logger.info(f"Processed {len(self.processor.chunks)} documentation chunks")
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise

    def format_context(self) -> str:
        """Format documentation chunks for context"""
        if not self.processor or not self.processor.chunks:
            return ""
        
        context = "Here is the relevant documentation:\n\n"
        for chunk in self.processor.chunks:
            context += f"Source: {chunk.url}\nTitle: {chunk.title}\nContent: {chunk.content}\n\n"
        return context

    def answer_question(self, question: str) -> str:
        """Process a user question and generate an answer using llm(claude haiku)"""
        if not self.processor:
            return "Error: Documentation not initialized. Please provide a help website URL first."

        try:
            # Prepare prompt for Claude
            prompt = f"""You are a helpful documentation assistant. Based on the provided documentation, 
            answer the following question. If the information is not available in the documentation, 
            clearly state that. Include relevant source URLs in your answer.

            Documentation Context:
            {self.format_context()}

            Question: {question}

            Please provide a clear and concise answer based solely on the documentation provided above."""

            # Get response from Claude Haiku
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

def main():
    """Main function to run the QA agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Help Website Q&A Agent')
    parser.add_argument('--url', required=True, help='Help website URL')
    args = parser.parse_args()
    

    api_key = "Place_api_key"
    os.environ['ANTHROPIC_API_KEY'] = api_key
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return
    
    # Initialize agent
    agent = QAAgent(api_key)
    
    try:
        print(f"Initializing agent with URL: {args.url}")
        agent.initialize_with_url(args.url)
        print("Documentation processed. Ready for questions!")
        
        # Interactive question-answering loop
        while True:
            question = input("\nEnter your question (or 'quit' to exit): ")
            if question.lower() == 'quit':
                break
                
            answer = agent.answer_question(question)
            print("\nAnswer:", answer)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
