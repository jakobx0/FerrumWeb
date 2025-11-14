#Visualize the hierarchy of links stored in a FerrumWeb SQLite database using NetworkX and Matplotlib.

import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import argparse
from urllib.parse import urlparse

#Load links and their relationships from the SQLite database
def load_links_from_db(db_path='data/links.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Fetch all links with their parent relationships
    cursor.execute("SELECT id, URL, parent_id, depth FROM link ORDER BY depth, id")
    rows = cursor.fetchall()
    conn.close()

    #rows format: (id, url, parent_id, depth)
    return rows

#Create a directed graph from the database rows.
def create_graph(rows, max_depth=None, shorten_urls=True):

    G = nx.DiGraph()

    # Store node attributes
    node_labels = {}
    node_depths = {}

    for node_id, url, parent_id, depth in rows:
        # Skip if beyond max_depth
        if max_depth is not None and depth > max_depth:
            continue
        
        label = url

        # Add node
        G.add_node(node_id, url=url, depth=depth, label=label)
        node_labels[node_id] = label
        node_depths[node_id] = depth

        # Add edge from parent (if not root)
        if parent_id > 0 and parent_id in G.nodes():
            G.add_edge(parent_id, node_id)

    return G, node_labels, node_depths

#tree -> visualize using hierarchical tree layout
def visualize_tree_layout(G, node_labels, node_depths, output_file='link_hierarchy_tree.png'):
    if len(G.nodes()) == 0:
        print("No nodes to visualize!")
        return

    try:
        plt.figure(figsize=(20, 12))
    except:
        print("Warning: Unable to set figure size, using default.")

    # Use graphviz layout for hierarchical structure (if available)
    try:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        # Fallback to spring layout with custom parameters
        print("Error: spring layout not available.")

    # Color nodes by depth
    max_depth = max(node_depths.values()) if node_depths else 1
    colors = [plt.cm.viridis(node_depths[node] / max_depth) for node in G.nodes()]

    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=500, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                          arrowsize=10, alpha=0.6, width=1.5)

    # Draw labels (only for smaller graphs)
    if len(G.nodes()) < 50:
        nx.draw_networkx_labels(G, pos, node_labels, font_size=8)

    plt.title('Link Hierarchy Visualization', fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Tree layout visualization saved to: {output_file}")
    plt.close()

#Visualize the graph using a circular layout grouped by depth.
def visualize_circular_layout(G, node_labels, node_depths, output_file='link_hierarchy_circular.png'):
    if len(G.nodes()) == 0:
        print("No nodes to visualize!")
        return

    plt.figure(figsize=(16, 16))

    # Group nodes by depth
    depth_groups = defaultdict(list)
    for node, depth in node_depths.items():
        depth_groups[depth].append(node)

    # Create circular layout with depths as concentric circles
    pos = {}
    max_depth = max(depth_groups.keys()) if depth_groups else 0

    for depth, nodes in depth_groups.items():
        # Calculate radius based on depth (root at center)
        radius = (depth + 1) * 2
        angle_step = 2 * 3.14159 / len(nodes) if nodes else 0

        for i, node in enumerate(nodes):
            angle = i * angle_step
            import math
            pos[node] = (radius * math.cos(angle), radius * math.sin(angle))

    # Color nodes by depth
    colors = [plt.cm.plasma(node_depths[node] / max_depth) if max_depth > 0 else 0.5
              for node in G.nodes()]

    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=300, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                          arrowsize=8, alpha=0.4, width=1)

    # Draw labels only for small graphs
    if len(G.nodes()) < 30:
        nx.draw_networkx_labels(G, pos, node_labels, font_size=6)

    plt.title('Link Hierarchy - Circular Layout (Depth-based)', fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Circular layout visualization saved to: {output_file}")
    plt.close()


def print_statistics(G, node_depths):
    """Print graph statistics."""
    print("\n" + "="*50)
    print("Graph Statistics")
    print("="*50)
    print(f"Total nodes: {G.number_of_nodes()}")
    print(f"Total edges: {G.number_of_edges()}")
    print(f"Maximum depth: {max(node_depths.values()) if node_depths else 0}")

    # Depth distribution
    depth_counts = defaultdict(int)
    for depth in node_depths.values():
        depth_counts[depth] += 1

    print("\nNodes per depth level:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} nodes")

    # Find nodes with most children
    out_degrees = dict(G.out_degree())
    if out_degrees:
        max_children = max(out_degrees.values())
        print(f"\nMaximum children per node: {max_children}")

    print("="*50 + "\n")


def main():
    #use --help for options
    parser = argparse.ArgumentParser(
        description='Visualize FerrumWeb link hierarchy using NetworkX'
    )
    #to use teser python -u visualize_hierarchy.py --db data/links_test.db
    parser.add_argument(
        '--db',
        default='data/links.db',
        help='Path to SQLite database (default: data/links.db)'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=None,
        help='Maximum depth to visualize (default: all depths)'
    )
    parser.add_argument(
        '--layout',
        choices=['tree', 'circular', 'all'],
        default='all',
        help='Layout type for visualization (default: all)'
    )
    parser.add_argument(
        '--output-prefix',
        default='link_hierarchy',
        help='Output file prefix (default: link_hierarchy)'
    )

    args = parser.parse_args()

    # Load data
    print(f"Loading links from {args.db}...")
    try:
        rows = load_links_from_db(args.db)
        print(f"Loaded {len(rows)} links from database")
    except Exception as e:
        print(f"Error loading database: {e}")
        return

    # Create graph
    G, node_labels, node_depths = create_graph(
        rows,
        max_depth=args.max_depth,
    )

    # Print statistics
    print_statistics(G, node_depths)

    # Generate visualizations
    if args.layout in ['tree', 'all']:
        print("Generating tree layout...")
        visualize_tree_layout(G, node_labels, node_depths,
                            f'{args.output_prefix}_tree.png')

    if args.layout in ['circular', 'all']:
        print("Generating circular layout...")
        visualize_circular_layout(G, node_labels, node_depths,
                                 f'{args.output_prefix}_circular.png')

    print("\nVisualization complete!")

if __name__ == '__main__':
    main()
