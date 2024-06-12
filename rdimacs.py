import networkx as nx
import matplotlib.pyplot as plt

def read_dimacs(filename):
    clauses = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('p'):
                _, _, variables, _ = line.split()
                num_vars = int(variables)
            elif line.startswith('c') or line.startswith('%') or line.startswith('0'):
                continue
            else:
                clause = list(map(int, line.strip().split()))
                clauses.append(clause)
    return num_vars, clauses

def generate_interaction_graph(num_vars, clauses):
    G = nx.Graph()
    for clause in clauses:
        for i in range(len(clause)):
            for j in range(i + 1):
                if i != j:
                    G.add_edge(abs(clause[i]), abs(clause[j]))
    return G

def plot_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edges(G, pos)
