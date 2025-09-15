#!/usr/bin/env python3
"""
Google Docs to Markdown Converter

This script downloads Google Docs documents and converts them to Markdown format,
while preserving images, links, and document structure.
"""

import re
import os
import base64
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import json

class GoogleDocsConverter:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.downloaded_docs = set()
        self.failed_downloads = []
        
        # Create directories
        self.base_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_document_id(self, url: str) -> Optional[str]:
        """Extract Google Docs document ID from URL."""
        if not url or 'docs.google.com' not in url:
            return None
        
        # Pattern to match document ID in various Google Docs URL formats
        patterns = [
            r'/document/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def download_as_markdown(self, doc_id: str, title: str = None) -> Optional[str]:
        """Download Google Doc as Markdown using export URL."""
        if not doc_id:
            return None
            
        # Use Google Docs export URL for markdown
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=md"
        
        try:
            print(f"Downloading document {doc_id}...")
            response = self.session.get(export_url, timeout=30)
            response.raise_for_status()
            
            # Google Docs markdown export
            markdown_content = response.text
            
            if not markdown_content or len(markdown_content) < 50:
                # Fallback to HTML if markdown is too short/empty
                html_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
                html_response = self.session.get(html_url, timeout=30)
                html_response.raise_for_status()
                
                # Convert HTML to markdown using simple conversion
                markdown_content = self.html_to_markdown_simple(html_response.text)
            
            return markdown_content
            
        except Exception as e:
            print(f"Error downloading document {doc_id}: {e}")
            self.failed_downloads.append((doc_id, str(e)))
            return None
    
    def html_to_markdown_simple(self, html_content: str) -> str:
        """Simple HTML to Markdown conversion."""
        # Basic HTML to Markdown conversion
        content = html_content
        
        # Remove style and script tags
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert headers
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', content, flags=re.IGNORECASE)
        
        # Convert links
        content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.IGNORECASE)
        
        # Convert paragraphs
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert line breaks
        content = re.sub(r'<br[^>]*/?>', '\n', content, flags=re.IGNORECASE)
        
        # Remove remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = content.strip()
        
        return content
    
    def extract_images_from_markdown(self, markdown_content: str, doc_id: str) -> str:
        """Extract base64 images from markdown and save as files."""
        if not markdown_content:
            return markdown_content
        
        # Pattern to find base64 encoded images
        base64_pattern = r'!\[([^\]]*)\]\(data:image/([^;]+);base64,([^)]+)\)'
        
        def replace_base64_image(match):
            alt_text = match.group(1)
            image_format = match.group(2)
            base64_data = match.group(3)
            
            try:
                # Decode base64 image
                image_data = base64.b64decode(base64_data)
                
                # Generate filename
                image_filename = f"{doc_id}_image_{len(os.listdir(self.images_dir)) + 1}.{image_format}"
                image_path = self.images_dir / image_filename
                
                # Save image
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # Return markdown image reference
                return f'![{alt_text}](images/{image_filename})'
                
            except Exception as e:
                print(f"Error processing image: {e}")
                return f'![{alt_text}](image_error)'
        
        # Replace all base64 images
        processed_content = re.sub(base64_pattern, replace_base64_image, markdown_content)
        return processed_content
    
    def extract_google_docs_links(self, content: str) -> List[str]:
        """Extract Google Docs links from content."""
        # Pattern to find Google Docs URLs
        pattern = r'https://docs\.google\.com/document/d/[a-zA-Z0-9-_]+[^\s\)\]\>"]*'
        links = re.findall(pattern, content)
        
        # Clean up links (remove trailing characters)
        cleaned_links = []
        for link in links:
            # Remove common trailing characters
            link = re.sub(r'[,\.\)\]"]+$', '', link)
            if link not in cleaned_links:
                cleaned_links.append(link)
        
        return cleaned_links
    
    def sanitize_filename(self, title: str) -> str:
        """Sanitize title for use as filename."""
        if not title:
            return "untitled"
        
        # Remove/replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('_')[:50]  # Limit length
        
        return filename if filename else "untitled"
    
    def extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content."""
        if not content:
            return "untitled"
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line and not line.startswith('#') and len(line) > 5:
                return line[:50]
        
        return "untitled"
    
    def download_document(self, url: str, filename: str = None) -> Optional[str]:
        """Download a single Google Doc and save as markdown."""
        doc_id = self.extract_document_id(url)
        if not doc_id:
            print(f"Could not extract document ID from: {url}")
            return None
        
        if doc_id in self.downloaded_docs:
            print(f"Document {doc_id} already downloaded, skipping...")
            return None
        
        print(f"Processing document: {url}")
        
        # Download markdown content
        markdown_content = self.download_as_markdown(doc_id)
        if not markdown_content:
            return None
        
        # Extract title if not provided
        if not filename:
            title = self.extract_title_from_content(markdown_content)
            filename = self.sanitize_filename(title)
        
        # Process images
        markdown_content = self.extract_images_from_markdown(markdown_content, doc_id)
        
        # Save to file
        file_path = self.base_dir / f"{filename}.md"
        
        # Add metadata header
        metadata = f"""---
title: "{self.extract_title_from_content(markdown_content)}"
source_url: "{url}"
document_id: "{doc_id}"
downloaded_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
---

"""
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(metadata + markdown_content)
            
            print(f"Saved: {file_path}")
            self.downloaded_docs.add(doc_id)
            
            return str(file_path)
            
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            return None
    
    def process_book_recursively(self, main_url: str) -> Dict[str, List[str]]:
        """Process the main document and all linked documents recursively."""
        print("Starting recursive processing of Google Docs book...")
        
        results = {
            'downloaded': [],
            'failed': [],
            'links_found': []
        }
        
        # Process main document first
        main_file = self.download_document(main_url, "00_table_of_contents")
        if main_file:
            results['downloaded'].append(main_file)
            
            # Read the main document to find links
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract all Google Docs links
            links = self.extract_google_docs_links(content)
            results['links_found'] = links
            
            print(f"Found {len(links)} Google Docs links to process...")
            
            # Process each linked document
            for i, link in enumerate(links, 1):
                print(f"\nProcessing link {i}/{len(links)}: {link}")
                
                # Add delay to avoid rate limiting
                if i > 1:
                    time.sleep(2)
                
                downloaded_file = self.download_document(link)
                if downloaded_file:
                    results['downloaded'].append(downloaded_file)
                else:
                    results['failed'].append(link)
        
        # Generate summary
        self.generate_download_summary(results)
        
        return results
    
    def generate_download_summary(self, results: Dict[str, List[str]]) -> None:
        """Generate a summary of the download process."""
        summary_path = self.base_dir / "download_summary.md"
        
        summary_content = f"""# Download Summary

**Downloaded:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## Statistics

- **Successfully downloaded:** {len(results['downloaded'])} files
- **Failed downloads:** {len(results['failed'])} files  
- **Total links found:** {len(results['links_found'])} links

## Successfully Downloaded Files

"""
        
        for file_path in results['downloaded']:
            filename = Path(file_path).name
            summary_content += f"- {filename}\n"
        
        if results['failed']:
            summary_content += "\n## Failed Downloads\n\n"
            for failed_link in results['failed']:
                summary_content += f"- {failed_link}\n"
        
        if self.failed_downloads:
            summary_content += "\n## Error Details\n\n"
            for doc_id, error in self.failed_downloads:
                summary_content += f"- **{doc_id}:** {error}\n"
        
        summary_content += f"\n## All Links Found\n\n"
        for link in results['links_found']:
            summary_content += f"- {link}\n"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"\nDownload summary saved to: {summary_path}")

def main():
    """Main function to demonstrate usage."""
    converter = GoogleDocsConverter()
    
    # The main Google Docs URL provided by the user
    main_url = "https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/"
    
    # Download just the sample first
    print("Downloading sample document...")
    sample_file = converter.download_document(main_url, "sample_first_page")
    
    if sample_file:
        print(f"\nSample download completed successfully!")
        print(f"File saved to: {sample_file}")
        print("\nPlease review the sample file and confirm if you'd like to proceed with recursive downloading of all linked documents.")
        
        return sample_file
    else:
        print("Failed to download sample document.")
        return None

if __name__ == "__main__":
    main()
