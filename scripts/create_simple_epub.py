#!/usr/bin/env python3
"""
Simple EPUB Creator - Text Only Version

Creates a clean EPUB without images to ensure the structure and navigation work perfectly.
We can add images later if needed.
"""

import json
import os
import re
import subprocess
from pathlib import Path

class SimpleEPUBCreator:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.base_dir = Path(base_dir)
        
    def load_book_structure(self) -> dict:
        """Load the book structure from JSON file"""
        structure_file = self.base_dir / "book_structure.json"
        
        with open(structure_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clean_content(self, content: str) -> str:
        """Clean content by removing YAML and fixing formatting"""
        # Remove YAML front matter
        content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
        
        # Remove all image references and definitions to avoid conflicts
        content = re.sub(r'!\[\]\[[^\]]+\]', '[Image removed for EPUB]', content)
        content = re.sub(r'^\[[^\]]+\]:\s*<data:image/[^>]+>\n?', '', content, flags=re.MULTILINE)
        
        # Clean up formatting
        content = re.sub(r'\\\-', '-', content)
        content = re.sub(r'\\\[', '[', content)
        content = re.sub(r'\\\]', ']', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def combine_book(self, book_structure: dict) -> str:
        """Combine all sections into one clean markdown file"""
        print("📚 Creating clean text-only EPUB...")
        
        content = []
        
        # Metadata
        content.append(f"""---
title: "{book_structure['title']}"
subtitle: "{book_structure['subtitle']}"
author: "{book_structure['author']}"
language: en-US
toc-title: "Table of Contents"
description: "A comprehensive guide to building intelligent AI systems"
---

# {book_structure['title']}

*{book_structure['subtitle']}*

**By {book_structure['author']}**

> All royalties will be donated to Save the Children

---

""")
        
        sections_added = 0
        
        # Process all sections in order
        all_sections = (
            book_structure['sections']['frontmatter'] +
            book_structure['sections']['chapters'] +
            book_structure['sections']['appendices'] +
            book_structure['sections']['backmatter']
        )
        
        for section in all_sections:
            file_path = self.base_dir / f"{section['filename']}.md"
            
            if file_path.exists():
                print(f"  📄 Adding: {section['title']}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    cleaned_content = self.clean_content(file_content)
                    content.append(cleaned_content)
                    content.append("\n\n---\n\n")  # Section divider
                    sections_added += 1
                    
                except Exception as e:
                    print(f"    ⚠️  Error reading {file_path}: {e}")
        
        print(f"✅ Combined {sections_added} sections successfully")
        return ''.join(content)
    
    def create_epub(self, book_structure: dict) -> str:
        """Create the EPUB file"""
        # Combine content
        combined_content = self.combine_book(book_structure)
        
        # Save combined file
        combined_path = self.base_dir / "book_clean.md"
        with open(combined_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        print(f"📝 Combined markdown saved: {combined_path}")
        print(f"   Length: {len(combined_content):,} characters")
        
        # Create EPUB
        epub_path = self.base_dir / "agentic-design-patterns-clean.epub"
        
        cmd = [
            "pandoc", str(combined_path),
            "-o", str(epub_path),
            "--from=markdown+yaml_metadata_block",
            "--to=epub3",
            "--toc",
            "--toc-depth=2",
            "--standalone"
        ]
        
        print(f"🔄 Creating EPUB...")
        result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = epub_path.stat().st_size
            print(f"✅ EPUB created successfully!")
            print(f"📦 File: {epub_path}")
            print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            return str(epub_path)
        else:
            print(f"❌ EPUB creation failed:")
            print(f"   Error: {result.stderr}")
            return None

def main():
    print("📖 Creating Clean EPUB (Text-Only Version)")
    print("=" * 50)
    
    creator = SimpleEPUBCreator()
    
    try:
        book_structure = creator.load_book_structure()
        epub_path = creator.create_epub(book_structure)
        
        if epub_path:
            print(f"\n🎉 Success!")
            print(f"📱 Your EPUB: {epub_path}")
            print(f"📖 Open with: Books app, Calibre, Adobe Digital Editions")
            print(f"💡 This version has clean text with working navigation")
            print(f"   Images were removed to ensure perfect EPUB compatibility")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

