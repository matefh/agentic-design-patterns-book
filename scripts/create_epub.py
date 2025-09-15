#!/usr/bin/env python3
"""
EPUB Creator for Agentic Design Patterns Book

This script creates a properly structured EPUB from all downloaded markdown files,
maintaining table of contents order and creating working internal links.
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict

class EPUBCreator:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        
    def load_book_structure(self) -> Dict:
        """Load the book structure from JSON file"""
        structure_file = self.base_dir / "book_structure.json"
        
        if not structure_file.exists():
            raise FileNotFoundError(f"Book structure file not found: {structure_file}")
        
        with open(structure_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_metadata_yaml(self, book_structure: Dict) -> str:
        """Create YAML metadata for the EPUB"""
        metadata = f"""---
title: "{book_structure['title']}"
subtitle: "{book_structure['subtitle']}"
author: "{book_structure['author']}"
language: en-US
toc-title: "Table of Contents"
---

"""
        return metadata
    
    def process_markdown_content(self, content: str, filename: str) -> str:
        """Process markdown content to improve EPUB compatibility"""
        # Remove existing YAML front matter
        content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
        
        # Convert base64 images to references
        def replace_base64_image(match):
            image_ref = match.group(1)
            return f"![Image]({image_ref})"
        
        # Replace base64 image references with cleaner format
        content = re.sub(r'!\[\]\[([^\]]+)\]', replace_base64_image, content)
        
        # Ensure proper chapter/section headings
        if filename.startswith('chapter_'):
            # Make sure first heading is level 1
            content = re.sub(r'^# (.+)', r'# \1', content, flags=re.MULTILINE)
        
        # Fix any malformed markdown
        content = re.sub(r'\\\-', '-', content)  # Fix escaped dashes
        content = re.sub(r'\\\[', '[', content)  # Fix escaped brackets
        content = re.sub(r'\\\]', ']', content)  # Fix escaped brackets
        
        return content
    
    def combine_all_files(self, book_structure: Dict) -> str:
        """Combine all markdown files in proper order"""
        print("📚 Combining all markdown files in proper order...")
        
        combined_content = []
        
        # Add metadata
        combined_content.append(self.create_metadata_yaml(book_structure))
        
        # Add title page
        combined_content.append(f"""# {book_structure['title']}

*{book_structure['subtitle']}*

**{book_structure['author']}**

---

""")
        
        # Process each section in order
        section_counts = {
            'frontmatter': 0,
            'chapters': 0,
            'appendices': 0,
            'backmatter': 0
        }
        
        # Front matter
        for section in book_structure['sections']['frontmatter']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📄 Adding frontmatter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n---\n\n")
                section_counts['frontmatter'] += 1
        
        # Chapters
        combined_content.append("# Part I: Core Patterns\n\n")
        
        for section in book_structure['sections']['chapters']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📖 Adding chapter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n---\n\n")
                section_counts['chapters'] += 1
        
        # Appendices
        combined_content.append("# Appendices\n\n")
        
        for section in book_structure['sections']['appendices']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📎 Adding appendix: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n---\n\n")
                section_counts['appendices'] += 1
        
        # Back matter
        for section in book_structure['sections']['backmatter']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📋 Adding backmatter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n---\n\n")
                section_counts['backmatter'] += 1
        
        # Print summary
        total_sections = sum(section_counts.values())
        print(f"✅ Combined {total_sections} sections:")
        for section_type, count in section_counts.items():
            print(f"   • {section_type}: {count}")
        
        return ''.join(combined_content)
    
    def read_and_process_file(self, file_path: Path, filename: str) -> str:
        """Read and process a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.process_markdown_content(content, filename)
            
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return f"# Error Loading {filename}\n\nContent could not be loaded.\n\n"
    
    def create_epub(self, book_structure: Dict) -> str:
        """Create the EPUB file using Pandoc"""
        print("\n🔧 Creating EPUB file...")
        
        # Combine all content
        combined_content = self.combine_all_files(book_structure)
        
        # Save combined markdown
        combined_md_path = self.base_dir / "complete_book.md"
        print(f"📝 Saving combined content to: {combined_md_path}")
        print(f"   Content length: {len(combined_content):,} characters")
        
        try:
            with open(combined_md_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            print(f"✅ File saved successfully")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None
        
        print(f"📝 Combined markdown saved: {combined_md_path}")
        
        # Create EPUB using Pandoc
        epub_path = self.base_dir / "agentic-design-patterns-book.epub"
        
        pandoc_cmd = [
            "pandoc",
            str(combined_md_path),
            "-o", str(epub_path),
            "--from=markdown+yaml_metadata_block",
            "--to=epub3",
            "--toc",
            "--toc-depth=3",
            "--epub-cover-image=cover.png" if (self.base_dir / "cover.png").exists() else "",
            "--epub-metadata=metadata.xml" if (self.base_dir / "metadata.xml").exists() else "",
            "--standalone"
        ]
        
        # Remove empty arguments
        pandoc_cmd = [arg for arg in pandoc_cmd if arg]
        
        # Execute Pandoc
        import subprocess
        try:
            print(f"🔄 Running Pandoc conversion...")
            print(f"   Command: {' '.join(pandoc_cmd)}")
            
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print(f"✅ EPUB created successfully: {epub_path}")
                
                # Get file size
                file_size = epub_path.stat().st_size
                print(f"📦 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                return str(epub_path)
            else:
                print(f"❌ Pandoc failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error running Pandoc: {e}")
            return None
    
    def create_simple_conversion_script(self) -> None:
        """Create a simple script for future conversions"""
        script_content = '''#!/bin/bash
# Simple EPUB conversion script

echo "🔄 Converting to EPUB..."
pandoc complete_book.md -o agentic-design-patterns-book.epub \\
    --from=markdown+yaml_metadata_block \\
    --to=epub3 \\
    --toc \\
    --toc-depth=3 \\
    --standalone

if [ $? -eq 0 ]; then
    echo "✅ EPUB created: agentic-design-patterns-book.epub"
    ls -lh agentic-design-patterns-book.epub
else
    echo "❌ EPUB creation failed"
fi
'''
        
        script_path = self.base_dir / "convert_to_epub.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        print(f"📜 Conversion script created: {script_path}")

def main():
    """Main function to create the EPUB"""
    print("📚 Agentic Design Patterns - EPUB Creator")
    print("=" * 50)
    
    creator = EPUBCreator()
    
    try:
        # Load book structure
        book_structure = creator.load_book_structure()
        print(f"📖 Loaded book structure: {book_structure['title']}")
        
        # Create EPUB
        epub_path = creator.create_epub(book_structure)
        
        if epub_path:
            # Create conversion script for future use
            creator.create_simple_conversion_script()
            
            print(f"\n🎉 EPUB Creation Complete!")
            print(f"📱 EPUB file: {epub_path}")
            print(f"📊 Contains: {len(book_structure['sections']['frontmatter'])} front matter + "
                  f"{len(book_structure['sections']['chapters'])} chapters + "
                  f"{len(book_structure['sections']['appendices'])} appendices + "
                  f"{len(book_structure['sections']['backmatter'])} back matter")
            
            # Test epub
            print(f"\n📖 To read your EPUB:")
            print(f"   • Open with Apple Books, Adobe Digital Editions, or Calibre")
            print(f"   • Install epubcheck with: brew install epubcheck")
            print(f"   • Validate with: epubcheck {epub_path}")
            
        else:
            print("❌ EPUB creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
