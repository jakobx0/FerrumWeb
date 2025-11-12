#!/usr/bin/env python3
"""
Create test data for FerrumWeb visualization testing
This script creates a sample database with hierarchical link data
"""

import sqlite3
import os

def create_test_database(db_path='data/links_test.db'):
    """Create a test database with sample hierarchical link data."""

    # Remove existing test database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing test database: {db_path}")

    # Create connection and table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table (same structure as the Rust crawler)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS link (
            id INTEGER PRIMARY KEY,
            URL TEXT NOT NULL,
            parent_id INTEGER,
            depth INTEGER
        )
    ''')

    # Sample hierarchical data
    test_links = [
        # Root (depth 0)
        (1, 'https://example.com/', 0, 0),

        # Depth 1
        (2, 'https://example.com/about', 1, 1),
        (3, 'https://example.com/products', 1, 1),
        (4, 'https://example.com/services', 1, 1),
        (5, 'https://example.com/contact', 1, 1),

        # Depth 2 - children of /products
        (6, 'https://example.com/products/software', 3, 2),
        (7, 'https://example.com/products/hardware', 3, 2),
        (8, 'https://example.com/products/consulting', 3, 2),

        # Depth 2 - children of /services
        (9, 'https://example.com/services/web-development', 4, 2),
        (10, 'https://example.com/services/mobile-apps', 4, 2),
        (11, 'https://example.com/services/cloud-solutions', 4, 2),

        # Depth 2 - children of /about
        (12, 'https://example.com/about/team', 2, 2),
        (13, 'https://example.com/about/history', 2, 2),

        # Depth 3 - children of /products/software
        (14, 'https://example.com/products/software/desktop', 6, 3),
        (15, 'https://example.com/products/software/web', 6, 3),
        (16, 'https://example.com/products/software/mobile', 6, 3),

        # Depth 3 - children of /services/web-development
        (17, 'https://example.com/services/web-development/frontend', 9, 3),
        (18, 'https://example.com/services/web-development/backend', 9, 3),
        (19, 'https://example.com/services/web-development/fullstack', 9, 3),

        # Depth 3 - children of /about/team
        (20, 'https://example.com/about/team/engineering', 12, 3),
        (21, 'https://example.com/about/team/sales', 12, 3),
        (22, 'https://example.com/about/team/support', 12, 3),
    ]

    # Insert test data
    cursor.executemany(
        'INSERT INTO link (id, URL, parent_id, depth) VALUES (?, ?, ?, ?)',
        test_links
    )

    conn.commit()
    conn.close()

    print(f"\nTest database created successfully: {db_path}")
    print(f"Total links inserted: {len(test_links)}")
    print("\nHierarchy structure:")
    print("  Depth 0: 1 node  (root)")
    print("  Depth 1: 4 nodes")
    print("  Depth 2: 8 nodes")
    print("  Depth 3: 9 nodes")
    print(f"\nYou can now visualize this data with:")
    print(f"  python visualize_hierarchy.py --db {db_path}")


if __name__ == '__main__':
    create_test_database()
