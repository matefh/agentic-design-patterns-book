#!/usr/bin/env python3
"""
Test Chapter 1 Download

Download just Chapter 1 to test code blocks and images handling
"""

from gdocs_to_markdown import GoogleDocsConverter

def test_chapter1():
    """Download Chapter 1 specifically to test formatting."""
    converter = GoogleDocsConverter()
    
    # Chapter 1: Prompt Chaining URL from the table of contents
    chapter1_url = "https://docs.google.com/document/d/1flxKGrbnF2g8yh3F-oVD5Xx7ZumId56HbFpIiPdkqLI/edit?usp=sharing"
    
    print("Downloading Chapter 1: Prompt Chaining...")
    print(f"URL: {chapter1_url}")
    
    # Download with specific filename
    result = converter.download_document(chapter1_url, "chapter_01_prompt_chaining")
    
    if result:
        print(f"\n✅ Chapter 1 downloaded successfully!")
        print(f"📁 File saved to: {result}")
        print("\n🔍 Please review the file to check:")
        print("   - Code block formatting")
        print("   - Image handling and placement")
        print("   - Overall structure and content quality")
        
        # Show some stats
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.count('\n')
            words = len(content.split())
            chars = len(content)
        
        print(f"\n📊 File Statistics:")
        print(f"   - Lines: {lines:,}")
        print(f"   - Words: {words:,}")
        print(f"   - Characters: {chars:,}")
        
        # Check for code blocks and images
        code_blocks = content.count('```')
        images = content.count('![')
        
        print(f"\n🎯 Content Analysis:")
        print(f"   - Code blocks (```): {code_blocks // 2}")  # Divide by 2 since each block has opening and closing
        print(f"   - Images: {images}")
        
        return result
    else:
        print("❌ Failed to download Chapter 1")
        return None

if __name__ == "__main__":
    test_chapter1()

