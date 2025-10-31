import os
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, parse_qs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchService:
    """
    Service for researching topics online and extracting relevant information
    """
    
    def __init__(self):
        self.search_url = "https://duckduckgo.com/html/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    async def research_topic(self, topic: str, depth: int = 3) -> Dict[str, Any]:
        """
        Research a topic by searching the web and extracting relevant information
        
        Args:
            topic: The topic to research
            depth: How many search results to analyze (1-5)
            
        Returns:
            Dictionary containing research results
        """
        logger.info(f"Researching topic: {topic}")
        
        try:
            # Search for the topic
            search_results = await self._search_web(topic, max_results=depth*3)
            
            # Extract content from top results
            content_results = []
            for result in search_results[:depth*3]:
                if result.get('url'):
                    try:
                        content = await self._extract_page_content(result['url'])
                        if content:
                            content_results.append({
                                'title': result.get('title', 'Unknown Title'),
                                'url': result['url'],
                                'summary': content[:1000],  # Truncate long content
                                'source': result.get('source', 'web')
                            })
                    except Exception as e:
                        logger.error(f"Error extracting content from {result['url']}: {str(e)}")
            
            # Compile research data
            research_data = {
                'topic': topic,
                'sources': content_results,
                'key_concepts': await self._extract_key_concepts(content_results),
                'related_topics': await self._find_related_topics(topic, search_results)
            }
            
            return research_data
            
        except Exception as e:
            logger.error(f"Error researching topic {topic}: {str(e)}")
            # Return minimal fallback data
            return {
                'topic': topic,
                'sources': [],
                'key_concepts': [],
                'related_topics': []
            }
    
    async def _search_web(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Perform a web search using DuckDuckGo
        """
        results = []
        
        try:
            # Format query for search
            search_params = {
                'q': query,
                'kl': 'us-en',
                't': 'h_'
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.search_url,
                    data=search_params,
                    headers={'User-Agent': self.user_agent},
                    follow_redirects=True # Added this line
                )
                
                if response.status_code != 200:
                    logger.error(f"Error with search request: {response.status_code}")
                    return results
                
                # Parse search results
                soup = BeautifulSoup(response.text, 'html.parser')
                result_elements = soup.select('.result')
                
                for i, result in enumerate(result_elements):
                    if i >= max_results:
                        break
                        
                    title_element = result.select_one('.result__title')
                    url_element = result.select_one('.result__url')
                    snippet_element = result.select_one('.result__snippet')
                    
                    title = title_element.get_text().strip() if title_element else "Unknown Title"
                    
                    # Extract URL from href attribute
                    url = None
                    if title_element and title_element.select_one('a'):
                        url_href = title_element.select_one('a').get('href', '')
                        # Some DDG results have redirect URLs, extract the actual URL
                        if 'duckduckgo.com/l/?' in url_href:
                            # Extract the actual URL from redirect parameter
                            parsed_url = urlparse(url_href)
                            url_params = parse_qs(parsed_url.query)
                            if 'uddg' in url_params:
                                url = url_params['uddg'][0]
                        else:
                            url = url_href
                    
                    snippet = snippet_element.get_text().strip() if snippet_element else ""
                    source = url_element.get_text().strip() if url_element else "Unknown Source"
                    
                    if url:  # Only add if we have a valid URL
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': source
                        })
                        
            return results
            
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            return results
    
    async def _extract_page_content(self, url: str) -> Optional[str]:
        """
        Extract the main content from a web page
        """
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    url, 
                    headers={'User-Agent': self.user_agent},
                    follow_redirects=True
                )
                
                if response.status_code != 200:
                    return None
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script.extract()
                
                # Get the main text content
                text = soup.get_text(separator='\n')
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
                
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None
    
    async def _extract_key_concepts(self, content_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key concepts from the research content
        This is a basic implementation - in a real app, this would use NLP techniques
        """
        # Placeholder implementation - in a real app this would use more sophisticated NLP
        key_concepts = set()
        
        for result in content_results:
            summary = result.get('summary', '')
            # Extract phrases that appear to be key concepts (simple implementation)
            if summary:
                # Split into sentences and look for definitional phrases
                sentences = summary.split('.')
                for sentence in sentences:
                    if any(phrase in sentence.lower() for phrase in [
                        ' is ', ' are ', ' refers to ', ' defined as ', ' means ', 
                        ' consists of ', ' includes '
                    ]):
                        # Clean up and add the concept
                        concept = sentence.strip()
                        if 30 < len(concept) < 200 and concept not in key_concepts:
                            key_concepts.add(concept)
        
        # Return top concepts, ordered by length (shorter is usually better)
        return sorted(list(key_concepts), key=len)[:10]
    
    async def _find_related_topics(self, main_topic: str, search_results: List[Dict[str, str]]) -> List[str]:
        """
        Extract related topics from search results
        """
        related_topics = set()
        main_words = set(main_topic.lower().split())
        
        for result in search_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # Process title for potential related topics
            title_words = title.split()
            for i in range(len(title_words)-1):
                if i < len(title_words) - 2:
                    phrase = f"{title_words[i]} {title_words[i+1]} {title_words[i+2]}"
                    if phrase.lower() not in main_topic.lower() and all(word.lower() not in main_words for word in phrase.split()):
                        related_topics.add(phrase)
                
                phrase = f"{title_words[i]} {title_words[i+1]}"
                if phrase.lower() not in main_topic.lower() and all(word.lower() not in main_words for word in phrase.split()):
                    related_topics.add(phrase)
        
        # Filter out common words and short phrases
        filtered_topics = []
        common_words = {'and', 'the', 'for', 'with', 'this', 'that', 'what', 'how', 'why'}
        
        for topic in related_topics:
            words = topic.lower().split()
            if (len(words) >= 2 and
                not any(word in common_words for word in words) and
                not all(c.isdigit() or c in '.,;:?!' for c in topic)):
                filtered_topics.append(topic.strip('.,;:?!'))
        
        return filtered_topics[:5]  # Return top 5 related topics
    
    async def get_trending_topics(self) -> List[str]:
        """
        Get trending study topics
        """
        # This would typically connect to an API or scrape from trending topics services
        # For now, returning a static list of trending topics
        trending_topics = [
            "Machine Learning and AI",
            "Data Science",
            "Cybersecurity",
            "Blockchain Technology",
            "Quantum Computing",
            "Web Development",
            "Mobile App Development",
            "Cloud Computing",
            "Digital Marketing",
            "UX/UI Design"
        ]
        
        return trending_topics
