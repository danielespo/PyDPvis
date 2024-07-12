import numpy as np
import igraph as ig
from tqdm import tqdm
import rdimacs as rd 
import plotly.graph_objs as go

# Updated to igraph because it is straight up faster.

def make_graph_positions_optimized(filename, max_edges=100000): #disable max_edges if you have a beefy machine
    num_vars, clauses = rd.read_dimacs(filename)
    G = generate_interaction_graph_optimized(num_vars, clauses)
    
    print("Calculating layout...")
    pos = G.layout_drl(dim=3)
    pos = np.array(pos)
    
    Xn, Yn, Zn = pos.T
    labels = [str(k+1) for k in range(2 * num_vars)]
    
    color_mapping = {label: idx for idx, label in enumerate(labels)}
    node_colors = np.arange(2 * num_vars)
    
    print("Preparing edge data...")
    edges = np.array(G.get_edgelist())
    
    # Downsample edges if there are too many
    if len(edges) > max_edges:
        downsample_rate = len(edges) // max_edges
        edges = edges[::downsample_rate]
    
    Xe = np.empty((len(edges) * 3,))
    Ye = np.empty((len(edges) * 3,))
    Ze = np.empty((len(edges) * 3,))
    
    Xe[::3], Xe[1::3], Xe[2::3] = pos[edges[:, 0], 0], pos[edges[:, 1], 0], None
    Ye[::3], Ye[1::3], Ye[2::3] = pos[edges[:, 0], 1], pos[edges[:, 1], 1], None
    Ze[::3], Ze[1::3], Ze[2::3] = pos[edges[:, 0], 2], pos[edges[:, 1], 2], None
    
    return Xn, Yn, Zn, labels, color_mapping, node_colors, Xe, Ye, Ze

def generate_interaction_graph_optimized(num_vars, clauses):
    edges = set()
    for clause in tqdm(clauses, desc="Generating graph"):
        clause_edges = set((literal_to_id(a, num_vars), literal_to_id(b, num_vars))
                           for i, a in enumerate(clause)
                           for b in clause[i+1:])
        edges.update(clause_edges)
    
    G = ig.Graph(n=2*num_vars, edges=list(edges))
    return G

def literal_to_id(literal, num_vars):
    """Maps a literal to a unique node ID."""
    if literal > 0:
        return literal - 1  # Positive literals: 0 to num_vars-1
    else:
        return num_vars - literal - 1  # Negative literals: num_vars to 2*num_vars-1

def plot_graph_from_positions(Xn, Yn, Zn, labels, color_mapping, node_colors, Xe, Ye, Ze):
    trace1 = go.Scatter3d(
        x=Xe,
        y=Ye,
        z=Ze,
        mode='lines',
        line=dict(color='rgb(125,125,125)', width=1),
        hoverinfo='none'
    )

    trace2 = go.Scatter3d(
        x=Xn,
        y=Yn,
        z=Zn,
        mode='markers',
        name='variables',
        marker=dict(symbol='circle', size=6, color=node_colors, colorscale='Viridis', line=dict(color='rgb(50,50,50)', width=0.5)),
        text=labels,
        hoverinfo='text'
    )

    axis = dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')

    layout = go.Layout(
        title="3D Visualization of CNF Variables and Clauses",
        width=1000,
        height=1000,
        showlegend=False,
        scene=dict(xaxis=dict(axis), yaxis=dict(axis), zaxis=dict(axis)),
        margin=dict(t=100),
        hovermode='closest',
        annotations=[
            dict(
                showarrow=False,
                text="Data source: <a href='your_data_source_url'>CNF File</a>",
                xref='paper',
                yref='paper',
                x=0,
                y=0.1,
                xanchor='left',
                yanchor='bottom',
                font=dict(size=14)
            )
        ]
    )

    fig = go.Figure(data=[trace1, trace2], layout=layout)
    fig.show()
