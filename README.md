# FerrumWeb

FerrumWeb is a recursive web crawler written in Rust.
It starts from a root URL, discovers links, stores crawl results in SQLite, and provides Python-based visualization of the crawl graph.

## Highlights

- Recursive crawling with configurable max depth
- Stores crawl graph in SQLite (`link` + `categories` tables)
- Tracks parent-child URL relationships and depth
- Optional interactive graph visualization with PyVis
- Simple CLI workflow for quick local experiments

## Project Structure

```text
FerrumWeb/
├── src/
│   ├── main.rs           # CLI input flow + crawl entrypoint
│   ├── crawler.rs        # Recursive crawler logic
│   └── db.rs             # SQLite schema + inserts
├── visualize/
│   ├── visualize_hierarchy.py
│   ├── categories_db_fill.py
│   └── link_db_test.py
├── data/
│   ├── links.db
│   └── links_test.db
└── Cargo.toml
```

## Requirements

### Rust crawler

- Rust toolchain (stable recommended)
- Build essentials for your platform

Install Rust:

- https://www.rust-lang.org/tools/install

### Python visualization

- Python 3.9+
- `networkx`
- `pyvis`

## Quick Start

### 1) Clone and enter project

```bash
git clone https://github.com/jakobx0/FerrumWeb.git
cd FerrumWeb
```

### 2) Run crawler

```bash
cargo run
```

The CLI asks for:

1. Start URL (e.g. `https://example.com`)
2. Maximum depth (e.g. `2`)

Results are written to:

- `data/links.db`

## Python Environment (recommended)

Create and activate a virtual environment before installing visualization dependencies.

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install networkx pyvis
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install networkx pyvis
```

## Visualization Workflow

### Option A: Use test data

```bash
python -u "visualize/link_db_test.py"
python -u "visualize/categories_db_fill.py"
python -u "visualize/visualize_hierarchy.py" --db ./data/links_test.db
```

### Option B: Use crawler output

```bash
python -u "visualize/categories_db_fill.py"
python -u "visualize/visualize_hierarchy.py" --db ./data/links.db
```

Output:

- `link_hierarchy.html` (interactive graph)

Open it in your browser.

## Database Schema

FerrumWeb creates these tables:

### `categories`

- `category_id INTEGER PRIMARY KEY`
- `category TEXT UNIQUE`

### `link`

- `id INTEGER PRIMARY KEY`
- `url TEXT NOT NULL`
- `parent_id INTEGER`
- `depth INTEGER`
- `category_id INTEGER` (FK to `categories.category_id`)

## Known Limitations

- Currently processes only absolute `http://` and `https://` links
- No URL deduplication strategy in crawler/DB yet
- Error handling can be improved in recursive path
- Category matching logic in Python is currently simplistic

## Troubleshooting

### `cargo: command not found`

Install Rust and restart shell:

```bash
rustup --version
cargo --version
```

### Linux OpenSSL build issues (`openssl-sys`)

```bash
sudo apt update
sudo apt install -y libssl-dev pkg-config
```

### Windows linker error: `link.exe not found`

Try GNU toolchain fallback:

```bash
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu
```

## Contributing

Contributions are welcome.

Suggested flow:

1. Fork the repository
2. Create a feature branch
3. Make focused commits
4. Open a pull request with clear description and test steps

## License

No explicit license file is currently present in this repository.
If you intend to reuse or distribute this code, clarify licensing with the repository owner first.
