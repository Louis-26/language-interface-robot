import matplotlib.pyplot as plt
import networkx as nx

def visualize_path(path_str):
    """
    Visualizes the nasal anatomy graph and highlights the endoscope path.
    """
    # Define full anatomy graph (bidirectional)
    edges = [
        ("nose", "nasal_meatus"),
        ("nasal_meatus", "superior_nasal_meatus"),
        ("nasal_meatus", "middle_nasal_meatus"),
        ("nasal_meatus", "inferior_nasal_meatus"),
        ("middle_nasal_meatus", "concha_nasalis_media"),
        ("concha_nasalis_media", "sinus_maxillaris"),
        ("concha_nasalis_media", "bulla_ethmoidalis"),
        ("concha_nasalis_media", "sinus_ethmoidalis"),
        ("sinus_ethmoidalis", "sinus_sphenoidalis")
    ]

    G = nx.Graph()
    G.add_edges_from(edges)

    # Parse path from LLM output
    nodes_in_path = [node.strip(" []") for node in path_str.strip().split("->")]

    # Highlighted edges for the endoscope path
    path_edges = list(zip(nodes_in_path, nodes_in_path[1:]))

    # Position layout
    pos = nx.spring_layout(G, seed=42)

    # Draw full graph
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightgray', node_size=1200, edge_color='gray', width=1.5)

    # Highlight path
    nx.draw_networkx_nodes(G, pos, nodelist=nodes_in_path, node_color='lightcoral', node_size=1400)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3)

    # Highlight start and end nodes
    if nodes_in_path:
        nx.draw_networkx_nodes(G, pos, nodelist=[nodes_in_path[0]], node_color='green', node_size=1600, label="Start")  # Start node
        nx.draw_networkx_nodes(G, pos, nodelist=[nodes_in_path[-1]], node_color='blue', node_size=1600, label="End")    # End node

    # Title and legend
    import matplotlib.lines as mlines

    # Define custom legend markers to match node colors and shapes
    start_marker = mlines.Line2D([], [], color='green', marker='o', linestyle='None',
                                markersize=15, label='Start')
    end_marker = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                            markersize=15, label='End')

    # Add the legend
    plt.legend(handles=[start_marker, end_marker], loc='upper left', fontsize=12)
    plt.title("Endoscope Navigation Path", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()