#! /bin/python3
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

gr = nx.DiGraph()

nodes_num = 5

nodes = ['Entry']

for i in range(1, nodes_num + 1):
    nodes.append(f'B{i}')

nodes.append('Exit')

edges = [('Entry', 'B1'), ('B1', 'B2'), ('B2', 'B3'), ('B2', 'B4'), ('B4', 'B5'), ('B5', 'B2'), ('B3', 'B5'), ('B5', 'Exit')]

gr.add_nodes_from(nodes)
gr.add_edges_from(edges)

dominators = {'Entry' : ['Entry']}
for node in nodes[1:-1]:
    dominators[node] = nodes

print(dominators)

changed = True

while changed:
    changed = False
    print("Starting iteration...")
    for node in nodes[1:-1]:
        # print(f"Processing {node}:\n", end="")
        preds = gr.predecessors(node)
        adding = np.copy(nodes)
        
        for pred in preds:
            # print(f"\tcurr pred = {pr}")
            adding = np.intersect1d(adding, dominators[pred])

        doms = np.append(node, adding)

        if not np.array_equal(doms, dominators[node]):
            print("dominators changed")
            changed = True
        else:
            print(f"\tdominators[{node}] = {dominators[node]}")
        dominators[node] = doms

imm_dom = {"Entry" : None}

for node in nodes[1:-1]:
    dom = dominators[node][-2]
    if len(dominators[node]) < 3:
        dom = None
    print(f"Imm_dom({node}) = {dom}")
    imm_dom[node] = dom

print(f'soulless machine\'s solution: {nx.immediate_dominators(gr, nodes[0])}')
nx.draw(gr, with_labels=True)
plt.show()

print("Plotting dominators tree...")

dom_gr = nx.DiGraph()
dom_gr.add_nodes_from(nodes[1:-1])

dom_edges = []
for node in nodes[1:-1]:
    if imm_dom[node]:
        dom_edges.append((imm_dom[node], node))

print(dom_edges)
dom_gr.add_edges_from(dom_edges)

nx.draw(dom_gr, with_labels=True)
plt.show()

print("Finding dominance frontiers...")

dom_frs = {'Entry' : None}

for node in nodes[1:-1]:
    dom_frs[node] = None

for n in nodes[1:-1]:
    preds = list(gr.predecessors(n))
    print(f"preds({n}) = {preds}")
    if (len(preds) > 1):
        for p in preds:
            r = p
            while r != imm_dom[n]:
                if dom_frs[r] == None:
                    dom_frs[r] = [n]
                else:
                    dom_frs[r] = np.append(dom_frs[r], n)
                r = imm_dom[r]

print("my DF solution:       ", dom_frs)
print("machine's DF solution:", nx.dominance_frontiers(gr, 'Entry'))
