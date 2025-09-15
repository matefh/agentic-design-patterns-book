#!/bin/bash

# Simple script to convert markdown to EPUB using pandoc
# Usage: ./convert.sh

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="$SCRIPT_DIR/agentic-design-patterns-book/book_final.md"
OUTPUT_FILE="$SCRIPT_DIR/agentic-design-patterns-book-final.epub"

echo "🚀 Converting Agentic Design Patterns to EPUB..."

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Error: Input file not found: $INPUT_FILE"
    exit 1
fi

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "❌ Error: pandoc is not installed"
    echo "Install with: brew install pandoc"
    exit 1
fi

echo "📖 Input:  $INPUT_FILE"
echo "📚 Output: $OUTPUT_FILE"

# Convert with pandoc
pandoc "$INPUT_FILE" \
    -o "$OUTPUT_FILE" \
    --from markdown+yaml_metadata_block \
    --to epub3 \
    --toc \
    --toc-depth=3 \
    --metadata title="Agentic Design Patterns" \
    --metadata creator="Antonio Gulli" \
    --metadata language="en-US" \
    --metadata subject="Artificial Intelligence, Software Engineering" \
    --standalone \
    --self-contained

echo "✅ Conversion completed successfully!"
echo "📏 File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo ""
echo "📖 Your EPUB is ready for:"
echo "   • E-readers (Kindle, Kobo, etc.)"
echo "   • Mobile apps (Apple Books, Google Play Books)"
echo "   • Desktop readers (Calibre, Adobe Digital Editions)"
