import numpy as np
import igraph as ig
from tqdm import tqdm
import rdimacs as rd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def make_graph_positions_optimized(filename, max_nodes=10000, max_edges=50000):
    num_vars, clauses = rd.read_dimacs(filename)
    print(f"Variables: {num_vars}, Clauses: {len(clauses)}")
    
    G = generate_interaction_graph_optimized(num_vars, clauses, max_nodes, max_edges)
   
    print("Calculating layout...")
    pos = G.layout_fruchterman_reingold(dim=3, weights='weight', niter=50)
    pos = np.array(pos)
   
    print("Preparing edge data...")
    edges = np.array(G.get_edgelist())
   
    return pos, edges, min(num_vars, max_nodes // 2)

def generate_interaction_graph_optimized(num_vars, clauses, max_nodes, max_edges):
    edge_dict = {}
    node_set = set()
    for clause in tqdm(clauses, desc="Generating graph"):
        for i, a in enumerate(clause):
            for b in clause[i+1:]:
                node1, node2 = literal_to_id(a, num_vars, max_nodes), literal_to_id(b, num_vars, max_nodes)
                if node1 != node2:
                    edge = tuple(sorted([node1, node2]))
                    edge_dict[edge] = edge_dict.get(edge, 0) + 1
                    node_set.add(node1)
                    node_set.add(node2)
                if len(edge_dict) >= max_edges:
                    break
            if len(edge_dict) >= max_edges:
                break
        if len(edge_dict) >= max_edges:
            break

    G = ig.Graph(n=len(node_set), edges=list(edge_dict.keys()), edge_attrs={'weight': list(edge_dict.values())})
    return G

def literal_to_id(literal, num_vars, max_nodes):
    """Maps a literal to a unique non-negative node ID within the max_nodes limit."""
    if literal > 0:
        return (literal - 1) % (max_nodes // 2)
    else:
        return (max_nodes // 2 + abs(literal) - 1) % max_nodes

def plot_graph_from_positions(pos, edges, num_vars, max_edges_to_plot=1000000):
    Xn, Yn, Zn = pos.T
   
    edge_x = []
    edge_y = []
    edge_z = []
   
    for i, edge in enumerate(edges[:max_edges_to_plot]):
        edge_x.extend([pos[edge[0], 0], pos[edge[1], 0], None])
        edge_y.extend([pos[edge[0], 1], pos[edge[1], 1], None])
        edge_z.extend([pos[edge[0], 2], pos[edge[1], 2], None])
   
    node_colors = ['blue' if i < num_vars else 'red' for i in range(len(Xn))]
   
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'scene'}]])
   
    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='lightgrey', width=1), hoverinfo='none'), row=1, col=1)
    fig.add_trace(go.Scatter3d(x=Xn, y=Yn, z=Zn, mode='markers', marker=dict(size=4, color=node_colors), hoverinfo='text', text=[f'Var {i+1}' if i < num_vars else f'Not Var {i-num_vars+1}' for i in range(len(Xn))]), row=1, col=1)
   
    fig.update_layout(
        title="3D Visualization of CNF Variables and Clauses (Simplified)",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
        width=800, height=800,
        margin=dict(r=20, l=10, b=10, t=40)
    )
   
    fig.show()