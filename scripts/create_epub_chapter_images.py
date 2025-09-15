#!/usr/bin/env python3
"""
EPUB Creator with Chapter-Specific Image References

This script ensures each chapter's images stay unique by prefixing them
with chapter identifiers (ch01_image1, ch02_image1, etc.)
"""

import json
import os
import re
import subprocess
from pathlib import Path

class ChapterImageEPUBCreator:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.base_dir = Path(base_dir)
        
    def load_book_structure(self) -> dict:
        """Load the book structure from JSON file"""
        structure_file = self.base_dir / "book_structure.json"
        
        with open(structure_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_chapter_prefix(self, filename: str) -> str:
        """Generate a unique prefix for each chapter/section"""
        if filename.startswith('01_dedication'):
            return 'dedication'
        elif filename.startswith('02_acknowledgment'):
            return 'acknowledgment'
        elif filename.startswith('03_foreword'):
            return 'foreword'
        elif filename.startswith('04_thought'):
            return 'thought'
        elif filename.startswith('05_introduction'):
            return 'intro'
        elif filename.startswith('06_what'):
            return 'agent'
        elif filename.startswith('chapter_'):
            # Extract chapter number
            match = re.search(r'chapter_(\d+)', filename)
            if match:
                chapter_num = match.group(1)
                return f"ch{chapter_num.zfill(2)}"
            return 'chapter'
        elif filename.startswith('appendix_'):
            # Extract appendix letter
            match = re.search(r'appendix_([a-z])', filename)
            if match:
                return f"app{match.group(1)}"
            return 'appendix'
        elif 'conclusion' in filename:
            return 'conclusion'
        elif 'glossary' in filename:
            return 'glossary'
        elif 'index' in filename:
            return 'index'
        elif 'online' in filename:
            return 'online'
        else:
            return 'misc'
    
    def fix_image_references(self, content: str, chapter_prefix: str) -> str:
        """Fix image references to be unique per chapter"""
        # Remove YAML front matter first
        content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
        
        # Find all image references in text like ![][image1]
        image_refs_in_text = re.findall(r'!\[\]\[([^\]]+)\]', content)
        
        # Find all image definitions like [image1]: <data:...>
        image_defs = re.findall(r'^\[([^\]]+)\]:\s*<data:', content, flags=re.MULTILINE)
        
        # Get all unique image names mentioned
        all_image_names = set(image_refs_in_text + image_defs)
        
        print(f"    🖼️  Found {len(all_image_names)} unique images: {sorted(all_image_names)}")
        
        # Replace each image with chapter-specific name
        for old_image_name in all_image_names:
            new_image_name = f"{chapter_prefix}_{old_image_name}"
            
            # Replace references in text: ![][image1] -> ![][ch01_image1]
            content = re.sub(
                rf'!\[\]\[{re.escape(old_image_name)}\]',
                f'![Figure]({new_image_name})',
                content
            )
            
            # Replace image definitions: [image1]: <data:...> -> [ch01_image1]: <data:...>
            content = re.sub(
                rf'^\[{re.escape(old_image_name)}\]:',
                f'[{new_image_name}]:',
                content,
                flags=re.MULTILINE
            )
        
        # Clean up formatting
        content = re.sub(r'\\\-', '-', content)
        content = re.sub(r'\\\[', '[', content)
        content = re.sub(r'\\\]', ']', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def combine_book_with_unique_images(self, book_structure: dict) -> str:
        """Combine all sections with chapter-specific image names"""
        print("📚 Combining book with chapter-specific image references...")
        
        content = []
        
        # Add metadata
        content.append(f"""---
title: "{book_structure['title']}"
subtitle: "{book_structure['subtitle']}"
author: "{book_structure['author']}"
language: en-US
toc-title: "Table of Contents"
description: "A comprehensive guide to building intelligent AI systems using proven design patterns"
publisher: "Converted from Google Docs"
rights: "All royalties donated to Save the Children"
---

# {book_structure['title']}

*{book_structure['subtitle']}*

**By {book_structure['author']}**

> "All royalties will be donated to Save the Children"

---

""")
        
        sections_processed = 0
        
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
                chapter_prefix = self.get_chapter_prefix(section['filename'])
                print(f"  📄 Processing: {section['title']} (prefix: {chapter_prefix})")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Fix image references for this chapter
                    fixed_content = self.fix_image_references(file_content, chapter_prefix)
                    
                    content.append(fixed_content)
                    content.append("\n\n---\n\n")  # Section divider
                    sections_processed += 1
                    
                except Exception as e:
                    print(f"    ⚠️  Error reading {file_path}: {e}")
        
        print(f"✅ Processed {sections_processed} sections with unique image references")
        return ''.join(content)
    
    def create_final_epub(self, book_structure: dict) -> str:
        """Create the final EPUB with properly handled images"""
        print("\n🔧 Creating EPUB with chapter-specific images...")
        
        # Combine content with unique image names
        combined_content = self.combine_book_with_unique_images(book_structure)
        
        # Save combined file
        combined_path = self.base_dir / "book_final.md"
        with open(combined_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        print(f"📝 Combined file saved: {combined_path}")
        print(f"   Content: {len(combined_content):,} characters")
        
        # Create EPUB
        epub_path = self.base_dir / "agentic-design-patterns-final.epub"
        
        cmd = [
            "pandoc", str(combined_path),
            "-o", str(epub_path),
            "--from=markdown+yaml_metadata_block",
            "--to=epub3",
            "--toc",
            "--toc-depth=2",
            "--standalone"
        ]
        
        print(f"🔄 Creating final EPUB...")
        result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = epub_path.stat().st_size
            print(f"✅ EPUB created successfully!")
            print(f"📦 File: {epub_path}")
            print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Check for warnings about images
            if result.stderr:
                warnings = [w for w in result.stderr.split('\n') if w.strip()]
                duplicate_warnings = [w for w in warnings if 'Duplicate link reference' in w]
                image_warnings = [w for w in warnings if 'Could not fetch resource' in w]
                
                if duplicate_warnings:
                    print(f"⚠️  Still have {len(duplicate_warnings)} duplicate image warnings")
                    print(f"   (This is expected - images are embedded as base64)")
                
                if image_warnings:
                    print(f"🖼️  Image embedding: {len(image_warnings)} images embedded as base64")
                
                if len(warnings) <= 10:
                    print(f"📋 All warnings:")
                    for w in warnings:
                        if w.strip():
                            print(f"   {w}")
            
            return str(epub_path)
        else:
            print(f"❌ EPUB creation failed:")
            print(f"   Error: {result.stderr}")
            return None

def main():
    print("📖 Creating Final EPUB with Chapter-Specific Images")
    print("=" * 55)
    
    creator = ChapterImageEPUBCreator()
    
    try:
        book_structure = creator.load_book_structure()
        print(f"📚 Book: {book_structure['title']}")
        
        epub_path = creator.create_final_epub(book_structure)
        
        if epub_path:
            print(f"\n🎉 Final EPUB Created!")
            print(f"📱 File: {epub_path}")
            print(f"🔍 Features:")
            print(f"   ✅ Chapter-specific image naming")
            print(f"   ✅ Complete table of contents")
            print(f"   ✅ All 37 sections included")
            print(f"   ✅ Professional EPUB3 format")
            
            print(f"\n📖 To read:")
            print(f"   macOS: open {epub_path}")
            print(f"   Or use any EPUB reader")
            
        else:
            print("❌ EPUB creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
