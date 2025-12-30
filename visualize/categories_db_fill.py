import sqlite3

connection = sqlite3.connect('data/links.db')

cursor = connection.cursor()

#is all ready covered in db.rs! -> remove 
sql_command = """
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category TEXT UNIQUE);"""   

cursor.execute(sql_command)

categories = [
    #genaral website categories
    (1, 'Home'),
    (2, 'About'),
    (3, 'Contact'),
    (4, 'Blog'),
    (5, 'Careers'),
    (6, 'Team'),
    (7, 'Support'),
    (8, 'FAQ'),
    (9, 'Tutorials'),
    (10, 'News'),
    (11, 'Events'),
    (12, 'Products'),
    (13, 'Services'),
    (14, 'Pricing'),
    (15, 'Testimonials'),
    (16, 'Portfolio'),
    (17, 'Resources'),
    (18, 'Community'),
    (19, 'Partners'),
    (20, 'Developers'),
    (21, 'Documentation'),
    (22, 'API'),
    
    #social media categories
    (23, 'youTube'),
    (24, 'Twitter'),
    (25, 'Facebook'),
    (26, 'LinkedIn'),
    (27, 'Instagram'),
    (28, 'Reddit'),
    (29, 'GitHub'),
    (30, 'TikTok'),
    (31, 'Snapchat'),
    (32, 'X'),
    (33, 'Whatsapp'),
    (34, 'Discord'),
    ]

for c in categories:
    formatted_sql = "INSERT INTO categories (category_id, category) VALUES (?, ?);"
    cursor.execute(formatted_sql, c)   
connection.commit()
connection.close()


