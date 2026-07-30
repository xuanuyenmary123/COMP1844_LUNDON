import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

class Graph:
    def __init__(self):
        self.adjacency_list = {}
    def add_station(self, station):
        """Add a station if it does not already exist."""
        if station not in self.adjacency_list:
            self.adjacency_list[station] = []
    def add_connection(self, station1, station2, distance, line, colour):
        """Create a bidirectional connection."""
        self.add_station(station1)
        self.add_station(station2)
        edge = {
            "station": station2,
            "distance": distance,
            "line": line,
            "colour": colour
        }
        reverse_edge = {
            "station": station1,
            "distance": distance,
            "line": line,
            "colour": colour
        }
        self.adjacency_list[station1].append(edge)
        self.adjacency_list[station2].append(reverse_edge)
    def display_graph(self):
        """Display the graph structure."""
        for station, neighbours in self.adjacency_list.items():
            print(f"\n{station}")
            for edge in neighbours:
                print(edge)

def load_data(file_name):
    try:
        dataframe = pd.read_csv(file_name)
        return dataframe
    except Exception as error:
        print(error)
        return None

def validate_data(dataframe):
    required_columns = [
        "From Station",
        "To Station",
        "Line",
        "Distance",
        "Colour"
    ]
    for column in required_columns:
        if column not in dataframe.columns:
            raise ValueError(f"Missing column: {column}")

def build_graph(dataframe):
    graph = Graph()
    for _, row in dataframe.iterrows():
        graph.add_connection(
            row["From Station"],
            row["To Station"],
            row["Distance"],
            row["Line"],
            row["Colour"]
        )
    return graph

def convert_to_networkx(graph):
    G = nx.Graph()
    for station in graph.adjacency_list:
        for edge in graph.adjacency_list[station]:
            G.add_edge(
                station,
                edge["station"],
                distance=edge["distance"],
                colour=edge["colour"],
                line=edge["line"]
            )
    return G

def auto_adjust_view(pos, padding_ratio=0.15, min_padding=0.5):
    x_coords = [p[0] for p in pos.values()]
    y_coords = [p[1] for p in pos.values()]

    x_min = min(x_coords)
    x_max = max(x_coords)

    y_min = min(y_coords)
    y_max = max(y_coords)

    x_range = x_max - x_min
    y_range = y_max - y_min

    x_pad = max(x_range * padding_ratio, min_padding)
    y_pad = max(y_range * padding_ratio, min_padding)

    return (
        x_min - x_pad,
        x_max + x_pad,
        y_min - y_pad,
        y_max + y_pad
    )

def auto_figure_size(pos,
                     base_scale=1.8,
                     min_width=10,
                     min_height=8,
                     max_width=20,
                     max_height=16):

    x_coords = [p[0] for p in pos.values()]
    y_coords = [p[1] for p in pos.values()]

    x_range = max(x_coords) - min(x_coords)
    y_range = max(y_coords) - min(y_coords)

    width = np.clip(
        x_range * base_scale,
        min_width,
        max_width
    )
    height = np.clip(
        y_range * base_scale,
        min_height,
        max_height
    )
    return width, height

def get_positions():
    return {
        "Oxford Circus": (1.0, 10.0),
        "Piccadilly Circus": (2.3, 6.5),
        "Covent Garden": (4.7, 7.7),
        "Leicester Square": (3.6, 6.5),
        "Charing Cross": (3.6, 3.2),
    }

def draw_graph(G):
    positions = get_positions()
    width, height = auto_figure_size(positions)
    fig, ax = plt.subplots(figsize=(width, height))

    edge_colours = []
    for _, _, data in G.edges(data=True):
        edge_colours.append(data.get("colour", "#000000"))

    node_colours = ["#CCCCCC" for _ in G.nodes()]

    # Draw edges
    nx.draw_networkx_edges(
        G,
        positions,
        edge_color=edge_colours,
        width=4,
        ax=ax
    )
    # Draw nodes
    nx.draw_networkx_nodes(
        G,
        positions,
        node_size=450,
        node_color=node_colours,
        ax=ax
    )

    label_config = {
        "Oxford Circus": (1.160, 10.82, "left", "center", 0),
        "Piccadilly Circus": (2.033, 6.359, "right", "top", 18),
        "Covent Garden": (5.0, 7.7, "left", "center", 0),
        "Leicester Square": (3.9, 6.2, "left", "center", 0),
        "Charing Cross": (3.6, 2.5, "center", "top", 0),
    }

    # Draw station names
    for name, node_pos in positions.items():
        lx, ly, ha, va, rot = label_config.get(name, (node_pos[0], node_pos[1], "center", "center", 0))
        ax.text(
            lx,
            ly,
            name,
            fontsize=10,
            color="black",
            fontweight="normal",
            ha=ha,
            va=va,
            rotation=rot,
            zorder=5
        )

    # Distance labels
    drawn = set()

    for u, v, data in G.edges(data=True):
        edge = tuple(sorted((u, v)))
        if edge in drawn:
            continue
        drawn.add(edge)

        x1, y1 = positions[u]
        x2, y2 = positions[v]

        # Midpoint of the edge
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        # Rotation angle of the edge
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

        # Keep text upright
        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180

        # Unit vector perpendicular to the edge
        dx = x2 - x1
        dy = y2 - y1
        length = np.hypot(dx, dy)

        if length != 0:
            px = -dy / length
            py = dx / length
        else:
            px = py = 0

        # Move the label slightly away from the line
        offset = 0.10
        mx += px * offset
        my += py * offset

        ax.text(
            mx,
            my,
            f"{data['distance']} m",
            fontsize=8,
            color="black",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="square,pad=0.10",
                fc="white",
                ec="none",
                alpha=1.0
            ),
            zorder=6
        )
    legend = [
        Line2D([0], [0], color="blue", lw=2, label="Piccadilly"),
        Line2D([0], [0], color="black", lw=2, label="Northern"),
        Line2D([0], [0], color="#A65B11", lw=2, label="Bakerloo")
    ]

    leg = plt.legend(
        handles=legend,
        title="Key",
        loc="lower right",
        frameon=True,
        fancybox=False,
        edgecolor="black",
        framealpha=1,
        bbox_to_anchor=(0.95, 0.05),
        borderpad=1.2,
        labelspacing=1.0
    )
    
    for text, color in zip(leg.get_texts(), ["blue", "black", "#A65B11"]):
        text.set_color(color)

    plt.title(
       "London Underground Network Map",
        fontsize=16,
        fontweight="bold",
        pad=20,
        y=0.92
    )

    xmin, xmax, ymin, ymax = auto_adjust_view(positions)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    file_name = "Map London.csv"
    dataframe = load_data(file_name)
    if dataframe is None:
        return
    validate_data(dataframe)
    graph = build_graph(dataframe)
    print("\n========== Adjacency List ==========")
    graph.display_graph()
    G = convert_to_networkx(graph)
    draw_graph(G)

if __name__ == "__main__":
    main()