# Skills - AI Skills Collection

A collection of AI skills for Claude Code, each designed to enhance productivity and automate common tasks.

## Available Skills

### [db-mcp](./db-mcp/) - Database MCP Service Management

A comprehensive database MCP server skill providing secure database query functionality.

**Features:**
- Support for MySQL, PostgreSQL, and SQLite
- Automatic dependency detection and one-click installation
- Secure read-only queries with SQL injection protection
- Multi-database configuration support
- Unified command-line tool for MCP service management

**Key Tools:**
- `list_tables` - List all tables in the database
- `describe_table` - View table structure and schema
- `execute_query` - Execute SELECT queries
- `get_table_count` - Get table row counts
- `get_database_info` - Get database information
- `search_tables` - Search tables by keywords

**Quick Start:**
```bash
cd db-mcp
python scripts/db-mcp.py install    # Auto-install dependencies
python scripts/db-mcp.py setup      # Install MCP service
```

### [doc2md](./doc2md/) - Document to Markdown Converter

Convert 40+ document formats to Markdown using Pandoc and MinerU.

**Features:**
- **Pandoc**: Universal converter for DOCX, EPUB, HTML, PPTX, LaTeX, and more
- **MinerU**: Advanced PDF parser with OCR, table extraction, and layout recognition
- Batch processing with glob patterns
- Flexible image handling (relative paths or Base64 embedding)
- TOC removal and post-processing

**Supported Formats:**
- Documents: DOCX, DOC, ODT, RTF, PDF
- E-books: EPUB, FB2
- Presentations: PPTX
- Web: HTML, XHTML, XML
- Academic: LaTeX, TeX
- And 30+ more formats

**Quick Start:**
```bash
cd doc2md
# Install Pandoc (required)
choco install pandoc  # Windows
brew install pandoc   # macOS

# Install MinerU (optional, for advanced PDF)
pip install mineru

# Convert documents
python scripts/converter.py document.docx --relative-images --skip-toc
python scripts/converter.py document.pdf --tool mineru --relative-images
```

## Installation

Each skill can be installed independently:

```bash
# Install db-mcp skill
xcopy db-mcp %USERPROFILE%\.claude\skills\ /E /I  # Windows
cp -r db-mcp ~/.claude/skills/                     # Linux/Mac

# Install doc2md skill
xcopy doc2md %USERPROFILE%\.claude\skills\ /E /I  # Windows
cp -r doc2md ~/.claude/skills/                     # Linux/Mac
```

## Usage

Each skill has its own `SKILL.md` file with detailed instructions:

- `db-mcp/SKILL.md` - Database management usage guide
- `doc2md/SKILL.md` - Document conversion workflow

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests for:
- Bug fixes
- New features
- Documentation improvements
- Additional skills

## License

This repository is licensed under the MIT License. See individual skill directories for specific license information.
