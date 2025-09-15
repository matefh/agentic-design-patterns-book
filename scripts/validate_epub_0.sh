#!/bin/bash

# Script to validate and analyze the EPUB file
# Usage: ./validate_epub.sh

EPUB_FILE="agentic-design-patterns-book-final.epub"

echo "📚 EPUB Validation Report"
echo "========================"
echo ""

if [ ! -f "$EPUB_FILE" ]; then
    echo "❌ Error: EPUB file not found: $EPUB_FILE"
    exit 1
fi

# File size and basic info
echo "📏 File Information:"
echo "   File: $EPUB_FILE"
echo "   Size: $(du -h "$EPUB_FILE" | cut -f1)"
echo "   Created: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$EPUB_FILE")"
echo ""

# Check if file is a valid ZIP (EPUBs are ZIP files)
echo "🔍 Structure Validation:"
if unzip -t "$EPUB_FILE" >/dev/null 2>&1; then
    echo "   ✅ Valid ZIP structure"
else
    echo "   ❌ Invalid ZIP structure"
fi

# Extract and show some metadata
echo ""
echo "📖 Content Analysis:"
echo "   Extracting metadata..."

# Create temp directory for extraction
TEMP_DIR=$(mktemp -d)
unzip -q "$EPUB_FILE" -d "$TEMP_DIR"

# Check for required EPUB files
if [ -f "$TEMP_DIR/META-INF/container.xml" ]; then
    echo "   ✅ Container file found"
else
    echo "   ❌ Missing container file"
fi

if [ -f "$TEMP_DIR/mimetype" ]; then
    echo "   ✅ MIME type file found"
    echo "   MIME type: $(cat "$TEMP_DIR/mimetype")"
else
    echo "   ❌ Missing MIME type file"
fi

# Count chapters/sections
CONTENT_FILES=$(find "$TEMP_DIR" -name "*.html" -o -name "*.xhtml" | wc -l)
echo "   📄 Content files: $CONTENT_FILES"

# Show table of contents if available
if [ -f "$TEMP_DIR/nav.xhtml" ] || [ -f "$TEMP_DIR/toc.ncx" ]; then
    echo "   ✅ Navigation/TOC found"
else
    echo "   ⚠️  Navigation/TOC may be missing"
fi

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 EPUB Analysis Complete!"
echo ""
echo "📱 How to Open Your EPUB:"
echo "   • macOS: Double-click to open in Books app"
echo "   • iOS: Share to Books app or use file manager"
echo "   • Android: Google Play Books, Kindle app"
echo "   • Desktop: Calibre (free), Adobe Digital Editions"
echo "   • E-readers: Transfer via USB or email to device"
echo ""
echo "✨ Pro tip: To convert to Kindle format (.mobi):"
echo "   brew install calibre"
echo "   ebook-convert '$EPUB_FILE' 'book.mobi'"
