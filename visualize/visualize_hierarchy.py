#Visualize the hierarchy of links stored in a FerrumWeb SQLite database.
import argparse
import os
import sqlite3
from collections import defaultdict
from html import escape
from urllib.parse import urlparse

import networkx as nx
from pyvis.network import Network

#Define categories with associated keywords and colors for visualization.
#TODO - expand categories and keywords over time based on real data patterns.
CATEGORY_DEFINITIONS = [
    (0, "Root", "#FF7F24", ("root",)),
    (1, "Home", "#ff9999", ("home",)),
    (2, "About", "#99ff99", ("about",)),
    (3, "Contact", "#9999ff", ("contact",)),
    (4, "Blog", "#ffff99", ("blog", "posts", "articles")),
    (5, "Careers", "#ff99ff", ("career", "careers", "jobs")),
    (6, "Team", "#99ffff", ("team", "staff")),
    (7, "Support", "#ffcc99", ("support", "help")),
    (8, "FAQ", "#ffcc99", ("faq", "frequently-asked")),
    (9, "Tutorials", "#cc99ff", ("tutorial", "tutorials", "guide", "guides")),
    (10, "News", "#99ccff", ("news", "updates")),
    (11, "Events", "#ffff99", ("event", "events")),
    (12, "Products", "#ff99cc", ("product", "products")),
    (13, "Services", "#99ffcc", ("service", "services")),
    (14, "Pricing", "#ccff99", ("pricing", "plans")),
    (15, "Testimonials", "#ff9999", ("testimonial", "testimonials", "reviews")),
    (16, "Portfolio", "#9999ff", ("portfolio", "work")),
    (17, "Resources", "#ffcccc", ("resource", "resources")),
    (18, "Community", "#ccffcc", ("community", "forum", "forums")),
    (19, "Partners", "#ccccff", ("partner", "partners")),
    (20, "Developers", "#ffffcc", ("developer", "developers", "dev")),
    (21, "Documentation", "#ffccff", ("documentation", "docs")),
    (22, "API", "#ccffff", ("api",)),
    (23, "YouTube", "#EE3A8C", ("youtube.com", "youtu.be", "youtube")),
    (24, "Twitter", "#1DA1F2", ("twitter.com", "twitter")),
    (25, "Facebook", "#1877F2", ("facebook.com", "facebook")),
    (26, "LinkedIn", "#0A66C2", ("linkedin.com", "linkedin")),
    (27, "Instagram", "#9A32CD", ("instagram.com", "instagram")),
    (28, "Reddit", "#FF4500", ("reddit.com", "reddit")),
    (29, "GitHub", "#333333", ("github.com", "github")),
    (30, "TikTok", "#000000", ("tiktok.com", "tiktok")),
    (31, "Snapchat", "#FFFC00", ("snapchat.com", "snapchat")),
    (32, "X", "#000000", ("x.com",)),
    (33, "WhatsApp", "#25D366", ("whatsapp.com", "wa.me", "whatsapp")),
    (34, "Discord", "#5865F2", ("discord.gg", "discord.com", "discord")),
    (35, "admin", "#ff0000", ("admin", "administrator")),
    (36, "login", "#ff0000", ("login", "signin", "signup", "register")),
]

CATEGORY_LABELS = {category_id: label for category_id, label, _, _ in CATEGORY_DEFINITIONS}
CATEGORY_COLORS = {category_id: color for category_id, _, color, _ in CATEGORY_DEFINITIONS}
CATEGORY_KEYWORDS = {category_id: keywords for category_id, _, _, keywords in CATEGORY_DEFINITIONS}

DEFAULT_COLOR = "#aaaaaa"
DEFAULT_CATEGORY_LABEL = "Uncategorized"


def has_table(cursor, table_name):
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1;",
        (table_name,),
    )
    return cursor.fetchone() is not None


def get_table_columns(cursor, table_name):
    if not has_table(cursor, table_name):
        return set()

    cursor.execute(f"PRAGMA table_info({table_name});")
    return {row[1] for row in cursor.fetchall()}

#TODO Dynamically match keywords to categories based on database content patterns instead of hardcoding.
def match_keyword(db_path="data/links.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        link_columns = get_table_columns(cursor, "link")
        if "category_id" not in link_columns or not has_table(cursor, "categories"):
            print("Skipping keyword/category sync: database has no categories schema.")
            return

        cursor.execute(
            """
            UPDATE link
            SET category_id = (
                SELECT category_id
                FROM categories
                WHERE lower(link.url) LIKE '%' || lower(categories.category) || '%'
                LIMIT 1
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

#TODO dynamic database schema handling to avoid hardcoded assumptions about columns.
def load_links_from_db(db_path="data/links.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        link_columns = get_table_columns(cursor, "link")
        if "category_id" in link_columns:
            query = "SELECT id, url, parent_id, depth, category_id FROM link ORDER BY depth, id;"
        else:
            query = "SELECT id, url, parent_id, depth, NULL AS category_id FROM link ORDER BY depth, id;"

        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def create_graph(rows, max_depth=None, shorten_urls=True):
    G = nx.DiGraph()

    node_labels = {}
    node_depths = {}
    node_category = {}

    for node_id, url, parent_id, depth, category_id in rows:
        if max_depth is not None and depth > max_depth:
            continue

        label = url
        G.add_node(node_id, url=url, depth=depth, label=label, category_id=category_id)
        node_labels[node_id] = label
        node_depths[node_id] = depth
        node_category[node_id] = category_id

        if parent_id > 0 and parent_id in G.nodes():
            G.add_edge(parent_id, node_id)

    return G, node_labels, node_depths, node_category

#Prioritize exact path segment matches for category inference, then domain/keyword matches, then partial matches.
def infer_category_id(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc.lower()
    path = parsed_url.path.strip("/").lower()

    if not path:
        return 0

    searchable_text = f"{hostname}/{path}"
    path_segments = [segment for segment in path.split("/") if segment]

    #Domain-based platforms should win immediately.
    for category_id in range(23, 35):
        keywords = CATEGORY_KEYWORDS.get(category_id, ())
        if any(keyword in searchable_text for keyword in keywords):
            return category_id

    #Prefer the deepest matching path segment so /about/team becomes Team.
    for segment in reversed(path_segments):
        for category_id in range(2, 23):
            keywords = CATEGORY_KEYWORDS.get(category_id, ())
            if any(keyword == segment or keyword in segment for keyword in keywords):
                return category_id

    for category_id in range(2, 23):
        keywords = CATEGORY_KEYWORDS.get(category_id, ())
        if any(keyword in searchable_text for keyword in keywords):
            return category_id

    return None


def resolve_category(url, category_id):
    if category_id in CATEGORY_LABELS:
        return category_id, CATEGORY_LABELS[category_id], CATEGORY_COLORS[category_id]

    inferred_category_id = infer_category_id(url)
    if inferred_category_id in CATEGORY_LABELS:
        return (
            inferred_category_id,
            CATEGORY_LABELS[inferred_category_id],
            CATEGORY_COLORS[inferred_category_id],
        )

    return None, DEFAULT_CATEGORY_LABEL, DEFAULT_COLOR

#TODO - implement dynamic legend generation based on categories actually used in the graph instead of static legend. 
#(Outsource to separate module if it becomes complex)
def build_legend_markup(used_categories):
    if not used_categories:
        return ""

    sorted_categories = sorted(
        used_categories.items(),
        key=lambda item: (item[0] is None, item[0] or 0),
    )

    legend_items = []
    for _, (label, color) in sorted_categories:
        legend_items.append(
            (
                '<li class="legend-item">'
                f'<span class="legend-swatch" style="background:{escape(color, quote=True)};"></span>'
                f"<span>{escape(label)}</span>"
                "</li>"
            )
        )

    items_markup = "\n".join(legend_items)

    return f"""
<style>
    #graph-legend {{
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 1000;
        width: min(280px, calc(100vw - 32px));
        max-height: 60vh;
        overflow-y: auto;
        padding: 16px 18px;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 14px;
        background: rgba(20, 20, 20, 0.92);
        color: #f5f5f5;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(10px);
    }}

    #graph-legend h2 {{
        margin: 0 0 10px;
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
    }}

    #graph-legend ul {{
        list-style: none;
        margin: 0;
        padding: 0;
    }}

    #graph-legend .legend-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 8px 0;
        font-size: 0.95rem;
        line-height: 1.3;
    }}

    #graph-legend .legend-swatch {{
        width: 14px;
        height: 14px;
        flex: 0 0 14px;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }}

    @media (max-width: 768px) {{
        #graph-legend {{
            position: static;
            width: auto;
            max-height: none;
            margin: 16px;
        }}
    }}
</style>
<aside id="graph-legend" aria-label="Graph legend">
    <h2>Legend</h2>
    <ul>
        {items_markup}
    </ul>
</aside>
"""


def display_legend(output_file, used_categories):
    legend_markup = build_legend_markup(used_categories)
    if not legend_markup:
        return

    with open(output_file, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()

    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{legend_markup}\n</body>", 1)
    else:
        html_content += legend_markup

    with open(output_file, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


def visualize_interactive(G, node_depths, node_category, output_file="link_hierarchy.html"):
    print(f"Generating interactive graph: {output_file}")

    nt = Network(
        height="90vh",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        select_menu=True,
        layout=True,
    )
    #TODO: refactor physics
    """
    nt.barnes_hut(
        gravity=-2000, #-2000
        central_gravity=0.3,
        spring_length=95,
        spring_strength=0.1,
        damping=0.09,
        overlap=0,
    )
    """
    """
    nt.force_atlas_2based(
        gravity=-50,
        central_gravity=0,
        spring_length=0,
        spring_strength=0.08,
        damping=1,
    )
    """

    #tree layout with physics off to preserve hierarchy and improve readability, especially for larger graphs.
    
    nt.options.layout.hierarchical.direction = "UD"
    nt.options.layout.hierarchical.sortMethod = "directed"
    nt.options.layout.hierarchical.levelSeparation = 180
    nt.options.layout.hierarchical.nodeSpacing = 140
    nt.options.layout.hierarchical.treeSpacing = 220
    nt.options.layout.hierarchical.blockShifting = True
    nt.options.layout.hierarchical.edgeMinimization = True
    nt.options.layout.hierarchical.parentCentralization = True
    nt.options.layout.hierarchical.shakeTowards = "roots"
    nt.options.physics.enabled = False
    
    used_categories = {}

    for node, data in G.nodes(data=True):
        depth = data.get("depth", 0)
        url = data.get("url", "")
        category_id = data.get("category_id")

        resolved_category_id, category_label, color = resolve_category(url, category_id)
        used_categories[resolved_category_id] = (category_label, color)

        nt.add_node(
            node,
            label=url,
            title=f"URL: {url}\nDepth: {depth}\nCategory: {category_label}",
            color=color,
            size=20 if depth == 0 else 10,
        )

    for source, target in G.edges():
        nt.add_edge(source, target, color="#555555")

    nt.show_buttons(filter_=["physics"])
    
    #neighbor map
    neighbor_map = nt.get_adj_list()
    for node in nt.nodes:
        neighbors = neighbor_map.get(node["id"], [])
        #form string listing neighbor IDs 
        node["title"] += f"\nNeighbors: {', '.join(str(neighbor) for neighbor in neighbors)}"
        #weight node size
        node["value"] = len(neighbors) + 2

    try:
        nt.save_graph(output_file)
        display_legend(output_file, used_categories)
        print(f"Interactive visualization saved to {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Error saving interactive graph: {e}")


def print_statistics(G, node_depths):
    print("\n" + "=" * 50)
    print("Graph Statistics")
    print("=" * 50)
    print(f"Total nodes: {G.number_of_nodes()}")
    print(f"Total edges: {G.number_of_edges()}")
    print(f"Maximum depth: {max(node_depths.values(), default=0)}")

    depth_counts = defaultdict(int)
    for depth in node_depths.values():
        depth_counts[depth] += 1

    print("\nNodes per depth level:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} nodes")

    out_degrees = dict(G.out_degree())
    if out_degrees:
        max_children = max(out_degrees.values())
        print(f"\nMaximum children per node: {max_children}")

    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize FerrumWeb link hierarchy using NetworkX"
    )
    parser.add_argument(
        "--db",
        default="data/links.db",
        help="Path to SQLite database (default: data/links.db)",
    )
    args = parser.parse_args()

    print(f"Matching keywords in database {args.db}...")
    try:
        match_keyword(args.db)
    except Exception as e:
        print(f"Error matching keywords: {e}")

    print(f"Loading links from {args.db}...")
    try:
        rows = load_links_from_db(args.db)
        print(f"Loaded {len(rows)} links from database")
    except Exception as e:
        print(f"Error loading database: {e}")
        return

    G, node_labels, node_depths, node_category = create_graph(rows)

    print_statistics(G, node_depths)
    visualize_interactive(G, node_depths, node_category)

    print("\nVisualization complete!")


if __name__ == "__main__":
    main()
