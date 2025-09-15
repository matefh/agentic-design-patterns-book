#!/bin/bash

echo "📚 EPUB Validation and Information"
echo "=================================="

EPUB_FILE="agentic-design-patterns-book.epub"

if [ ! -f "$EPUB_FILE" ]; then
    echo "❌ EPUB file not found: $EPUB_FILE"
    exit 1
fi

echo "📦 File Info:"
ls -lh "$EPUB_FILE"
echo ""

echo "🔍 File Type:"
file "$EPUB_FILE"
echo ""

echo "📖 EPUB Structure (first 20 files):"
unzip -l "$EPUB_FILE" | head -25
echo ""

echo "📋 To validate the EPUB:"
echo "   brew install epubcheck  # Install validator"
echo "   epubcheck $EPUB_FILE   # Validate"
echo ""

echo "📱 To read the EPUB:"
echo "   • macOS: Open with Books app"
echo "   • Windows: Adobe Digital Editions"
echo "   • Cross-platform: Calibre"
echo "   • Online: EPUBReader browser extension"
echo ""

echo "✅ EPUB creation completed successfully!"

