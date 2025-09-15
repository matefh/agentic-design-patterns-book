# Agentic Design Patterns

📖 🔗 👉 [**Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems**](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/)  
*By [Antonio Gulli](https://www.linkedin.com/feed/update/urn:li:activity:7354380927701004288/)*

## About This Book

This book explores the fundamental design patterns needed to build intelligent AI agents. From prompt chaining and tool use to multi-agent collaboration and safety patterns, it provides practical, hands-on guidance for developers building the next generation of AI applications.

## 📚 Book Structure

- **21 Chapters** covering core agentic design patterns
- **6 Appendices** with advanced techniques and frameworks
- **400+ pages** of comprehensive content
- **Hands-on code examples** in Python using LangChain, CrewAI, and Google ADK
- **Real-world applications** and use cases

## 🏗️ Repository Structure

```
├── agentic-design-patterns.epub  # Final EPUB file
├── agentic-design-patterns.md    # Main book content (Markdown)
├── markdown/                     # Individual chapter files downloaded from Google Docs
│   ├── chapter_*.md             # Chapter files
│   ├── appendix_*.md            # Appendix files
│   └── table_of_contents_epub.md # EPUB table of contents
├── scripts/                      # Build and utility scripts
│   ├── create_epub_with_toc.py  # Main EPUB builder
│   └── ...                      # Other utility scripts  
├── images/                       # Book images and diagrams
│   ├── cover.png                # Book cover
│   └── *.png                    # Chapter illustrations
├── styles/                       # EPUB styling
│   └── epub-styles.css          # CSS for EPUB formatting
├── backups/                      # Backup files
├── epub/                         # EPUB files
└── docs/                        # Documentation
```

## 🛠️ Building the EPUB

### Prerequisites

- Python 3.7+
- [Pandoc](https://pandoc.org/installing.html) for EPUB conversion
- Required Python packages (see individual scripts)

### Quick Build

```bash
# Build EPUB with cover image, table of contents, and navigation
python3 scripts/create_epub_with_toc.py
```

This creates a complete EPUB with:
- ✅ Cover image on first page
- ✅ Embedded table of contents  
- ✅ Internal chapter navigation
- ✅ EPUB metadata cover
- ✅ Custom CSS styling
- ✅ Proper EPUB3 structure

### Generated Output

The EPUB will be created at:
```
epub/agentic-design-patterns-complete.epub
```

## 📖 Chapters Overview

### Foundation Patterns (Part 1)
1. **Prompt Chaining** - Sequential LLM interactions
2. **Routing** - Dynamic task delegation
3. **Parallelization** - Concurrent processing
4. **Reflection** - Self-correction mechanisms  
5. **Tool Use** - External API integration
6. **Planning** - Multi-step strategy formulation
7. **Multi-Agent Collaboration** - Distributed intelligence

### Advanced Patterns (Part 2)
8. **Memory Management** - State persistence
9. **Learning and Adaptation** - Continuous improvement
10. **Model Context Protocol** - Standardized communication
11. **Goal Setting and Monitoring** - Objective tracking

### Integration Patterns (Part 3)
12. **Exception Handling** - Error recovery
13. **Human-in-the-Loop** - Interactive workflows
14. **Knowledge Retrieval (RAG)** - Information augmentation

### Production Patterns (Part 4)
15. **Inter-Agent Communication** - Agent-to-agent protocols
16. **Resource-Aware Optimization** - Efficient resource usage
17. **Reasoning Techniques** - Advanced problem solving
18. **Guardrails/Safety** - Safe AI operations
19. **Evaluation and Monitoring** - Performance assessment
20. **Prioritization** - Task management
21. **Exploration and Discovery** - Adaptive learning

## 🔧 Development Scripts

- `create_epub_with_toc.py` - Main EPUB builder with cover and navigation
- `fix_headings.py` - Heading level normalization
- `create_epub_with_images.py` - EPUB with embedded images
- `gdocs_to_markdown.py` - Google Docs conversion
- Various validation and testing scripts

## 📝 Content Guidelines

- All chapter content uses consistent heading hierarchy
- Code examples include proper attribution and licenses
- Images are optimized for EPUB compatibility
- Cross-references use proper markdown linking

## 🚀 Getting Started

1. **Clone this repository**
2. **Install Pandoc**: `brew install pandoc` (macOS) or follow [installation guide](https://pandoc.org/installing.html)
3. **Build EPUB**: `python3 scripts/create_epub_with_toc.py`
4. **Open EPUB**: Double-click the generated file or use your preferred e-reader

## 📱 Compatibility

The generated EPUB works with:
- **macOS Books** app
- **Moon+ Reader** app
- **ElevenReader** app for audio books
- **Kindle** (via Calibre conversion)
- **Adobe Digital Editions**
- **Calibre** e-book management
- Most modern e-readers

## 🤝 Contributing

This book represents cutting-edge knowledge in agentic AI systems. While the main content is authored by Antonio Gulli, the build system and scripts welcome improvements.

## 📄 License

All rights belong to Antonio Gulli.
