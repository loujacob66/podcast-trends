# Podcast Trends CLI

A command-line tool for importing and analyzing podcast download trends from Excel files.

---

## 📥 Importing a New Spreadsheet

To reset and re-import a new `.xlsx` file:

```bash
rm -f logs/podcast_trends.db
python import_from_excel.py data/YourSpreadsheet.xlsx
```

This will:
- Load **all sheets** from the Excel file
- Normalize the data (title, code, date, feature, etc.)
- Store it in a local SQLite database at `logs/podcast_trends.db`
- Print how many rows are imported

---

## 🚀 CLI Usage

Main entrypoint:

```bash
./bin/podcast [COMMAND] [OPTIONS]
```

---

## 📊 Commands

### `top`

View top podcast episodes ranked by `eq_full` or other metrics.

#### 🔧 Options

| Flag | Description |
|------|-------------|
| `--by` | Metric to sort by (default: `eq_full`) |
| `--limit` | Number of rows to return |
| `--year` | Filter by year (e.g., `--year 2023`) |
| `--after`, `--before` | Filter by date range |
| `--months` | Only include episodes in the past X months |
| `--features` | Partial match for one or more features (e.g., `--features HPC cast`) |
| `--verbose` | Show all columns |

#### 🧪 Examples

```bash
./bin/podcast top --limit 15
./bin/podcast top --year 2024 --features HPC
./bin/podcast top --after 2023-01-01 --before 2023-12-31
./bin/podcast top --months 6 --features HPCNB Mktg
./bin/podcast top --features cast --by downloads_full
./bin/podcast top --verbose
```

---

## 📦 Features Extracted

During import, each episode gets normalized with fields:

- `title` — full cleaned filename (e.g. `HPCNB_20240115`)
- `feature` — detected category like `HPCNB`, `Mktg_podcast`
- `code` — 3-digit code if found (e.g. `021`)
- `date`, `year`, `month` — from filename or folder path
- `downloads_full`, `downloads_partial`, `eq_full` — calculated metric
- `file_ext`, `size_per_download`, `url`

---

## ✅ Dependencies

- Python 3.9+
- `pandas`
- `typer`
- `tabulate`
- `openpyxl` (for Excel support)

Install them with:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pandas typer tabulate openpyxl
```

---

Let me know if you'd like CSV/JSON export, dashboard output, or a "top by feature" summary view!
