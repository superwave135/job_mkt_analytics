#!/usr/bin/env python3
import argparse
import os
import sys
import tempfile
import re

def sample_csv(src, n):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    with open(src, 'r', encoding='utf-8', errors='replace') as fr, open(tmp.name, 'w', encoding='utf-8') as fw:
        header = fr.readline()
        if not header:
            raise SystemExit('Empty CSV')
        fw.write(header)
        for i, line in enumerate(fr):
            if i >= n:
                break
            fw.write(line)
    return tmp.name

def valid_table_name(name):
    return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name) is not None

def main():
    parser = argparse.ArgumentParser(description='Create a DuckDB file from a CSV')
    parser.add_argument('--csv', '-c', required=True, help='Path to CSV file')
    parser.add_argument('--db', '-d', default='SGJobData.duckdb', help='Output DuckDB file')
    parser.add_argument('--table', '-t', default='jobs', help='Table name to store CSV data')
    parser.add_argument('--sample', '-s', type=int, help='Import only first N rows (for testing)')
    parser.add_argument('--overwrite', action='store_true', help='Drop table if it exists and re-create')
    parser.add_argument('--delimiter', '-l', help='CSV delimiter (single character). Let DuckDB auto-detect if omitted')
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print('CSV not found:', args.csv, file=sys.stderr)
        sys.exit(1)

    if not valid_table_name(args.table):
        print('Invalid table name. Use letters, numbers, and underscores, not starting with a number.', file=sys.stderr)
        sys.exit(1)

    try:
        import duckdb
    except Exception:
        print("duckdb module not installed. Run: pip install duckdb", file=sys.stderr)
        sys.exit(2)

    csv_to_use = args.csv
    tmp = None
    if args.sample is not None:
        tmp = sample_csv(args.csv, args.sample)
        csv_to_use = tmp

    conn = duckdb.connect(database=args.db, read_only=False)
    try:
        if args.overwrite:
            conn.execute(f"DROP TABLE IF EXISTS {args.table}")

        opts = ['header=True']
        if args.delimiter:
            if len(args.delimiter) != 1:
                print('Delimiter must be a single character', file=sys.stderr)
                sys.exit(3)
            opts.append(f"delim='{args.delimiter}'")

        opts_sql = ', '.join(opts)
        sql = f"CREATE TABLE {args.table} AS SELECT * FROM read_csv_auto('{csv_to_use}', {opts_sql});"
        conn.execute(sql)
    finally:
        conn.close()

    if tmp:
        try:
            os.remove(tmp)
        except Exception:
            pass

    size = os.path.getsize(args.db) if os.path.exists(args.db) else 0
    print(f'Created {args.db} ({size} bytes)')

if __name__ == '__main__':
    main()
