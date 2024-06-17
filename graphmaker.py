import numpy as np
import networkx as nx
import rdimacs as rd
import plotly.graph_objs as go


def make_graph_positions(filename='4_queens.txt'):

    num_vars, clauses = rd.read_dimacs(filename)

    # Empty graph
    G = nx.Graph()

    # Nodes
    for i in range(1, num_vars + 1):
        G.add_node(i)

    # Edges based on clauses
    for clause in clauses:
        for i in range(len(clause)):
            for j in range(i + 1, len(clause)):
                G.add_edge(abs(clause[i]), abs(clause[j]))

    # Get node positions in 3D space using Fruchterman-Reingold layout as in the original DPVis
    pos = nx.fruchterman_reingold_layout(G, dim=3)  
    # Uncomment this to try my favorite type of layout pos = nx.kamada_kawai_layout(G, dim=3)

    # Extract positions for Plotly
    Xn = [pos[k][0] for k in G.nodes()]
    Yn = [pos[k][1] for k in G.nodes()]
    Zn = [pos[k][2] for k in G.nodes()]
    labels = [str(k) for k in G.nodes()]

    # Assign colors based on the node labels (mapping to numerical values)
    color_mapping = {label: idx for idx, label in enumerate(labels)}
    node_colors = [color_mapping[label] for label in labels]

    Xe = []
    Ye = []
    Ze = []
    for e in G.edges():
        Xe += [pos[e[0]][0], pos[e[1]][0], None]
        Ye += [pos[e[0]][1], pos[e[1]][1], None]
        Ze += [pos[e[0]][2], pos[e[1]][2], None]

    return Xn, Yn, Zn, labels, color_mapping, node_colors, Xe, Ye, Ze

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
