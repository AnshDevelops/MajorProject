import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from graphviz import Digraph


def events_graph(data: dict) -> str:
    dot = Digraph(format="png")

    # Calculate dimensions based on content
    node_count = len(data["plots"])
    edge_count = len(data["subplots"])
    height = max(500, 100 * node_count)  # min 500px, 100px per node
    width = 800  # fixed width for readability

    dot.attr(
        rankdir="TB",
        bgcolor="#ffffff",
        fontname="Poppins",
        fontsize="12",
        fontcolor="#0f172a",
        ranksep="0.75",
        nodesep="0.5",
        size=f"{width / 72},{height / 72}!"  # Convert to inches
    )

    dot.node_attr.update(
        shape="box",
        style="filled,rounded,setlinewidth(2)",
        color="#a5f3fc",
        fillcolor="#ccfbf1",
        fontcolor="#0f172a",
        fontname="Poppins",
        height="0.5",
        width="2.5"
    )

    dot.edge_attr.update(
        color="#38bdf8",
        fontname="Poppins",
        fontsize="10",
        fontcolor="#0f172a",
        arrowsize="0.8",
        arrowhead="normal",
        penwidth="1.5",
        minlen="2"
    )

    for plot in sorted(data["plots"], key=lambda x: x["sequence"]):
        label = f"{plot['sequence']}. {plot['event']}"
        dot.node(plot["id"], label)

    for subplot in sorted(data["subplots"], key=lambda x: x["sequence"]):
        dot.edge(subplot["from"], subplot["to"],
                 label=f"{subplot['event']}")

    dot.graph_attr["concentrate"] = "true"

    tmp = Path(tempfile.mkdtemp())
    path = tmp / f"graph_{uuid.uuid4().hex}.png"
    dot.render(path.stem, directory=tmp, cleanup=True)

    return str(path)


def add_plot(state, event, sequence=None):
    """Add a new plot point to the story."""
    if not event:
        return events_graph(state)

    plot_id = f"p{len(state['plots']) + 1}"
    if sequence is None or sequence <= 0:
        sequence = len(state['plots']) + 1

    for plot in state['plots']:
        plot['time'] = 'middle'

    new_plot = {
        "id": plot_id,
        "event": event,
        "sequence": sequence,
        "time": "end"
    }

    state["plots"].append(new_plot)
    state["plots"].sort(key=lambda x: x["sequence"])

    if state["plots"]:
        state["plots"][0]["time"] = "start"
        state["plots"][-1]["time"] = "end"

    return events_graph(state)


def add_subplot(state, from_plot, to_plot, event, sequence=None):
    """Add a subplot connection between two plot points."""
    if not all([from_plot, to_plot, event]):
        return events_graph(state)

    if sequence is None or sequence <= 0:
        sequence = len(state['subplots']) + 1

    plot_ids = {p["id"] for p in state["plots"]}
    if from_plot not in plot_ids or to_plot not in plot_ids:
        return events_graph(state)

    new_subplot = {
        "from": from_plot,
        "to": to_plot,
        "type": "leads_to",
        "event": event,
        "sequence": sequence
    }

    state["subplots"].append(new_subplot)
    state["subplots"].sort(key=lambda x: x["sequence"])

    return events_graph(state)


def delete_plot(state, plot_id):
    """Delete a plot point and its connected subplots."""
    if not plot_id:
        return events_graph(state)

    state["plots"] = [p for p in state["plots"] if p["id"] != plot_id]
    state["subplots"] = [s for s in state["subplots"]
                         if s["from"] != plot_id and s["to"] != plot_id]

    for i, plot in enumerate(state["plots"], 1):
        plot["sequence"] = i
        plot["time"] = "middle"

    if state["plots"]:
        state["plots"][0]["time"] = "start"
        state["plots"][-1]["time"] = "end"

    for i, subplot in enumerate(state["subplots"], 1):
        subplot["sequence"] = i

    return events_graph(state)


def save(state):
    """Save the event graph state to a JSON file."""
    fp = Path(tempfile.gettempdir()) / f"story_{datetime.now().isoformat()}.json"
    fp.write_text(json.dumps(state, indent=2))
    return str(fp)


def load(path):
    """Load event graph state from a JSON file."""
    data = json.loads(Path(path).read_text())
    assert {"plots", "subplots"} <= data.keys()
    return data
