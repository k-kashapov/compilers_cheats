#! /bin/python3
import importlib.util
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import sys

USE_GRAPHVIZ = True

def main():
    # Amount of nodes excluding the Entry and Exit nodes
    NODES_NUM = 10

    # Reverse the graph before all steps
    REVERSE = False

    if len(sys.argv) <= 1 or 'help' in sys.argv[1].lower().strip():
        print_help_and_exit() 

    gr = nx.read_adjlist(sys.argv[1], create_using=nx.DiGraph())
    nodes = list(gr.nodes)
    
    if REVERSE:
        gr = gr.reverse()
        nodes.reverse()

    print("\nFinding dominators...")
    dominators = find_dom(gr, nodes)

    print("\nPlotting your graph...")
    plot_graph(gr, 'neato')

    print("\nFinding immediate dominators...")
    imm_dom = find_imm_dom(gr, nodes, dominators)

    print("\nPlotting dominator tree...")
    plot_dom_tree(nodes, imm_dom)

    print("\nFinding dominance frontiers...")
    dom_frs = find_df(gr, nodes, imm_dom)
    print("\nFinished")
    return

def print_help_and_exit():
    print(
        "Provide path to file, containing graph as first argument.",
        "File must contain graph's adjastency list and it's structure must be:",
        "`a b c # source target target`",
        "where `#` is comment separator.",
        "You can check file's example in examples/cfg_example.adj",
        "P.S. `entry` and `exit nodes should be named exactly like in the example`",
        sep='\n'
    )
    
    exit(0)

def plot_graph(graph, prog):
    if USE_GRAPHVIZ:
        pos = nx.nx_agraph.graphviz_layout(graph, prog=prog)
        nx.draw(graph, pos, with_labels=True)
    else:
        print("WARNING: USE_GRAPHVIZ is False - pygraphviz not found. Not fatal, but graphs are ugly.")
        nx.draw(graph, with_labels=True)
    plt.show()
    return

def find_dom(gr, nodes):
    dominators = {nodes[0] : [nodes[0]]}
    for node in nodes[1:]:
        dominators[node] = nodes

    for node in nodes[1:]:
        print(f"Processing {node}:")
        preds = list(gr.predecessors(node))
        print(f"\tNode predecessors = {preds}")
        adding = np.copy(nodes)

        for pred in preds:
            print(f"\tPredecessor {pred}:")
            print(f"\t\tIntersecting {adding} and {dominators[pred]}")
            adding = np.intersect1d(adding, dominators[pred])

        doms = np.append(node, adding)

        dominators[node] = doms
        print(f"\tdominators[{node}] = {node} U intersection = {dominators[node]}")
    return dominators

def find_imm_dom(gr, nodes, dominators):
    imm_dom = {nodes[0] : None}
    for node in nodes:
        idom = None
        if len(dominators[node]) > 2:
            shortest = 10000000
            for dom in dominators[node]:
                if dom != node:
                    path = nx.shortest_path(gr, dom, node)
                    if len(path) < shortest:
                        shortest = len(path)
                        idom = dom
        print(f"\tImm_dom({node}) = {idom}")
        imm_dom[node] = idom

    print(f'Soulless networkx library solution:')
    nx_res = nx.immediate_dominators(gr, nodes[0])
    for immd in nx_res:
        print(f"\timm_dom[{immd}] = {nx_res[immd]}")

    return imm_dom

def plot_dom_tree(nodes, imm_dom):
    dom_gr = nx.DiGraph()
    dom_gr.add_nodes_from(nodes[1:])

    dom_edges = []
    for node in nodes[1:]:
        if imm_dom[node]:
            dom_edges.append((imm_dom[node], node))

    print(f"Dominator tree edges: {dom_edges}")
    dom_gr.add_edges_from(dom_edges)

    plot_graph(dom_gr, 'dot')
    return

def find_df(gr, nodes, imm_dom):
    dom_frs = {nodes[0] : None}

    for node in nodes:
        dom_frs[node] = None

    for n in nodes:
        print(f"Processing node {node}:")
        preds = list(gr.predecessors(n))
        print(f"\tpreds({n}) = {preds}")
        if (len(preds) > 1):
            print("\t|Preds| > 1")
            for p in preds:
                print(f"\tProcessing pred {p}:")
                r = p
                while r != imm_dom[n]:
                    print(f"\t\tr = {r}")
                    if type(dom_frs[r]) is type(None):
                        dom_frs[r] = [n]
                    else:
                        dom_frs[r] = np.unique(np.append(dom_frs[r], n))
                    print(f"\t\tdominance_frontiers[{r}] = {dom_frs[r]}")
                    r = imm_dom[r]
                print(f"\t\t{r} = imm_dom[{n}]. Moving on...")

    dom_frs[nodes[0]] = None
    print("my DF solution:")
    for dom_fr in dom_frs:
        print(f"\tdom_frs[{dom_fr}] = {dom_frs[dom_fr]}")

    print("networkx library DF solution:")
    nx_res = nx.dominance_frontiers(gr, nodes[0])
    for dom_fr in nx_res:
        print(f"\tdom_frs[{dom_fr}] = {nx_res[dom_fr]}")

    return dom_frs

if __name__ == "__main__":
    if (spec := importlib.util.find_spec("pygraphviz")) is None:
        print("Cannot find pygraphviz!!!!! Defaulting to ugly graph plotting...")
        USE_GRAPHVIZ = False
    main()
