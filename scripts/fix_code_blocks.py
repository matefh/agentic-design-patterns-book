#!/usr/bin/env python3
"""
Script to automatically fix problematic code blocks in markdown files using Claude 4 Sonnet.
Converts table-format code blocks to proper markdown code blocks.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
import time

# Load environment variables
load_dotenv()

class CodeBlockFixer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.backup_path = None
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Initialize Claude 3.5 Sonnet (latest available model)
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 Sonnet as it's the latest available
            api_key=self.anthropic_api_key,
            temperature=0.1,
            max_tokens=8192
        )
        
        self.conversion_prompt = """You are tasked with converting improperly formatted code blocks in markdown to proper markdown format.

The input contains code blocks that are formatted as markdown tables like this:
| `code here...` |
| :---- |

Your task is to:
1. Extract the code from between the backticks
2. Determine the appropriate programming language (python, bash, json, etc.)
3. Format it as a proper markdown code block with syntax highlighting
4. Format the code properly with correct indentation and line breaks

Rules:
- If it's a bash command, use ```bash
- If it's Python code, use ```python  
- If it's JSON data, use ```json
- If language can't be determined, use ```
- Preserve the actual code content but format it properly with appropriate line breaks and indentation
- Do NOT add any explanatory text, just return the properly formatted code block

Input text to convert:
{input_text}

Return ONLY the properly formatted markdown code block, nothing else."""

    def create_backup(self):
        """Create a backup of the original file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.file_path.stem}_backup_{timestamp}{self.file_path.suffix}"
        self.backup_path = self.file_path.parent / backup_name
        
        shutil.copy2(self.file_path, self.backup_path)
        print(f"✓ Created backup: {self.backup_path}")
        
    def find_problematic_blocks(self, content: str):
        """Find all problematic code block patterns in the content."""
        # Pattern to match any variation of | `...code...` | followed by | :---- |
        # This handles 1-4 backticks and content that may extend beyond pipes
        pattern = r'\|\s*(`{1,4})(.*?)\1\s*\|\s*\n\|\s*:----\s*\|'
        matches = []
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            matches.append({
                'full_match': match.group(0),
                'code_content': match.group(2).strip(),
                'start': match.start(),
                'end': match.end()
            })
        
        # Sort by position (descending for reverse processing)
        matches.sort(key=lambda x: x['start'], reverse=True)
        return matches
    
    def convert_code_block(self, problematic_block: str) -> str:
        """Use Claude to convert a problematic code block to proper markdown."""
        try:
            prompt = self.conversion_prompt.format(input_text=problematic_block)
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"  ⚠️ Error converting block: {e}")
            return problematic_block  # Return original if conversion fails
    
    def process_file(self):
        """Main processing function."""
        print(f"🚀 Starting code block conversion for: {self.file_path}")
        print(f"📝 Using model: {self.llm.model}")
        
        # Create backup
        self.create_backup()
        
        # Read the file
        print("📖 Reading file...")
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Find problematic blocks
        problematic_blocks = self.find_problematic_blocks(content)
        total_blocks = len(problematic_blocks)
        
        if total_blocks == 0:
            print("✅ No problematic code blocks found!")
            return
            
        print(f"🔍 Found {total_blocks} problematic code blocks to fix")
        
        # Process blocks (already sorted in reverse order to maintain correct positions)
        for i, block_info in enumerate(problematic_blocks, 1):
            block_num = i
            print(f"\n📝 Processing block {block_num}/{total_blocks}")
            
            # Show preview of the block
            preview = block_info['code_content'][:100]
            if len(block_info['code_content']) > 100:
                preview += "..."
            print(f"   Preview: {preview}")
            
            # Convert using Claude
            print("   🤖 Converting with Claude...")
            converted_block = self.convert_code_block(block_info['full_match'])
            
            # Replace in content
            content = (content[:block_info['start']] + 
                      converted_block + 
                      content[block_info['end']:])
            
            print(f"   ✅ Converted block {block_num}")
            
            # Add a small delay to respect API rate limits
            time.sleep(0.5)
        
        # Write the updated content back to file
        print(f"\n💾 Saving updated file...")
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Report results
        original_size = len(original_content)
        new_size = len(content)
        size_diff = new_size - original_size
        
        print(f"\n🎉 Conversion complete!")
        print(f"   📊 Blocks converted: {total_blocks}")
        print(f"   📏 Size change: {size_diff:+d} characters")
        print(f"   💾 Backup saved as: {self.backup_path}")
        print(f"   ✅ Updated file: {self.file_path}")


def main():
    """Main function."""
    # Path to the book file
    book_file = "/Users/matefh/Work/Optima/LrnCon/agentic-design-patterns-book/agentic-design-patterns-book/book_final.md"
    
    try:
        # Check if file exists
        if not os.path.exists(book_file):
            print(f"❌ File not found: {book_file}")
            return
            
        # Initialize and run the fixer
        fixer = CodeBlockFixer(book_file)
        fixer.process_file()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
