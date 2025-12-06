use rusqlite::{params, Connection, Result};

pub fn init_db() -> Result<Connection> {
    //opens an connection -> links.db
    let conn = Connection::open("data/links.db")?;
    //create Table for URLs -> Classifikator
    conn.execute_batch(


        "PRAGMA foreign_keys = ON;

        DROP TABLE IF EXISTS link;
        DROP TABLE IF EXISTS classifikator;

        CREATE TABLE IF NOT EXISTS classifikator (
        classification_id INTEGER PRIMARY KEY,
        classifikation TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS link (
        id INTEGER PRIMARY KEY,
        URL TEXT NOT NULL,
        parent_id INTEGER,
        depth INTEGER,
        classification_id INTEGER,
        FOREIGN KEY(classification_id) REFERENCES classifikator(classification_id)
        );"

    ).expect("Failed to generate Tables");
    Ok(conn)
}

//insert link -> DB 
pub fn insert_link(conn: &Connection, url: &str, depth: usize, parent_id: i32) -> Result<i64>{
    conn.execute("INSERT INTO link (url, depth, parent_id) VALUES (?1, ?2, ?3)",
    params![url, depth as i64, parent_id],
    )?;
Ok(conn.last_insert_rowid())
}