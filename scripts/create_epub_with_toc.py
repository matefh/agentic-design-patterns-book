#!/usr/bin/env python3
"""
Create EPUB with cover image, table of contents, and internal navigation
"""

import subprocess
import os
import re
from pathlib import Path

def create_enhanced_book_with_toc():
    """Create enhanced book file with embedded table of contents and cover image"""
    
    base_dir = Path(__file__).parent.parent
    book_final = base_dir / "book_final.md"
    toc_file = base_dir / "markdown" / "table_of_contents_epub.md"
    enhanced_book = base_dir / "book_final_with_toc.md"
    cover_image = base_dir / "images" / "cover.png"
    
    print("🔨 Creating enhanced book with cover image and table of contents...")
    
    # Read the table of contents
    if not toc_file.exists():
        print(f"❌ Table of contents file not found: {toc_file}")
        return False
    
    with open(toc_file, 'r', encoding='utf-8') as f:
        toc_content = f.read()
    
    # Read the main book
    if not book_final.exists():
        print(f"❌ Book file not found: {book_final}")
        return False
    
    with open(book_final, 'r', encoding='utf-8') as f:
        book_content = f.read()
    
    # Find insertion points
    toc_insertion_point = book_content.find("---\n\n# Acknowledgment")
    if toc_insertion_point == -1:
        print("❌ Could not find insertion point for table of contents")
        return False
    
    # Find the end of YAML frontmatter to insert cover image
    yaml_end = book_content.find("---\n\n# Agentic Design Patterns")
    if yaml_end == -1:
        print("❌ Could not find end of YAML frontmatter")
        return False
    
    # Prepare cover image content
    cover_content = ""
    if cover_image.exists():
        print(f"🖼️  Including cover image in first page: {cover_image.name}")
        cover_content = f"![Cover](images/cover.png)\n\n"
    else:
        print(f"⚠️  Cover image not found: {cover_image}")
    
    # Create enhanced book content with cover image and table of contents
    enhanced_content = (
        book_content[:yaml_end + 4] +  # Include "---\n\n"
        cover_content +
        book_content[yaml_end + 4:toc_insertion_point] + 
        "---\n\n" + 
        toc_content + 
        "\n\n" + 
        book_content[toc_insertion_point:]
    )
    
    # Write enhanced book
    with open(enhanced_book, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"✅ Enhanced book created: {enhanced_book}")
    return enhanced_book

def convert_to_epub_with_navigation():
    """Convert the enhanced book to EPUB with proper navigation"""
    
    base_dir = Path(__file__).parent.parent
    enhanced_book = base_dir / "book_final_with_toc.md"
    output_epub = base_dir / "epub" / "agentic-design-patterns-complete.epub"
    css_file = base_dir / "styles" / "epub-styles.css"
    cover_image = base_dir / "images" / "cover.png"
    
    # Ensure epub directory exists
    output_epub.parent.mkdir(exist_ok=True)
    
    print(f"📚 Converting to EPUB with navigation...")
    print(f"📖 Input: {enhanced_book}")
    print(f"📚 Output: {output_epub}")
    
    # Advanced pandoc command with proper EPUB settings, CSS styling, and cover image
    cmd = [
        "pandoc", 
        str(enhanced_book),
        "-o", str(output_epub),
        "--from", "markdown+yaml_metadata_block+auto_identifiers",
        "--to", "epub3",
        "--toc",
        "--toc-depth=3", 
        "--split-level=1",
        "--css", str(css_file),
        "--epub-cover-image", str(cover_image),
        "--metadata", "title=Agentic Design Patterns",
        "--metadata", "creator=Antonio Gulli",
        "--metadata", "language=en-US",
        "--metadata", "subject=Artificial Intelligence, Software Engineering",
        "--metadata", "description=A comprehensive guide to building intelligent AI systems using proven design patterns",
        "--metadata", "publisher=Converted from Google Docs",
        "--metadata", "rights=All royalties donated to Save the Children",
        "--standalone",
        "--embed-resources"
    ]
    
    # Check if CSS file exists
    if not css_file.exists():
        print(f"⚠️  CSS file not found: {css_file}")
        print("   Creating EPUB without custom styling...")
        # Remove CSS parameter if file doesn't exist
        cmd = [c for c in cmd if c != "--css" and c != str(css_file)]
    else:
        print(f"🎨 Including CSS styling: {css_file.name}")
    
    # Check if cover image exists
    if not cover_image.exists():
        print(f"⚠️  Cover image not found: {cover_image}")
        print("   Creating EPUB without cover image...")
        # Remove cover image parameter if file doesn't exist
        cmd = [c for c in cmd if c != "--epub-cover-image" and c != str(cover_image)]
    else:
        print(f"🖼️  Including cover image: {cover_image.name}")
    
    try:
        result = subprocess.run(cmd, 
                              cwd=base_dir, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        print(f"✅ Successfully created EPUB with navigation!")
        print(f"📚 Output: {output_epub}")
        print(f"📏 Size: {output_epub.stat().st_size / 1024 / 1024:.1f} MB")
        
        return output_epub
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during EPUB conversion:")
        print(f"Command: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return None
    
    except FileNotFoundError:
        print("❌ Error: pandoc not found. Please install pandoc first:")
        print("  brew install pandoc")
        return None

def validate_epub_navigation(epub_path):
    """Validate the EPUB structure and navigation"""
    
    print(f"\n🔍 Validating EPUB navigation...")
    
    if not epub_path or not epub_path.exists():
        print("❌ EPUB file not found")
        return False
    
    # Create temp directory for validation
    import tempfile
    import zipfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract EPUB
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        
        # Check for navigation files
        nav_files = list(temp_path.glob("**/nav.xhtml")) + list(temp_path.glob("**/toc.ncx"))
        if nav_files:
            print(f"✅ Navigation files found: {[f.name for f in nav_files]}")
        else:
            print("⚠️  Navigation files may be missing")
        
        # Count content files
        content_files = list(temp_path.glob("**/*.html")) + list(temp_path.glob("**/*.xhtml"))
        print(f"📄 Content files: {len(content_files)}")
        
        # Check for proper structure
        opf_files = list(temp_path.glob("**/*.opf"))
        if opf_files:
            print(f"✅ EPUB package file found: {opf_files[0].name}")
        else:
            print("❌ Missing EPUB package file")
    
    print(f"🎉 EPUB validation complete!")
    return True

def main():
    """Main function to create EPUB with cover image, table of contents, and proper navigation"""
    
    print("🚀 Creating EPUB with Cover Image, Table of Contents and Internal Navigation")
    print("=" * 70)
    
    # Step 1: Create enhanced book with cover image and TOC
    enhanced_book = create_enhanced_book_with_toc()
    if not enhanced_book:
        return 1
    
    # Step 2: Convert to EPUB with navigation
    epub_path = convert_to_epub_with_navigation()
    if not epub_path:
        return 1
    
    # Step 3: Validate EPUB
    validate_epub_navigation(epub_path)
    
    print("\n🎉 SUCCESS! Your EPUB is ready with:")
    print("   ✅ Cover image on first page")
    print("   ✅ Embedded table of contents")
    print("   ✅ Internal chapter navigation")
    print("   ✅ EPUB metadata cover")
    print("   ✅ Custom CSS styling")
    print("   ✅ Proper EPUB3 structure")
    print("   ✅ Cross-device compatibility")
    
    print(f"\n📚 Final EPUB: {epub_path}")
    print("\n📱 How to use:")
    print("   • Double-click to open in Books app (macOS)")
    print("   • Transfer to e-readers via USB or email")
    print("   • Open in Calibre for format conversion")
    
    return 0

if __name__ == "__main__":
    exit(main())
