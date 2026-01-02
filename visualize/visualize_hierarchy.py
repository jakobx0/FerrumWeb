#Visualize the hierarchy of links stored in a FerrumWeb SQLite database using NetworkX and Matplotlib.
import sqlite3
import sys
import networkx as nx
from collections import defaultdict
import argparse
from urllib.parse import urlparse
from pyvis.network import Network
import os


#Search categories matching a keyword in URLs and assign category_id -> later outsource ans rewite in rust
def match_keyword(db_path='data/links.db' ):
    #Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE link SET category_id = (SELECT category_id FROM categories WHERE link.URL LIKE '%' || categories.category || '%')"
    )
    conn.commit()
    conn.close()


#Load links and their relationships from the SQLite database
#maby load after match keyword is run -> row + category id to reference categorie name
def load_links_from_db(db_path='data/links.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Fetch all links with their parent relationships
    cursor.execute("SELECT id, URL, parent_id, depth, category_id FROM link ORDER BY depth;")
    rows = cursor.fetchall()
    conn.close()
    
    #rows format: (id, url, parent_id, depth, categoery_id)
    return rows
    

#Create a directed graph from the database rows.
def create_graph(rows, max_depth=None, shorten_urls=True):
    
    G = nx.DiGraph()

    #Store node attributes
    node_labels = {}
    node_depths = {}
    node_category = {}
    
    #Build the nodes
    for node_id, url, parent_id, depth, category_id in rows:
        # Skip if beyond max_depth
        if max_depth is not None and depth > max_depth:
            continue
        label = url
        #Add node
        G.add_node(node_id, url=url, depth=depth, label=label, category_id=category_id)
        node_labels[node_id] = label
        node_depths[node_id] = depth
        node_category[node_id] = category_id

        #Add edge from parent (if not root) 
        if parent_id > 0 and parent_id in G.nodes():
            G.add_edge(parent_id, node_id)

    return G, node_labels, node_depths, node_category


def visualize_interactive(G, node_depths, node_category, output_file='link_hierarchy.html'):
    #Visualize graph interactively using PyVis
    print(f"Generating interactive graph: {output_file}")
    
    #Create network
    nt = Network(height='90vh', width='100%', bgcolor='#222222', font_color='white', select_menu=True)
    
    #Enable physics for better separation -> needs some fine tuning
    nt.barnes_hut(gravity=-2000, central_gravity=0.3, spring_length=95, spring_strength=0.1, damping=0.09, overlap=0)
    
    #Add nodes with custom styling
    max_depth = max(node_depths.values()) if node_depths else 1

    #implement color for diffrent keywords
    keyword_colors = {
        1: '#ff9999',  # Category 1 - Light Red
        2: '#99ff99',  # Category 2 - Light Green
        3: '#9999ff',  # Category 3 - Light Blue
        4: '#ffff99',  # Category 4 - Light Yellow
        5: '#ff99ff',  # Category 5 - Light Magenta
        6: '#99ffff',  # Category 6 - Light Cyan
        7: '#ffcc99',  # Category 7 - Light Orange
        8: '#ffcc99',   # Category 8 - Light Orange
        9: '#cc99ff',   # Category 9 - Light Purple
        10: '#99ccff',  # Category 10 - Sky Blue
        11: '#ffff99',  # Category 11 - Light Yellow
        12: '#ff99cc',  # Category 12 - Light Pink
        13: '#99ffcc',  # Category 13 - Mint Green
        14: '#ccff99',  # Category 14 - Pale Green
        15: '#ff9999',  # Category 15 - Light Red
        16: '#9999ff',  # Category 16 - Light Blue
        17: '#ffcccc',  # Category 17 - Pale Red
        18: '#ccffcc',  # Category 18 - Pale Green
        19: '#ccccff',  # Category 19 - Pale Blue
        20: '#ffffcc',  # Category 20 - Pale Yellow
        21: '#ffccff',  # Category 21 - Pale Magenta
        22: '#ccffff',  # Category 22 - Pale Cyan

        23: '#ff0000',  # Category 23 - YouTube Red
        24: '#1DA1F2',  # Category 24 - Twitter Blue
        25: '#1877F2',  # Category 25 - Facebook Blue
        26: '#0A66C2',  # Category 26 - LinkedIn Blue
        27: '#E4405F',  # Category 27 - Instagram Pink
        28: '#FF4500',  # Category 28 - Reddit Orange
        29: '#333333',  # Category 29 - GitHub Dark
        30: '#000000',  # Category 30 - TikTok Black
        31: '#FFFC00',  # Category 31 - Snapchat Yellow
        32: '#000000',  # Category 32 - X Black
        33: '#25D366',  # Category 33 - WhatsApp Green
        34: '#5865F2',  # Category 34 - Discord Blurple
        # Add more categories/colors as needed
    }
    
    # Define colors for depths (simple palette) -> implement a dynamic solution
    """
    depth_colors = {
        0: '#ff4b4b',  # Red for root
        1: '#4b79ff',  # Blue for depth 1
        2: '#4bff79',  # Green for depth 2
        3: '#ffb74b',  # Orange for depth 3
        4: '#b74bff',  # Purple for depth 4
    }
    """
    
    #Prepare Nodes for visualization
    for node, data in G.nodes(data=True):
        #test
        #print (f"Node: {node}, Data: {data}")
        
        depth = data.get('depth')
        url = data.get('url', '')
        categorie = data.get('category_id')
        
        #Test
        print(f"Category ID: {categorie}")
        #color = depth_colors.get(depth, '#aaaaaa')
        
        color = keyword_colors.get(categorie, '#aaaaaa')
        
        #Test
        print(f"Color: {color}")
        label=url
        
        nt.add_node(
            node, 
            label=label, 
            title=f"URL: {url}\nDepth: {depth}\nCategory ID: {categorie}", 
            color=color,
            size=20 if depth == 0 else 10,
            group=depth
        )

    #Add edges
    for source, target in G.edges():
        nt.add_edge(source, target, color='#555555')

    #Add controls
    nt.show_buttons(filter_=['physics'])
    
    #Save to HTML file
    try:
        nt.save_graph(output_file)
        print(f"Interactive visualization saved to {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Error saving interactive graph: {e}")


def print_statistics(G, node_depths):
    #Print statistics
    print("\n" + "="*50)
    print("Graph Statistics")
    print("="*50)
    print(f"Total nodes: {G.number_of_nodes()}")
    print(f"Total edges: {G.number_of_edges()}")
    print(f"Maximum depth: {max(node_depths.values())}")

    #Depth distribution
    depth_counts = defaultdict(int)
    for depth in node_depths.values():
        depth_counts[depth] += 1

    print("\nNodes per depth level:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} nodes")

    #Find nodes with most children
    out_degrees = dict(G.out_degree())
    if out_degrees:
        max_children = max(out_degrees.values())
        print(f"\nMaximum children per node: {max_children}")

    print("="*50 + "\n")


def main():
    #Read arguments
    parser = argparse.ArgumentParser(
        description='Visualize FerrumWeb link hierarchy using NetworkX'
    )
    # --db data/links_test.db
    parser.add_argument(
        '--db',
        default='data/links.db',
        help='Path to SQLite database (default: data/links.db)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Generate interactive HTML visualization using PyVis'
    )
    args = parser.parse_args()

    #Match keywords to categories in DB
    print(f"Matching keywords in database {args.db}...")
    try:
        match_keyword(args.db)
    except Exception as e:
        print(f"Error matching keywords: {e}")

    # Load data -> cmp args.db
    print(f"Loading links from {args.db}...")
    try:
        rows = load_links_from_db(args.db)
        print(f"Loaded {len(rows)} links from database")
    except Exception as e:
        print(f"Error loading database: {e}")
        return

    #Create graph with rows from data base
    G, node_labels, node_depths, node_category = create_graph(rows)

    #Print statistics
    print_statistics(G, node_depths)

    #For no input arguments or non existing ones -> genearate all
    if len(sys.argv) == 1:
        visualize_interactive(G, node_depths,node_category)

    # Generate interactive visualization -i or --interactive
    if args.interactive:
        visualize_interactive(G, node_depths, node_category)

    print("\nVisualization complete!")


if __name__ == '__main__':
    main()
