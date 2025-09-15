#!/usr/bin/env python3
"""
Convert the Agentic Design Patterns markdown book to EPUB format
"""

import subprocess
import os
import sys
from pathlib import Path

def convert_markdown_to_epub():
    """Convert the markdown file to EPUB using pandoc"""
    
    # Define paths
    base_dir = Path(__file__).parent
    markdown_file = base_dir / "agentic-design-patterns-book" / "book_final.md"
    output_file = base_dir / "agentic-design-patterns-book-final.epub"
    
    # Check if markdown file exists
    if not markdown_file.exists():
        print(f"Error: Markdown file not found at {markdown_file}")
        return False
    
    print(f"Converting {markdown_file} to {output_file}")
    
    # Pandoc command for high-quality EPUB conversion
    cmd = [
        "pandoc",
        str(markdown_file),
        "-o", str(output_file),
        "--from", "markdown+yaml_metadata_block",
        "--to", "epub3",
        "--toc",  # Generate table of contents
        "--toc-depth=3",  # Include up to 3 levels in TOC
        "--epub-cover-image", "images/cover.png",  # Add cover if exists
        "--epub-metadata", f"title=Agentic Design Patterns",
        "--epub-metadata", f"creator=Antonio Gulli",
        "--epub-metadata", f"language=en-US",
        "--epub-metadata", f"subject=Artificial Intelligence, Software Engineering",
        "--standalone",
        "--self-contained"
    ]
    
    # Remove cover image option if cover doesn't exist
    if not (base_dir / "agentic-design-patterns-book" / "images" / "cover.png").exists():
        cmd = [c for c in cmd if not c.startswith("--epub-cover-image")]
        cmd = [c for c in cmd if c != "images/cover.png"]
    
    try:
        # Run pandoc conversion
        result = subprocess.run(cmd, 
                              cwd=base_dir, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        print(f"✅ Successfully converted to EPUB!")
        print(f"📚 Output file: {output_file}")
        print(f"📏 File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion:")
        print(f"Command: {' '.join(cmd)}")
        print(f"Error output: {e.stderr}")
        return False
    
    except FileNotFoundError:
        print("❌ Error: pandoc not found. Please install pandoc first:")
        print("  brew install pandoc")
        return False

def create_metadata_file():
    """Create a separate metadata file for better EPUB structure"""
    
    base_dir = Path(__file__).parent
    metadata_file = base_dir / "metadata.yaml"
    
    metadata_content = """---
title: "Agentic Design Patterns"
subtitle: "A Hands-On Guide to Building Intelligent Systems"
creator:
  - role: author
    text: Antonio Gulli
identifier:
  - scheme: ISBN
    text: "978-0-000-00000-0"
publisher: "Independent"
date: "2025"
language: en-US
subject:
  - "Artificial Intelligence"
  - "Software Engineering"  
  - "Machine Learning"
  - "AI Agents"
description: |
  A comprehensive guide to building intelligent systems using agentic design patterns.
  This book covers everything from basic prompt chaining to advanced multi-agent 
  architectures, providing practical examples and code implementations.
rights: "© 2025 Antonio Gulli. All rights reserved."
---"""
    
    with open(metadata_file, 'w') as f:
        f.write(metadata_content)
    
    print(f"📝 Created metadata file: {metadata_file}")
    return metadata_file

def main():
    """Main conversion function"""
    print("🚀 Starting EPUB conversion...")
    
    # Create metadata file
    metadata_file = create_metadata_file()
    
    # Convert to EPUB
    success = convert_markdown_to_epub()
    
    if success:
        print("\n✅ Conversion completed successfully!")
        print("\n📖 Your EPUB file is ready for:")
        print("   • Reading on e-readers (Kindle, Kobo, etc.)")
        print("   • Mobile apps (Apple Books, Google Play Books)")
        print("   • Desktop readers (Calibre, Adobe Digital Editions)")
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
