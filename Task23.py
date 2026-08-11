import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.widgets import Button


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

LINE_COLOURS = {
    "Piccadilly": "#003688",
    "Northern": "#000000",
    "Bakerloo": "#B36305",
    "Central": "#E32017",
    "Victoria": "#006600"
}

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
        "Distance"
        
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
            LINE_COLOURS.get(row["Line"], "#666666")
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
            line = next(iter(lines), None)
            node_colours.append(LINE_COLOURS.get(line, "white"))
      
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
    for u, v, data in G.edges(data=True):
        x1, y1 = positions[u]
        x2, y2 = positions[v]

        x_mid = (x1 + x2) / 2
        y_mid = (y1 + y2) / 2

        ax.text(
            x_mid,
            y_mid,
            f"{data['distance']} km",
            fontsize=8,
            rotation=0,
            rotation_mode="anchor",
            ha="center",
            va="center",
            color="black",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                pad=0.2
            ),
            zorder=6
        )
    # Legend
    legend = [
        Line2D([0], [0], color="#003688", lw=4, label="Piccadilly"),
        Line2D([0], [0], color="#000000", lw=4, label="Northern"),
        Line2D([0], [0], color="#B36305", lw=4, label="Bakerloo"),
        Line2D([0], [0], color="#E32017", lw=4, label="Central"),
        Line2D([0], [0], color="#006600", lw=4, label="Victoria"),
        Line2D([0], [0],marker='o',linestyle='None',markerfacecolor="#888888",markersize=8,label="Interchange station")
    ]

    leg = plt.legend(
        handles=legend,
        title="Key",
        loc="lower right",
        frameon=True,
        fancybox=False,
        edgecolor="black",
        facecolor="white",
        framealpha=1,
        bbox_to_anchor=(0.97, 0.04),
        borderpad=1.0,
        labelspacing=0.8,
        handlelength=2.5,
        handletextpad=0.8,
        fontsize=9,
        title_fontsize=10
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
            text.set_color("#006600")

    ax.set_title(
        "London Underground Network Map",
        fontsize=16,
        fontweight="bold",
        pad=20,
        y=0.92
    )
    xmin, xmax, ymin, ymax = auto_adjust_view(positions)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")

    # Fit the map first, then reserve a strip at the bottom of this same
    # window for the Task 3 buttons, so a second window is not needed.
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.16)

    return fig, ax
    
def analyse_network(G, fig=None):
    """
    Task 3: Extract network statistics from the graph
    (total length, average distance, standard deviation) and let the
    user view a chart for each statistic by clicking a button.
    """
    edges = list(G.edges(data=True))
    distances = np.array([data["distance"] for _, _, data in edges], dtype=float)

    total_length = float(np.sum(distances))
    average_distance = float(np.mean(distances))
    std_distance = float(np.std(distances))

    print("\n========== Task 3: Network Statistics ==========")
    print(f"Number of station connections          : {len(distances)}")
    print(f"Total length of the transport network  : {total_length:.2f} km")
    print(f"Average distance between stations      : {average_distance:.2f} km")
    print(f"Standard deviation of distances         : {std_distance:.2f} km")

    # Group distances by line (used by the "Total length" chart)
    line_totals = {}
    for _, _, data in edges:
        line = data["line"]
        line_totals[line] = line_totals.get(line, 0.0) + data["distance"]

    LARGE_TITLE = 17
    LARGE_LABEL = 14
    LARGE_TICK = 12
    LARGE_LEGEND = 12

    # ---------------------------------------------------------------
    # Chart callbacks
    # ---------------------------------------------------------------
    def show_total_length_chart(event):
        """Bar chart: total distance contributed by each line."""
        fig, ax = plt.subplots(figsize=(11, 7))

        sorted_lines = sorted(line_totals.items(), key=lambda item: item[1], reverse=True)
        lines = [item[0] for item in sorted_lines]
        totals = [item[1] for item in sorted_lines]
        colours = [LINE_COLOURS.get(line, "#666666") for line in lines]
        percentages = [(value / total_length) * 100 for value in totals]

        bars = ax.bar(lines, totals, color=colours, edgecolor="black", linewidth=0.8)
        for bar, value, pct in zip(bars, totals, percentages):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.2f} km\n({pct:.0f}%)",
                ha="center",
                va="bottom",
                fontsize=LARGE_TICK
            )

        plt.xticks(rotation=15, ha="right", fontsize=LARGE_TICK)
        for tick_label, colour in zip(ax.get_xticklabels(), colours):
            tick_label.set_color(colour)
            tick_label.set_fontweight("bold")

        ax.set_title(f"Total Network Length: {total_length:.2f} km",
                     fontweight="bold", fontsize=LARGE_TITLE)
        ax.set_xlabel("Line", fontsize=LARGE_LABEL)
        ax.set_ylabel("Distance (km)", fontsize=LARGE_LABEL)
        ax.tick_params(axis="y", labelsize=LARGE_TICK)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)
        ax.margins(y=0.18)

        plt.tight_layout()
        plt.show()

    def show_average_distance_chart(event):
        """Line chart: distance of every connection, sorted, against the average."""
        fig, ax = plt.subplots(figsize=(12, 7))

        sorted_edges = sorted(edges, key=lambda edge: edge[2]["distance"])
        sorted_distances = [edge[2]["distance"] for edge in sorted_edges]
        x_pos = np.arange(1, len(sorted_distances) + 1)

        ax.plot(x_pos, sorted_distances, color="#2A6EBB", marker="o",
                markersize=7, linewidth=2.5, label="Distance per connection")
        ax.axhline(average_distance, color="red", linestyle="--", linewidth=2.5,
                   label=f"Average = {average_distance:.2f} km")

        above = [d >= average_distance for d in sorted_distances]
        below = [d < average_distance for d in sorted_distances]
        ax.fill_between(x_pos, sorted_distances, average_distance,
                         where=above, color="red", alpha=0.10, interpolate=True)
        ax.fill_between(x_pos, sorted_distances, average_distance,
                         where=below, color="#2A6EBB", alpha=0.10, interpolate=True)

        ax.set_title(f"Distance per Station Connection (Average = {average_distance:.2f} km)",
                     fontweight="bold", fontsize=LARGE_TITLE)
        ax.set_xlabel("Connection, sorted shortest to longest", fontsize=LARGE_LABEL)
        ax.set_ylabel("Distance (km)", fontsize=LARGE_LABEL)
        ax.tick_params(axis="both", labelsize=LARGE_TICK)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)
        ax.legend(fontsize=LARGE_LEGEND, loc="upper left")

        summary_text = (
            f"Connections: {len(distances)}\n"
            f"Shortest: {distances.min():.2f} km\n"
            f"Longest: {distances.max():.2f} km"
        )
        ax.text(
            0.98, 0.04, summary_text, transform=ax.transAxes,
            fontsize=LARGE_TICK, va="bottom", ha="right",
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.9)
        )

        plt.tight_layout()
        plt.show()

    def show_std_dev_chart(event):
        """Bar chart: distance of every connection with the +/-1 std deviation band."""
        sorted_edges = sorted(edges, key=lambda edge: edge[2]["distance"])
        sorted_distances = [edge[2]["distance"] for edge in sorted_edges]
        sorted_labels = [f"{u} - {v}" for u, v, _ in sorted_edges]
        sorted_colours = [LINE_COLOURS.get(edge[2]["line"], "#666666") for edge in sorted_edges]

        fig, ax = plt.subplots(figsize=(14, 8))
        x_pos = np.arange(len(sorted_distances))

        ax.axhspan(
            average_distance - std_distance,
            average_distance + std_distance,
            color="red", alpha=0.12,
            label=f"\u00b11 STD band ({std_distance:.2f} km)"
        )
        ax.bar(x_pos, sorted_distances, color=sorted_colours, edgecolor="black", linewidth=0.6)
        ax.axhline(average_distance, color="blue", linestyle="--", linewidth=2,
                   label=f"Mean = {average_distance:.2f} km")

        ax.set_title(
            f"Distances Between Connected Stations (Standard Deviation = {std_distance:.2f} km)",
            fontweight="bold", fontsize=LARGE_TITLE
        )
        ax.set_xlabel("Station connection", fontsize=LARGE_LABEL)
        ax.set_ylabel("Distance (km)", fontsize=LARGE_LABEL)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(sorted_labels, rotation=65, ha="right", fontsize=10)
        ax.tick_params(axis="y", labelsize=LARGE_TICK)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)

        present_lines = sorted({edge[2]["line"] for edge in edges})
        line_handles = [
            Line2D([0], [0], color=LINE_COLOURS.get(line, "#666666"), lw=6, label=line)
            for line in present_lines
        ]
        band_handles, _ = ax.get_legend_handles_labels()

        # Two separate legend boxes side by side, rather than one mixed
        # legend, so the reference lines and the line-colour key don't
        # interleave: reference lines (band + mean) on the left, the
        # Underground line colours on the right.
        reference_legend = ax.legend(
            handles=band_handles, loc="upper left", bbox_to_anchor=(0.0, 1.0),
            fontsize=11, frameon=True, title="Reference", title_fontsize=11
        )
        ax.add_artist(reference_legend)
        ax.legend(
            handles=line_handles, loc="upper left", bbox_to_anchor=(0.20, 1.0),
            fontsize=11, frameon=True, title="Line", title_fontsize=11
        )

        plt.tight_layout()
        plt.show()

    # ---------------------------------------------------------------
    # Buttons, placed in the same window as the network map
    # (in the strip reserved by draw_graph via subplots_adjust(bottom=...))
    # ---------------------------------------------------------------
    if fig is None:
        fig = plt.figure(figsize=(7, 2))
        fig.subplots_adjust(bottom=0.3)

    ax_total = fig.add_axes([0.06, 0.03, 0.27, 0.07])
    ax_avg = fig.add_axes([0.365, 0.03, 0.27, 0.07])
    ax_std = fig.add_axes([0.67, 0.03, 0.27, 0.07])

    btn_total = Button(ax_total, "Total length of the\ntransport network")
    btn_avg = Button(ax_avg, "The average distance\nbetween the stations")
    btn_std = Button(ax_std, "The standard deviation\nof the distances")

    btn_total.on_clicked(show_total_length_chart)
    btn_avg.on_clicked(show_average_distance_chart)
    btn_std.on_clicked(show_std_dev_chart)

    # Keep references alive for the duration of the window
    # (otherwise the buttons stop responding once this function returns)
    fig._task3_buttons = (btn_total, btn_avg, btn_std)

    return total_length, average_distance, std_distance


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
    fig, ax = draw_graph(G)
    analyse_network(G, fig)
    plt.show()

if __name__ == "__main__":
    main()