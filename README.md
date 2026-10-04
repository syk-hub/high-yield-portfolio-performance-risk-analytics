# High-Yield Portfolio Performance and Risk Analytics

This project packages the portfolio-performance and risk-analysis workflow described in the project specification into a runnable Python workflow and supporting SQL/data-quality templates.

## Project goal

The code reconciles a simulated high-yield portfolio and benchmark across an end-of-month snapshot, calculates bond-level and portfolio-level return attribution, and produces a static dashboard and manager note for review.

## Structure

- `portfolio_analytics.py` implements the holdings generation, return calculations, benchmark construction, validation assertions, and static dashboard exports.
- `sql/portfolio_schema.sql` defines the relational schema for holdings, benchmark, and exception records.
- `sql/validation_queries.sql` includes checks for duplicates, missing fields, reconciliations, and unacceptable price movements.
- `data/` stores the generated beginning/ending holdings files and provenance dictionary.
- `output/` stores the final static dashboard, note, and summary exports.

## Run

```bash
cd "c:\Users\syksh\Documents\high-yield-portfolio-performance-risk-analytics-1"
C:/Users/syksh/AppData/Local/Programs/Python/Python312/python.exe portfolio_analytics.py
```

## Validation

```bash
cd "c:\Users\syksh\Documents\high-yield-portfolio-performance-risk-analytics-1"
C:/Users/syksh/AppData/Local/Programs/Python/Python312/python.exe -m pytest -q
```

## Notes

- This is a simulation for educational and analytical use only.
- The effective duration and OAS values are supplied simulated inputs.
- The project intentionally follows the agreed return conventions in the specification.
