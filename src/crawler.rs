use crate::db;
use reqwest;
use rusqlite::Connection;
use scraper::{Html, Selector};
use std::error::Error;

// webscraper
pub fn seaker(conn: &Connection, url_input: String, depth: usize, depth_max: usize, parent_id: i64) -> Result<(), Box<dyn Error>> {

    //max depth to search through
    if depth > depth_max {
        return Ok(());
    }
    
    //init client to send request
    let client = reqwest::blocking::Client::new();

    //send request
    let response = client.get(&url_input)
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, wie Gecko) Chrome/100.0.4896.127 Safari/537.36")
        .send()?;
    
    //ask status
    if !response.status().is_success() {
        eprintln!("Failed to call: {}, Status: {}", url_input, response.status());
    }
    
    //search for new links in input url -> look for new links in those and so on...
    let body = response.text()?;
    let document = Html::parse_document(&body);
    let selector_link = Selector::parse("a").unwrap();

    print!("\n");
    println!("links found on {} (Depth: {})", url_input, depth);
    //print partent_id ->> TEST
    println!("------------------------{}---------------------------", parent_id);

    //vector with new links and their db ids
    let mut new_links: Vec<(String, i64)> = Vec::new();

    //list all links
    for element in document.select(&selector_link){
        if let Some(link) = element.value().attr("href"){
        //owner -> String
        let absolute_link: String = if link.starts_with("http://") || link.starts_with("https://"){
            link.to_string()
        }else{
            continue;
        };
            //print discovert links
            println!("- {} Depth: {}", absolute_link, depth);
            
            //parse absolute_link -> insert_link with correct parent_id
            let link_id = db::insert_link(conn ,&absolute_link, depth + 1, parent_id)?;

            //no doubles
            if !new_links.iter().any(|(u, _)| u == &absolute_link){
                new_links.push((absolute_link, link_id));
             }
        }
    }
    println!("---------------------------------------------------");

    //Recursive call -> new links -> search trough new links +1 depth 
    //TODO Problem with depth+1 
    for (link, link_id) in new_links{
        seaker(conn, link, depth+1, depth_max, link_id).expect("seaker error");
    }
    Ok(())
}
