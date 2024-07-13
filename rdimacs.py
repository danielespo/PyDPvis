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
                clause = [int(lit) for lit in line.strip().split() if int(lit) != 0]
                if clause:  # Only append non-empty clauses
                    clauses.append(clause)
    return num_vars, clauses