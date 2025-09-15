#!/usr/bin/env python3
"""
Complete Agentic Design Patterns Book Downloader

This script systematically downloads all Google Docs from the table of contents
and converts them to well-structured markdown files.
"""

import re
import os
import time
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple
from gdocs_to_markdown import GoogleDocsConverter

@dataclass
class BookSection:
    """Represents a section of the book to download"""
    title: str
    url: str
    filename: str
    section_type: str  # 'frontmatter', 'chapter', 'appendix', 'backmatter'
    chapter_number: int = None

class FullBookDownloader:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.converter = GoogleDocsConverter(base_dir)
        self.base_dir = Path(base_dir)
        self.sections = []
        
    def parse_table_of_contents(self, toc_file: str) -> List[BookSection]:
        """Parse the table of contents markdown file to extract all Google Docs links"""
        print("📖 Parsing table of contents...")
        
        with open(toc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = []
        
        # Define patterns for different types of content
        patterns = [
            # Front matter
            (r'\[Dedication\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'dedication', 'frontmatter'),
            (r'\[Acknowledgment\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'acknowledgment', 'frontmatter'),
            (r'\[Foreword\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'foreword', 'frontmatter'),
            (r'\[A Thought Leader\'s Perspective[^]]*\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'thought_leaders_perspective', 'frontmatter'),
            (r'\[Introduction\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'introduction', 'frontmatter'),
            (r'\[What makes an AI system an "agent"\?\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'what_makes_ai_agent', 'frontmatter'),
            
            # Chapters (numbered)
            (r'(\d+)\.\s*\[Chapter (\d+):\s*([^]]+)\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'chapter', 'chapter'),
            
            # Appendices
            (r'\[Appendix ([A-Z]):\s*([^]]+)\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'appendix', 'appendix'),
            (r'\[Appendix ([A-Z])\s*-\s*([^]]+)\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'appendix', 'appendix'),
            
            # Back matter
            (r'\[Conclusion[^]]*\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'conclusion', 'backmatter'),
            (r'\[Glossary\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'glossary', 'backmatter'),
            (r'\[Index of Terms\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'index', 'backmatter'),
            (r'\[Online[^]]*Contribution[^]]*\]\((https://docs\.google\.com/document/d/[^)]+)\)', 'online_contribution', 'backmatter'),
        ]
        
        # Find all Google Docs links with their context
        all_links = re.findall(r'\[([^\]]+)\]\((https://docs\.google\.com/document/d/[^)]+)\)', content)
        
        print(f"Found {len(all_links)} potential Google Docs links")
        
        for link_text, url in all_links:
            # Determine the type and create appropriate filename
            section_type, filename, chapter_num = self._categorize_link(link_text, url)
            
            if section_type:  # Only add if we can categorize it
                section = BookSection(
                    title=link_text,
                    url=url,
                    filename=filename,
                    section_type=section_type,
                    chapter_number=chapter_num
                )
                sections.append(section)
                print(f"  📄 {section_type}: {link_text}")
        
        # Sort sections logically
        sections = self._sort_sections(sections)
        
        print(f"✅ Parsed {len(sections)} sections to download")
        return sections
    
    def _categorize_link(self, title: str, url: str) -> Tuple[str, str, int]:
        """Categorize a link and generate appropriate filename"""
        title_lower = title.lower()
        
        # Front matter
        if 'dedication' in title_lower:
            return 'frontmatter', '01_dedication', None
        elif 'acknowledgment' in title_lower:
            return 'frontmatter', '02_acknowledgment', None
        elif 'foreword' in title_lower:
            return 'frontmatter', '03_foreword', None
        elif 'thought leader' in title_lower or 'perspective' in title_lower:
            return 'frontmatter', '04_thought_leaders_perspective', None
        elif 'introduction' in title_lower and 'chapter' not in title_lower:
            return 'frontmatter', '05_introduction', None
        elif 'what makes' in title_lower and 'agent' in title_lower:
            return 'frontmatter', '06_what_makes_ai_agent', None
        
        # Chapters
        chapter_match = re.search(r'chapter\s+(\d+)', title_lower)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            # Clean title for filename
            clean_title = re.sub(r'chapter\s+\d+:\s*', '', title_lower)
            clean_title = re.sub(r'[^a-z0-9\s]', '', clean_title)
            clean_title = re.sub(r'\s+', '_', clean_title).strip('_')
            filename = f"chapter_{chapter_num:02d}_{clean_title}"
            return 'chapter', filename, chapter_num
        
        # Appendices
        appendix_match = re.search(r'appendix\s+([a-z])', title_lower)
        if appendix_match:
            appendix_letter = appendix_match.group(1)
            clean_title = re.sub(r'appendix\s+[a-z][\s\-:]*', '', title_lower)
            clean_title = re.sub(r'[^a-z0-9\s]', '', clean_title)
            clean_title = re.sub(r'\s+', '_', clean_title).strip('_')
            filename = f"appendix_{appendix_letter}_{clean_title}"
            return 'appendix', filename, None
        
        # Back matter
        if 'conclusion' in title_lower:
            return 'backmatter', 'conclusion', None
        elif 'glossary' in title_lower:
            return 'backmatter', 'glossary', None
        elif 'index' in title_lower:
            return 'backmatter', 'index_of_terms', None
        elif 'online' in title_lower and 'contribution' in title_lower:
            return 'backmatter', 'online_contribution', None
        
        # Default fallback
        clean_title = re.sub(r'[^a-z0-9\s]', '', title_lower)
        clean_title = re.sub(r'\s+', '_', clean_title).strip('_')
        return 'other', f"other_{clean_title}", None
    
    def _sort_sections(self, sections: List[BookSection]) -> List[BookSection]:
        """Sort sections in logical book order"""
        def sort_key(section):
            # Front matter first
            if section.section_type == 'frontmatter':
                if 'dedication' in section.filename:
                    return (0, 0)
                elif 'acknowledgment' in section.filename:
                    return (0, 1)
                elif 'foreword' in section.filename:
                    return (0, 2)
                elif 'perspective' in section.filename:
                    return (0, 3)
                elif 'introduction' in section.filename:
                    return (0, 4)
                elif 'agent' in section.filename:
                    return (0, 5)
                else:
                    return (0, 999)
            
            # Chapters by number
            elif section.section_type == 'chapter':
                return (1, section.chapter_number or 999)
            
            # Appendices by letter
            elif section.section_type == 'appendix':
                appendix_letter = section.filename.split('_')[1] if '_' in section.filename else 'z'
                return (2, ord(appendix_letter.lower()) - ord('a'))
            
            # Back matter last
            elif section.section_type == 'backmatter':
                if 'conclusion' in section.filename:
                    return (3, 0)
                elif 'glossary' in section.filename:
                    return (3, 1)
                elif 'index' in section.filename:
                    return (3, 2)
                else:
                    return (3, 999)
            
            # Other
            else:
                return (4, 999)
        
        return sorted(sections, key=sort_key)
    
    def download_all_sections(self, sections: List[BookSection]) -> Dict:
        """Download all sections with progress tracking"""
        print(f"\n🚀 Starting download of {len(sections)} sections...")
        
        results = {
            'downloaded': [],
            'failed': [],
            'skipped': []
        }
        
        for i, section in enumerate(sections, 1):
            print(f"\n📥 [{i:2d}/{len(sections)}] {section.section_type}: {section.title}")
            print(f"    URL: {section.url}")
            
            # Add delay between requests to be respectful
            if i > 1:
                time.sleep(3)
            
            try:
                # Download the document
                file_path = self.converter.download_document(section.url, section.filename)
                
                if file_path:
                    results['downloaded'].append({
                        'section': section,
                        'file_path': file_path
                    })
                    print(f"    ✅ Downloaded: {section.filename}.md")
                else:
                    results['failed'].append({
                        'section': section,
                        'error': 'Download returned None'
                    })
                    print(f"    ❌ Failed: Download returned None")
            
            except Exception as e:
                results['failed'].append({
                    'section': section,
                    'error': str(e)
                })
                print(f"    ❌ Failed: {str(e)}")
        
        return results
    
    def generate_download_report(self, results: Dict) -> None:
        """Generate a comprehensive download report"""
        report_path = self.base_dir / "download_report.md"
        
        total_sections = len(results['downloaded']) + len(results['failed']) + len(results['skipped'])
        
        report = f"""# Agentic Design Patterns Book - Download Report

**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Sections:** {total_sections}
- **Successfully Downloaded:** {len(results['downloaded'])}
- **Failed Downloads:** {len(results['failed'])}
- **Skipped:** {len(results['skipped'])}
- **Success Rate:** {len(results['downloaded'])/total_sections*100:.1f}%

## Successfully Downloaded Files

"""
        
        # Group by section type
        sections_by_type = {}
        for item in results['downloaded']:
            section_type = item['section'].section_type
            if section_type not in sections_by_type:
                sections_by_type[section_type] = []
            sections_by_type[section_type].append(item)
        
        for section_type in ['frontmatter', 'chapter', 'appendix', 'backmatter']:
            if section_type in sections_by_type:
                report += f"\n### {section_type.title()}\n\n"
                for item in sections_by_type[section_type]:
                    section = item['section']
                    report += f"- **{section.filename}.md** - {section.title}\n"
        
        if results['failed']:
            report += "\n## Failed Downloads\n\n"
            for item in results['failed']:
                section = item['section']
                error = item['error']
                report += f"- **{section.title}**\n"
                report += f"  - URL: {section.url}\n"
                report += f"  - Error: {error}\n\n"
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 Download report saved to: {report_path}")
    
    def create_book_structure(self, results: Dict) -> None:
        """Create a master book structure file"""
        structure_path = self.base_dir / "book_structure.json"
        
        # Create structured data
        book_structure = {
            'title': 'Agentic Design Patterns',
            'subtitle': 'A Hands-On Guide to Building Intelligent Systems',
            'author': 'Antonio Gulli',
            'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sections': {
                'frontmatter': [],
                'chapters': [],
                'appendices': [],
                'backmatter': []
            }
        }
        
        for item in results['downloaded']:
            section = item['section']
            section_data = {
                'title': section.title,
                'filename': section.filename,
                'file_path': item['file_path'],
                'source_url': section.url
            }
            
            if section.chapter_number:
                section_data['number'] = section.chapter_number
            
            # Add to appropriate section
            if section.section_type == 'frontmatter':
                book_structure['sections']['frontmatter'].append(section_data)
            elif section.section_type == 'chapter':
                book_structure['sections']['chapters'].append(section_data)
            elif section.section_type == 'appendix':
                book_structure['sections']['appendices'].append(section_data)
            elif section.section_type == 'backmatter':
                book_structure['sections']['backmatter'].append(section_data)
        
        # Save structure
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(book_structure, f, indent=2)
        
        print(f"📚 Book structure saved to: {structure_path}")

def main():
    """Main function to download the complete book"""
    print("🚀 Agentic Design Patterns - Full Book Downloader")
    print("=" * 50)
    
    # Initialize downloader
    downloader = FullBookDownloader()
    
    # Parse table of contents
    toc_file = "agentic-design-patterns-book/sample_first_page.md"
    if not os.path.exists(toc_file):
        print(f"❌ Table of contents file not found: {toc_file}")
        return
    
    sections = downloader.parse_table_of_contents(toc_file)
    
    if not sections:
        print("❌ No sections found to download")
        return
    
    # Confirm before starting
    print(f"\n📋 Ready to download {len(sections)} sections:")
    for section in sections[:5]:  # Show first 5
        print(f"  • {section.section_type}: {section.title}")
    if len(sections) > 5:
        print(f"  ... and {len(sections) - 5} more")
    
    response = input(f"\nProceed with download? (y/N): ")
    if response.lower() != 'y':
        print("❌ Download cancelled")
        return
    
    # Download all sections
    results = downloader.download_all_sections(sections)
    
    # Generate reports
    downloader.generate_download_report(results)
    downloader.create_book_structure(results)
    
    # Final summary
    print(f"\n🎉 Download Complete!")
    print(f"✅ Successfully downloaded: {len(results['downloaded'])}")
    print(f"❌ Failed downloads: {len(results['failed'])}")
    print(f"📁 All files saved in: {downloader.base_dir}")
    
    if results['failed']:
        print(f"\n⚠️  Some downloads failed. Check download_report.md for details.")

if __name__ == "__main__":
    main()

