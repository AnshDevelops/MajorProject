import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from graphviz import Digraph


def relations_graph(data: dict) -> str:
    dot = Digraph(format="png")

    dot.attr(
        rankdir="LR",
        bgcolor="#ffffff",
        fontname="Poppins",
        fontsize="12",
        fontcolor="#0f172a"
    )

    dot.node_attr.update(
        shape="ellipse",
        style="filled,setlinewidth(2)",
        color="#a5f3fc",
        fillcolor="#ccfbf1",
        fontcolor="#0f172a",
        fontname="Poppins"
    )

    dot.edge_attr.update(
        color="#38bdf8",
        fontname="Poppins",
        fontsize="10",
        fontcolor="#0f172a",
        arrowsize="0.8",
        arrowhead="vee",
        penwidth="1.5"
    )

    for c in data["characters"]:
        dot.node(c)

    for r in data["relations"]:
        dot.edge(r["from"], r["to"], label=r["type"])

    tmp = Path(tempfile.mkdtemp())
    path = tmp / f"graph_{uuid.uuid4().hex}.png"
    dot.render(path.stem, directory=tmp, cleanup=True)
    return str(path)


def add_character(state, name):
    if name and name not in state["characters"]:
        state["characters"].append(name)
    return relations_graph(state)


def add_relation(state, frm, to, typ):
    if frm in state["characters"] and to in state["characters"]:
        state["relations"].append({"from": frm, "to": to, "type": typ or "relation"})
    return relations_graph(state)


def delete_character(state, name):
    if name in state["characters"]:
        state["characters"].remove(name)
        state["relations"] = [r for r in state["relations"]
                              if r["from"] != name and r["to"] != name]
    return relations_graph(state)


def save(state):
    fp = Path(tempfile.gettempdir()) / f"story_{datetime.now().isoformat()}.json"
    fp.write_text(json.dumps(state, indent=2))
    return str(fp)


def load(path):
    data = json.loads(Path(path).read_text())
    assert {"characters", "relations"} <= data.keys()
    return data
