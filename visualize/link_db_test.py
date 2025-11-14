#this is just an example script to create a test database.

import sqlite3

#connect to database (or create if not exists)
connection = sqlite3.connect('data/links_test.db')
#create a pointer to execute SQL commands
cursor = connection.cursor()

#create table
sql_command = """
CREATE TABLE IF NOT EXISTS link (
    id INTEGER PRIMARY KEY,
    url text not null,
    parent_id INTEGER,
    depth INTEGER);"""

cursor.execute(sql_command)

#example data
staff_links = [
    (1, 'http://example.com', 0, 0),    
    (2, 'http://example.com/about', 1, 1),
    (3, 'http://example.com/contact', 1, 1),
    (4, 'http://example.com/about/team', 2, 2),
    (5, 'http://example.com/about/careers', 2, 2),
    (6, 'http://example.com/contact/form', 3, 2),
    (7, 'http://example.com/contact/map', 3, 2),
    (8, 'http://example.com/blog', 1, 1),
    (9, 'http://example.com/blog/post1', 8, 2),
    (10, 'http://example.com/blog/post2', 8, 2),
    (11, 'http://example.com/blog/post3', 8, 2 ),
    (12, 'http://example.com/blog/post4', 8, 2),
    (13, 'http://example.com/blog/post5', 8, 2),
    (14, 'http://example.com/blog/post6', 8, 2),
    (15, 'http://example.com/blog/post7', 8, 2),
    (16, 'http://example.com/blog/post8', 8, 2),
    (17, 'http://example.com/blog/post9', 8, 2),
    (18, 'http://example.com/blog/post10', 8, 2),
    (19, 'http://example.com/blog/post11', 8, 2),
    (20, 'http://example.com/blog/post12', 8, 2),
    (21, 'http://example.com/blog/post13', 8, 2),
    (22, 'http://example.com/blog/post14', 8, 2),
    (23, 'http://example.com/blog/post15', 8, 2),
    (24, 'http://example.com/blog/post16', 8, 2),
    (25, 'http://example.com/blog/post17', 8, 2),
    (26, 'http://example.com/blog/post18', 8, 2),
    (27, 'http://example.com/blog/post19', 8, 2),
    (28, 'http://example.com/blog/post20', 8, 2) ]

#insert data into table
for p in staff_links:
    formatted_sql = "INSERT INTO link (id, url, parent_id, depth) VALUES (?, ?, ?, ?);"
    cursor.execute(formatted_sql, p)
connection.commit()
connection.close()

