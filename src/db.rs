use rusqlite::{params, Connection, Result};

pub fn init_db() -> Result<Connection> {
    //opens an connection -> links.db
    let conn = Connection::open("data/links.db")?;
    //create Table with all informations
    conn.execute(
        "CREATE TABLE IF NOT EXISTS link (
        id INTEGER PRIMARY KEY,
        URL TEXT NOT NULL,
        parent_id INTEGER,
        depth INTEGER
        )",
        (),
    )?;
    Ok(conn)
}

//insert link -> DB 
pub fn insert_link(conn: &Connection, url: &str, depth: usize, parent_id: i32) -> Result<i64>{
    conn.execute("INSERT INTO link (url, depth, parent_id) VALUES (?1, ?2, ?3)",
    params![url, depth as i64, parent_id],
    )?;
Ok(conn.last_insert_rowid())
}