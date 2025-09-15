#!/usr/bin/env python3
"""
EPUB Creator with Proper Image Handling

This script properly handles base64 images by keeping them inline and making
the image references unique to avoid conflicts.
"""

import json
import os
import re
import time
import subprocess
import base64
from pathlib import Path
from typing import List, Dict

class ImageFixedEPUBCreator:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.image_counter = 1
        
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
date: "{book_structure['download_date']}"
description: "A comprehensive guide to building intelligent AI systems using proven design patterns"
publisher: "Converted from Google Docs"
rights: "All royalties donated to Save the Children"
---

"""
        return metadata
    
    def extract_and_save_images(self, content: str, filename: str) -> str:
        """Extract base64 images, save as files, and update references"""
        # Find all base64 image definitions
        base64_pattern = r'\[([^\]]+)\]:\s*<data:image/([^;]+);base64,([^>]+)>'
        
        def replace_base64_image(match):
            image_ref = match.group(1)
            image_format = match.group(2)
            base64_data = match.group(3)
            
            try:
                # Create unique image filename
                unique_image_name = f"{filename}_img_{self.image_counter:03d}.{image_format}"
                self.image_counter += 1
                
                # Decode and save image
                image_data = base64.b64decode(base64_data)
                image_path = self.images_dir / unique_image_name
                
                # Ensure images directory exists
                self.images_dir.mkdir(exist_ok=True)
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"    💾 Saved image: {unique_image_name}")
                
                # Return markdown reference to saved image
                return f'[{image_ref}]: images/{unique_image_name}'
                
            except Exception as e:
                print(f"    ⚠️  Error processing image {image_ref}: {e}")
                return f'[{image_ref}]: # Image could not be processed'
        
        # Replace all base64 images with file references
        processed_content = re.sub(base64_pattern, replace_base64_image, content)
        return processed_content
    
    def process_markdown_content(self, content: str, filename: str) -> str:
        """Process markdown content and handle images properly"""
        # Remove existing YAML front matter
        content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
        
        # Extract and save images, replace with file references
        content = self.extract_and_save_images(content, filename)
        
        # Clean up any remaining formatting issues
        content = re.sub(r'\\\-', '-', content)  # Fix escaped dashes
        content = re.sub(r'\\\[', '[', content)  # Fix escaped brackets
        content = re.sub(r'\\\]', ']', content)  # Fix escaped brackets
        
        # Ensure proper spacing
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
        
        return content.strip()
    
    def combine_all_files(self, book_structure: Dict) -> str:
        """Combine all markdown files with properly handled images"""
        print("📚 Combining all markdown files with proper image handling...")
        
        combined_content = []
        
        # Add metadata
        combined_content.append(self.create_metadata_yaml(book_structure))
        
        # Add title page
        combined_content.append(f"""# {book_structure['title']}

*{book_structure['subtitle']}*

**By {book_structure['author']}**

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
                print(f"  📄 Processing frontmatter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")
                section_counts['frontmatter'] += 1
        
        # Chapters
        combined_content.append("# Part I: Core Patterns\n\n")
        
        for section in book_structure['sections']['chapters']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📖 Processing chapter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")
                section_counts['chapters'] += 1
        
        # Appendices
        combined_content.append("# Appendices\n\n")
        
        for section in book_structure['sections']['appendices']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📎 Processing appendix: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")
                section_counts['appendices'] += 1
        
        # Back matter
        for section in book_structure['sections']['backmatter']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📋 Processing backmatter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")
                section_counts['backmatter'] += 1
        
        # Print summary
        total_sections = sum(section_counts.values())
        print(f"✅ Combined {total_sections} sections:")
        for section_type, count in section_counts.items():
            print(f"   • {section_type}: {count}")
        print(f"   • Total images extracted: {self.image_counter - 1}")
        
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
        """Create the EPUB file with properly handled images"""
        print("\n🔧 Creating EPUB with properly extracted images...")
        
        # Combine all content and extract images
        combined_content = self.combine_all_files(book_structure)
        
        # Save combined markdown
        combined_md_path = self.base_dir / "complete_book_with_images.md"
        print(f"📝 Saving combined content to: {combined_md_path}")
        print(f"   Content length: {len(combined_content):,} characters")
        
        try:
            with open(combined_md_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            print(f"✅ Combined file saved successfully")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None
        
        # Create EPUB using Pandoc
        epub_path = self.base_dir / "agentic-design-patterns-book-with-images.epub"
        
        pandoc_cmd = [
            "pandoc",
            str(combined_md_path),
            "-o", str(epub_path),
            "--from=markdown+yaml_metadata_block",
            "--to=epub3",
            "--toc",
            "--toc-depth=3",
            "--standalone",
            "--split-level=1",
            f"--resource-path={self.base_dir}"  # Tell Pandoc where to find images
        ]
        
        # Execute Pandoc
        try:
            print(f"🔄 Running Pandoc conversion...")
            print(f"   Output: {epub_path}")
            
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print(f"✅ EPUB created successfully!")
                
                # Get file size
                file_size = epub_path.stat().st_size
                print(f"📦 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # Show any warnings
                if result.stderr:
                    warnings = result.stderr.split('\n')
                    image_warnings = [w for w in warnings if 'Could not fetch resource' in w]
                    other_warnings = [w for w in warnings if w.strip() and 'Could not fetch resource' not in w]
                    
                    if other_warnings:
                        print(f"⚠️  Pandoc warnings:")
                        for warning in other_warnings[:5]:  # Show first 5
                            print(f"   {warning}")
                    
                    if image_warnings:
                        print(f"🖼️  Image warnings: {len(image_warnings)} images may not display properly")
                
                return str(epub_path)
            else:
                print(f"❌ Pandoc failed:")
                print(f"   stderr: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error running Pandoc: {e}")
            return None

def main():
    """Main function to create the EPUB with proper image handling"""
    print("📚 Agentic Design Patterns - EPUB Creator with Image Extraction")
    print("=" * 60)
    
    creator = ImageFixedEPUBCreator()
    
    try:
        # Load book structure
        book_structure = creator.load_book_structure()
        print(f"📖 Loaded book structure: {book_structure['title']}")
        
        # Create EPUB with proper image handling
        epub_path = creator.create_epub(book_structure)
        
        if epub_path:
            print(f"\n🎉 EPUB Creation Complete!")
            print(f"📱 EPUB file: {epub_path}")
            print(f"📁 Images folder: {creator.images_dir}")
            print(f"🖼️  Images extracted: {creator.image_counter - 1}")
            
            print(f"\n📖 To read your EPUB:")
            print(f"   macOS: open {epub_path}")
            print(f"   Or use any EPUB reader app")
            
            # Show file info
            file_size = Path(epub_path).stat().st_size
            print(f"\n📊 File Statistics:")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"   Format: EPUB3 with table of contents")
            
        else:
            print("❌ EPUB creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

