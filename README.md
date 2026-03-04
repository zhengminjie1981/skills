# Skills - AI Skills Collection

A collection of AI skills for Claude Code, each designed to enhance productivity and automate common tasks.

## Available Skills

### [dev-workflow](./dev-workflow/) - Document-Driven Development Workflow

A comprehensive development workflow specification enforcing document-driven development: no code without documentation, no code changes without documentation updates.

**Core Principles:**
- **Documentation First**: Any module or feature implementation must have technical documentation completed before coding
- **Change Tracking**: Any iterative modification must update related documentation and complete impact analysis before code changes
- **Modular Boundaries**: Modules interact through data structure specifications and interface specifications
- **Consistency Maintenance**: After documentation updates, synchronize all references
- **Centralized Progress**: All work plans and progress recorded in unified project planning documents

**Key Features:**
- 5-tier document hierarchy (System → Specs → Modules → Validation → Reports)
- Quality gates for pre-coding and pre-commit checkpoints
- Automated consistency checking tools
- Complete templates and checklists for new module development and iteration changes
- Temporary file isolation and management

**Trigger Scenarios:**
1. Creating new modules or features
2. Modifying existing code, data structures, or interfaces
3. Iterative changes or refactoring
4. Documentation consistency checks
5. Module design, data structure specifications, interface specifications

**Quick Start:**
```bash
# View complete specification
cat dev-workflow/SKILL.md

# Reference materials
ls dev-workflow/references/
# - full-spec.md: Detailed examples, anti-patterns, flowcharts, AI execution flows
# - checklist.md: New module and iteration checklists
# - quality-gates.md: Quality standards for each phase
# - decision-tree.md: Common scenario decision flows
# - anti-patterns.md: Anti-pattern examples with correct approaches
# - conversation-examples.md: Example AI-user interactions
# - quick-reference.md: Quick lookup tables and decision charts
# - ai-checklist.md: Pre-execution checkpoints for AI
# - git-integration.md: Git workflow integration
# - doc-generation-guide.md: Document generation assistance
# - templates.md: Document templates
# - tools.md: Document maintenance scripts
```

### [db-mcp](./db-mcp/) - Database MCP Service Management

A comprehensive database MCP server skill with zero-configuration startup and automatic dependency management.

**Features:**
- **Zero-Configuration Startup** - Server starts without config, auto-setup via AI tools
- **Auto-Install Dependencies** - Automatically detect and install missing database drivers
- **Intelligent Diagnostics** - System capability detection and connection testing
- Support for MySQL, PostgreSQL, and SQLite
- Secure read-only queries with SQL injection protection
- Multi-database configuration support

**Key Tools:**
- `check_capabilities()` - Check installed drivers, config status, and get recommendations
- `auto_setup_database()` - Zero-config setup: auto-install drivers, create config, test connection
- `test_connection()` - Test database connection with latency and server info
- `list_tables` - List all tables in the database
- `describe_table` - View table structure and schema
- `execute_query` - Execute SELECT queries
- `get_table_count` - Get table row counts
- `get_database_info` - Get database information
- `search_tables` - Search tables by keywords

**Quick Start (Zero-Config):**
```bash
cd db-mcp
python scripts/db-mcp.py setup    # Install MCP service
# Restart Claude Code, then in conversation:
# auto_setup_database(db_type="mysql", connection_params={...})
```

**Traditional Setup:**
```bash
cd db-mcp
python scripts/db-mcp.py install --db-type mysql  # Install specific driver
python scripts/db-mcp.py setup                    # Install MCP service
```

### [doc2md](./doc2md/) - Document to Markdown Converter

Convert 40+ document formats to Markdown using Pandoc and MinerU.

**Features:**
- **Pandoc**: Universal converter for DOCX, EPUB, HTML, PPTX, LaTeX, and more
- **MinerU**: Advanced PDF parser with OCR, table extraction, and layout recognition
- **PyMuPDF**: Fast and lightweight PDF converter
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
# Check environment status
python scripts/converter.py --status

# Convert Word document
python scripts/converter.py document.docx --relative-images --skip-toc

# Convert PDF (with auto tool selection)
python scripts/converter.py document.pdf --tool auto --relative-images

# Batch convert
python scripts/converter.py "./docs/*.docx" -o ./output/ --relative-images --skip-toc
```

### [knowledge-index](./knowledge-index/) - Local Knowledge Base Intelligent Indexing

Build AI-readable indexes for local document collections with automatic summarization, incremental updates, and intelligent retrieval.

**Core Features:**
- **Local-First**: Use local tools to extract text, avoid uploading documents to cloud
- **AI Summarization**: Generate concise summaries (50-500 chars) and keywords (5-10) for each document
- **Incremental Updates**: Detect file changes and update only modified documents
- **Intelligent Retrieval**: AI-powered search through index to locate relevant documents
- **Global Registry**: Manage all knowledge bases from skill's `data/registry.yaml`
- **Hierarchy Management**: Auto-promote child indexes to parent level

**Key Principles:**
- **Local First**: Extract text locally, only send plain text to LLM for summaries
- **Privacy Protection**: Configurable read strategies (local/direct/hybrid)
- **Smart Fallback**: Auto-degrade when tools unavailable
- **Fault Tolerance**: Single document failure doesn't affect overall workflow

**Trigger Scenarios:**
1. "Build index for [knowledge-base]"
2. "Update [knowledge-base] index"
3. "Search in knowledge base for..."
4. "Check which knowledge bases need updates"

**Quick Start:**
```bash
# Build index for a knowledge base
# AI will: Scan → Generate summaries → Write _index.yaml

# Query the knowledge base
# AI will: Read index → Match documents → Generate answer

# Update index incrementally
# AI will: Detect changes → Process new/modified files → Update index
```

**Index Structure:**
```
knowledge-base/
├── _index.yaml          # AI-readable index file
├── _index_config.yaml   # Configuration (optional)
├── document1.md
├── document2.pdf
└── subfolder/
    └── document3.docx
```

**Directory Structure:**
```
knowledge-index/
├── SKILL.md              # Entry point (AI-friendly, on-demand loading)
├── data/                 # Runtime data (registry, config, backups)
├── docs/                 # Development docs (design, changelog)
├── references/           # AI reference docs (on-demand loading)
│   ├── core/             # Index spec, workflow, quality gates
│   ├── execution/        # Tools, checklists, templates
│   ├── decision/         # Decision trees, anti-patterns
│   └── advanced/         # Global registry, hierarchy management
├── scripts/              # Utility scripts (extract_text, check_deps)
└── tests/                # Test cases
```

## Installation

Each skill can be installed independently:

```bash
# Install dev-workflow skill
xcopy dev-workflow %USERPROFILE%\.claude\skills\ /E /I  # Windows
cp -r dev-workflow ~/.claude/skills/                     # Linux/Mac

# Install db-mcp skill
xcopy db-mcp %USERPROFILE%\.claude\skills\ /E /I  # Windows
cp -r db-mcp ~/.claude/skills/                     # Linux/Mac

# Install doc2md skill
xcopy doc2md %USERPROFILE%\.claude\skills\ /E /I  # Windows
cp -r doc2md ~/.claude/skills/                     # Linux/Mac

# Install knowledge-index skill
xcopy knowledge-index %USERPROFILE%\.claude\skills\ /E /I  # Windows
cp -r knowledge-index ~/.claude/skills/                     # Linux/Mac
```

## Usage

Each skill has its own `SKILL.md` file with detailed instructions:

- `dev-workflow/SKILL.md` - Document-driven development workflow specification
- `db-mcp/SKILL.md` - Database management usage guide
- `doc2md/SKILL.md` - Document conversion workflow
- `knowledge-index/SKILL.md` - Knowledge base indexing guide

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests for:
- Bug fixes
- New features
- Documentation improvements
- Additional skills

## License

This repository is licensed under the MIT License. See individual skill directories for specific license information.
