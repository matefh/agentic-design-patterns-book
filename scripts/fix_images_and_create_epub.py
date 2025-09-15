#!/usr/bin/env python3
"""
Fixed EPUB Creator with Unique Image References

This script fixes the duplicate image reference issue by making all image references
unique across the entire book, then creates a proper EPUB.
"""

import json
import os
import re
import time
import subprocess
from pathlib import Path
from typing import List, Dict

class FixedEPUBCreator:
    def __init__(self, base_dir: str = "agentic-design-patterns-book"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.image_counter = 1  # Global image counter
        
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
    
    def process_markdown_content(self, content: str, filename: str) -> str:
        """Process markdown content with unique image references"""
        # Remove existing YAML front matter
        content = re.sub(r'^---\n.*?\n---\n\n', '', content, flags=re.DOTALL)
        
        # Extract all image references and definitions
        image_refs_in_text = re.findall(r'!\[\]\[([^\]]+)\]', content)
        image_definitions = re.findall(r'^\[([^\]]+)\]:\s*<data:image/[^>]+>', content, flags=re.MULTILINE)
        
        # Create mapping of old image names to new unique names
        image_mapping = {}
        
        for img_ref in set(image_refs_in_text + image_definitions):
            # Create unique image name using global counter
            unique_name = f"book_image_{self.image_counter:03d}"
            image_mapping[img_ref] = unique_name
            self.image_counter += 1
        
        # Replace image references in text
        for old_name, new_name in image_mapping.items():
            # Replace references in text
            content = re.sub(rf'!\[\]\[{re.escape(old_name)}\]', f'![Figure]({new_name})', content)
            
            # Replace image definitions (move base64 to inline)
            old_def_pattern = rf'^\[{re.escape(old_name)}\]:\s*(<data:image/[^>]+>)'
            
            def replace_def(match):
                base64_data = match.group(1)
                return f'[{new_name}]: {base64_data}'
            
            content = re.sub(old_def_pattern, replace_def, content, flags=re.MULTILINE)
        
        # Clean up any remaining formatting issues
        content = re.sub(r'\\\-', '-', content)  # Fix escaped dashes
        content = re.sub(r'\\\[', '[', content)  # Fix escaped brackets
        content = re.sub(r'\\\]', ']', content)  # Fix escaped brackets
        
        # Ensure proper spacing
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
        
        return content.strip()
    
    def combine_all_files(self, book_structure: Dict) -> str:
        """Combine all markdown files with unique image references"""
        print("📚 Combining all markdown files with unique image references...")
        
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
                combined_content.append("\n\n\\newpage\n\n")  # Page break for EPUB
                section_counts['frontmatter'] += 1
        
        # Chapters - Add part divider
        combined_content.append("# Part I: Core Patterns\n\n")
        
        for section in book_structure['sections']['chapters']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📖 Processing chapter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")  # Page break for EPUB
                section_counts['chapters'] += 1
        
        # Appendices - Add part divider  
        combined_content.append("# Appendices\n\n")
        
        for section in book_structure['sections']['appendices']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📎 Processing appendix: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")  # Page break for EPUB
                section_counts['appendices'] += 1
        
        # Back matter
        for section in book_structure['sections']['backmatter']:
            file_path = self.base_dir / f"{section['filename']}.md"
            if file_path.exists():
                print(f"  📋 Processing backmatter: {section['title']}")
                content = self.read_and_process_file(file_path, section['filename'])
                combined_content.append(content)
                combined_content.append("\n\n\\newpage\n\n")  # Page break for EPUB
                section_counts['backmatter'] += 1
        
        # Print summary
        total_sections = sum(section_counts.values())
        print(f"✅ Combined {total_sections} sections:")
        for section_type, count in section_counts.items():
            print(f"   • {section_type}: {count}")
        print(f"   • Total unique images: {self.image_counter - 1}")
        
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
        """Create the EPUB file using Pandoc with fixed images"""
        print("\n🔧 Creating EPUB with unique image references...")
        
        # Combine all content with unique image names
        combined_content = self.combine_all_files(book_structure)
        
        # Save combined markdown
        combined_md_path = self.base_dir / "complete_book_fixed.md"
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
        epub_path = self.base_dir / "agentic-design-patterns-book-fixed.epub"
        
        pandoc_cmd = [
            "pandoc",
            str(combined_md_path),
            "-o", str(epub_path),
            "--from=markdown+yaml_metadata_block",
            "--to=epub3",
            "--toc",
            "--toc-depth=3",
            "--standalone",
            "--epub-chapter-level=1"  # Treat # headers as chapter breaks
        ]
        
        # Execute Pandoc
        try:
            print(f"🔄 Running Pandoc conversion...")
            print(f"   Command: {' '.join(pandoc_cmd)}")
            
            result = subprocess.run(pandoc_cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print(f"✅ EPUB created successfully: {epub_path}")
                
                # Get file size
                file_size = epub_path.stat().st_size
                print(f"📦 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # Check for warnings
                if result.stderr:
                    print(f"⚠️  Pandoc warnings (but still succeeded):")
                    # Only show first few warnings to avoid spam
                    warnings = result.stderr.split('\n')[:10]
                    for warning in warnings:
                        if warning.strip():
                            print(f"   {warning}")
                    if len(result.stderr.split('\n')) > 10:
                        print(f"   ... and {len(result.stderr.split('\n')) - 10} more warnings")
                
                return str(epub_path)
            else:
                print(f"❌ Pandoc failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error running Pandoc: {e}")
            return None
    
    def validate_epub(self, epub_path: str) -> None:
        """Validate the EPUB file if epubcheck is available"""
        try:
            result = subprocess.run(['which', 'epubcheck'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"\n🔍 Validating EPUB...")
                validation = subprocess.run(['epubcheck', epub_path], capture_output=True, text=True)
                if validation.returncode == 0:
                    print(f"✅ EPUB validation passed!")
                else:
                    print(f"⚠️  EPUB validation warnings:")
                    print(validation.stdout)
            else:
                print(f"\n💡 To validate your EPUB:")
                print(f"   brew install epubcheck")
                print(f"   epubcheck {epub_path}")
        except:
            pass
    
    def show_epub_info(self, epub_path: str) -> None:
        """Show information about the created EPUB"""
        try:
            print(f"\n📖 EPUB Information:")
            print(f"   File: {epub_path}")
            
            # Show file info
            result = subprocess.run(['ls', '-lh', epub_path], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   Size: {result.stdout.split()[4]}")
            
            # Show EPUB structure (first few files)
            result = subprocess.run(['unzip', '-l', epub_path], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                print(f"\n📋 EPUB Structure (first 10 files):")
                for line in lines[3:13]:  # Skip header, show first 10 files
                    if line.strip():
                        print(f"   {line}")
            
        except Exception as e:
            print(f"⚠️  Could not get EPUB info: {e}")

def main():
    """Main function to create the EPUB with fixed images"""
    print("📚 Agentic Design Patterns - Fixed EPUB Creator")
    print("🖼️  Fixing duplicate image references...")
    print("=" * 50)
    
    creator = FixedEPUBCreator()
    
    try:
        # Load book structure
        book_structure = creator.load_book_structure()
        print(f"📖 Loaded book structure: {book_structure['title']}")
        
        # Create EPUB with fixed images
        epub_path = creator.create_epub(book_structure)
        
        if epub_path:
            # Validate EPUB if possible
            creator.validate_epub(epub_path)
            
            # Show EPUB info
            creator.show_epub_info(epub_path)
            
            print(f"\n🎉 Fixed EPUB Creation Complete!")
            print(f"📱 EPUB file: {epub_path}")
            print(f"🖼️  Images: All image references made unique")
            print(f"📚 Content: All {sum(len(section) for section in book_structure['sections'].values())} sections included")
            
            print(f"\n📖 To read your EPUB:")
            print(f"   • macOS: open {epub_path}")
            print(f"   • Or double-click the file in Finder")
            print(f"   • Transfer to devices via AirDrop, email, etc.")
            
        else:
            print("❌ EPUB creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

