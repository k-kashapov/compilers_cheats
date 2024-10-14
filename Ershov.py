#! /usr/bin/python3

import importlib.util
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# DO NOT TOUCH:
ERSHOV = {}
OPS = {}

# TOUCH ALL YOU WANT:
USE_GRAPHVIZ = 1
EDGES = [('t4', 't1'), ('t1', 'a'), ('t1', 'b'), ('t4', 't3'), ('t3', 'e'), ('t3', 't2'), ('t2', 'c'), ('t2', 'd')]
ROOT_NODE = 't4'
INIT_BASE = 1 # "база" b >= 1

# Usage:
#   Set EDGES. 
#        WARNING: DO NOT NAME ANY TWO NODES WITH THE SAME NAME.
#        WARNING: MARK Rsp VALUES WITH 'Rsp' SUBSTRING IN THE NAME. E.G. 'd_Rsp'.
#   Set USE_GRAPHVIZ
#   Set ROOT_NODE
#   Set INIT_BASE
#   ./Ershov.py

def plot_graph(graph, prog):
    if USE_GRAPHVIZ:
        pos = nx.nx_agraph.graphviz_layout(graph, prog=prog)
        nx.draw(graph, pos, with_labels=True)
    else:
        print("WARNING: USE_GRAPHVIZ is False - pygraphviz not found. Not fatal, but graphs are ugly.")
        nx.draw(graph, with_labels=True)
    plt.show()
    return

def ershov_number(gr, node):
    children = list(gr[node])
    if len(children) == 0:
        # Leaf node
        if 'Rsp' in node:
            # It's stack pointer register
            ERSHOV[node] = 0
        else:
            ERSHOV[node] = 1
    elif len(children) == 1:
        # Single child
        ERSHOV[node] = ershov_number(gr, children[0])
    else:
        left, right = children[0], children[1]

        if ershov_number(gr, left) != ershov_number(gr, right):
            ERSHOV[node] = max(ERSHOV[left], ERSHOV[right])
        else:
            ERSHOV[node] = ERSHOV[left] + 1

    return ERSHOV[node]

def code_gen(gr, node, base):
    print("code gen for node", node, "with base =", base)
    ch = list(gr[node]) # children list

    if len(ch) == 0:
        OPS[node] = f"LD R{base}, {node}"
    elif len(ch) == 1:
        code_gen(gr, ch[0], base)
    else:
        l, r = ch[0], ch[1]
        nv, lv, rv = gr.nodes[node]['ersh'], gr.nodes[l]['ersh'], gr.nodes[r]['ersh']

        # print(f"l = {l}, r = {r}, lv = {lv}, rv = {rv}")
        if rv > lv:
            k = rv
            m = lv
            code_gen(gr, r, base)
            code_gen(gr, l, base)
            OPS[node] = f"OP R{base + k - 1}, R{base + m - 1}, R{base + k - 1}"
            print(node, ":", OPS[node])
        elif lv > rv:
            k = lv
            m = rv
            code_gen(gr, l, base)
            code_gen(gr, r, base)
            OPS[node] = f"OP R{base + k - 1}, R{base + k - 1}, R{base + m - 1}"
            print(node, ":", OPS[node])
        else:
            k = nv
            code_gen(gr, r, base + 1)
            code_gen(gr, l, base)
            OPS[node] = f"OP R{base + k - 1}, R{base + k - 2}, R{base + k - 1}"
            print(node, ":", OPS[node])

def main():
    gr = nx.DiGraph()
    gr.add_edges_from(EDGES)

    if not nx.is_tree(gr):
        print("ERROR: This is not a tree!")
        plot_graph(gr, 'dot')
        return -1

    print(f"Root node \"{ROOT_NODE}\" Ershov number =", ershov_number(gr, ROOT_NODE))
    
    for node in gr.nodes:
        gr.nodes[node]['ersh'] = ERSHOV[node]
        print(f"Node \"{node}\" Ershov number =", ERSHOV[node])

    plot_graph(gr, 'dot')

    code_gen(gr, ROOT_NODE, INIT_BASE)



if __name__ == "__main__":
    if (spec := importlib.util.find_spec("pygraphviz")) is None:
        print("Cannot find pygraphviz!!!!! Defaulting to ugly graph plotting...")
        USE_GRAPHVIZ = False
    main()
