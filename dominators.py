#! /bin/python3
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def main():
    nodes_num = 5
    reverse = 0

    nodes = ['Entry']
    for i in range(1, nodes_num + 1):
        nodes.append(f'B{i}')
    nodes.append('Exit')

    edges = [('Entry', 'B1'), ('B1', 'B2'), ('B2', 'B3'), ('B2', 'B4'), ('B4', 'B5'), ('B5', 'B2'), ('B3', 'B5'), ('B5', 'Exit')]

    gr = nx.DiGraph()
    gr.add_nodes_from(nodes)
    gr.add_edges_from(edges)

    if reverse:
        gr = gr.reverse()
        nodes.reverse()

    dominators = find_dom(gr, nodes)
    print()
    
    imm_dom = find_imm_dom(gr, nodes, dominators)
    print()

    plot_dom_tree(nodes, imm_dom)
    print()

    dom_frs = find_df(gr, nodes, imm_dom)
    print("Finished")
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

    for node in nodes[1:]:
        idom = None
        if len(dominators[node]) > 2:
            shortest = 10000000
            for dom in dominators[node]:
                if dom != node:
                    path = nx.shortest_path(gr, dom, node)
                    if len(path) < shortest:
                        shortest = len(path)
                        idom = dom
        print(f"Imm_dom({node}) = {idom}")
        imm_dom[node] = idom

    print(f'soulless networkx library solution: {nx.immediate_dominators(gr, nodes[0])}')
    nx.draw(gr, with_labels=True)
    plt.show()
    return imm_dom

def plot_dom_tree(nodes, imm_dom):
    print("Plotting dominators tree...")

    dom_gr = nx.DiGraph()
    dom_gr.add_nodes_from(nodes[1:])

    dom_edges = []
    for node in nodes[1:]:
        if imm_dom[node]:
            dom_edges.append((imm_dom[node], node))

    print(f"Dominator tree edges: {dom_edges}")
    dom_gr.add_edges_from(dom_edges)

    nx.draw(dom_gr, with_labels=True)
    plt.show()

def find_df(gr, nodes, imm_dom):
    print("Finding dominance frontiers...")

    dom_frs = {nodes[0] : None}

    for node in nodes[1:]:
        dom_frs[node] = None

    for n in nodes[1:]:
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
                    if dom_frs[r] == None:
                        dom_frs[r] = [n]
                    else:
                        dom_frs[r] = np.append(dom_frs[r], n)
                    print(f"\t\tdominance_frontiers[{r}] = {dom_frs[r]}")
                    r = imm_dom[r]
                print(f"\t\t{r} = imm_dom[{n}]. Moving on...")
    print("my DF solution:              ", dom_frs)
    print("networkx library DF solution:", nx.dominance_frontiers(gr, nodes[0]))

    return dom_frs

if __name__ == "__main__":
    main()
