import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm

def read_dimacs(filename):
    clauses = []
    with open(filename, 'r') as file:
        for line in tqdm(file, "Parsing Dimacs File"):
            if line.startswith('p'):
                _, _, variables, _ = line.split()
                num_vars = int(variables)
            elif line.startswith('c') or line.startswith('%') or line.startswith('0'):
                continue
            else:
                clause = list(map(int, line.strip().split()))
                clauses.append(clause)
    return num_vars, clauses