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
        # Piccadilly Line
        "King's Cross St Pancras": (4.568, 27.56),
        "Russell Square": (4.551, 15.22),
        "Holborn": (4.553, 8.42),
        "Covent Garden": (4.552, 3.11),
        "Leicester Square": (3.922, 0.06),
        "Piccadilly Circus": (3.396, 0.06),
        "Green Park": (2.528, 0.30),

        # Bakerloo Line
        "Paddington": (-0.266, 4.57),
        "Edgware Road": (0.004, 14.85),
        "Marylebone": (0.452, 18.97),
        "Baker Street": (0.964, 18.72),
        "Regent's Park": (1.750, 17.00),
        "Oxford Circus": (2.742, 11.57),
        "Charing Cross": (3.797, -6.86),

        # Northern Line
        "Camden Town": (3.875, 42.50),
        "Mornington Crescent": (3.875, 34.50),
        "Euston": (3.875, 26.50),
        "Tottenham Court Road": (3.875, 10.43),
        "Embankment": (3.80, -11.20),

        # Central Line
        "Marble Arch": (1.337, 11.57),
        "Bond Street": (2.10, 11.57),
        "Bank": (6.00, 9.32),

        # Victoria Line
        "Warren Street": (3.455, 20.81),
        "Victoria": (2.53, -8.50)
    }

def draw_graph(G):
    positions = get_positions()
    width, height = auto_figure_size(positions)
    fig, ax = plt.subplots(figsize=(width, height))
    edge_colours = []
    for _, _, data in G.edges(data=True):
        edge_colours.append(data.get("colour", "#000000"))

    # Node colours
    node_colours = []
    for node in G.nodes():
        incident_edges = list(G.edges(node, data=True))

        lines = {edge_data["line"] for _, _, edge_data in incident_edges}

        if len(lines) > 1:
            node_colours.append("#888888")      
        else:
            node_colours.append("white")        
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
        node_size=180,
        node_color=node_colours,
        edgecolors="black",
        linewidths=1.5,
        ax=ax
    )
    label_positions = {
        # Piccadilly Line
        "King's Cross St Pancras": (4.994, 27.62),
        "Russell Square": (4.920, 15.22),
        "Holborn": (4.943, 7.32),
        "Covent Garden": (4.842, 1.81),
        "Leicester Square": (4.250, -2.12),
        "Piccadilly Circus": (3.111, -2.12),
        "Green Park": (2.288, -0.00),

        # Bakerloo Line
        "Paddington": (-0.566, 4.57),
        "Edgware Road": (-0.296, 14.85),
        "Marylebone": (0.413, 22.14),
        "Baker Street": (0.980, 22.14),
        "Regent's Park": (1.799, 21.25),
        "Oxford Circus": (2.640, 15.50),
        "Charing Cross": (3.497, -6.86),

        # Northern Line
        "Camden Town": (3.502, 42.28),
        "Mornington Crescent": (3.402, 34.75),
        "Euston": (3.638, 26.96),
        "Tottenham Court Road": (3.516, 8.49),
        "Embankment": (3.50, -11.50),

        # Central Line
        "Marble Arch": (1.263, 9.08),
        "Bond Street": (2.091, 9.08),
        "Bank": (6.019, 7.23),

        # Victoria Line
        "Warren Street": (3.150, 21.99),
        "Victoria": (2.33, -8.50)
    }

    # Draw station names 
    for name, node_pos in positions.items():
        lx, ly = label_positions.get(name, node_pos)
        ax.text(
            lx,
            ly,
            name,
            fontsize=9,
            color="black",
            ha="center",
            va="center",
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
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ax.text(
            mx,
            my,
            f"{data['distance']} m",
            fontsize=8,
            color="#444444",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.15",
                fc="white",
                ec="none",
                alpha=1
            )
        )
    # Legend
    legend = [
        Line2D([0], [0], color="#003688", lw=4, label="Piccadilly"),
        Line2D([0], [0], color="#000000", lw=4, label="Northern"),
        Line2D([0], [0], color="#B36305", lw=4, label="Bakerloo"),
        Line2D([0], [0], color="#E32017", lw=4, label="Central"),
        Line2D([0], [0], color="#0098D4", lw=4, label="Victoria"),
        Line2D([0], [0],marker='o',linestyle='None',markerfacecolor="white",markeredgecolor="black",markersize=8,label="Station"),
        Line2D([0], [0],marker='o',linestyle='None',markerfacecolor="#888888",markeredgecolor="black",markersize=8,label="Interchange station")
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

    for text in leg.get_texts():

        if "Piccadilly" in text.get_text():
            text.set_color("#003688")
        elif "Northern" in text.get_text():
            text.set_color("#000000")
        elif "Bakerloo" in text.get_text():
            text.set_color("#B36305")
        elif "Central" in text.get_text():
            text.set_color("#E32017")
        elif "Victoria" in text.get_text():
            text.set_color("#0098D4")

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
    
def analyse_network(G):
    distances = np.array([
        float(data["distance"])
        for _, _, data in G.edges(data=True)
    ])
    total_length = np.sum(distances)
    average_distance = np.mean(distances)
    standard_deviation = np.std(distances)
    print("=" * 45)
    print("TASK 3 RESULTS")
    print(f"Total length of transport network : {total_length:10.2f} m")
    print(f"Average distance between stations : {average_distance:10.2f} m")
    print(f"Standard deviation                : {standard_deviation:10.2f} m")

def main():
    file_name = "Map London2.csv"
    dataframe = load_data(file_name)
    if dataframe is None:
        return
    validate_data(dataframe)
    graph = build_graph(dataframe)
    print("\n========== Adjacency List ==========")
    graph.display_graph()
    G = convert_to_networkx(graph)
    draw_graph(G)
    analyse_network(G)

if __name__ == "__main__":
    main()