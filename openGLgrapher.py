import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import glfw
from ctypes import c_void_p

import igraph as ig
import plotly.graph_objs as go
from tqdm import tqdm
import mmap
import re

# Work in progress -- create an independent OpenGL window to render larger graphs in instead of depending on plotly

# Vertex shader
vertex_shader = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
out vec3 fragColor;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0f);
    fragColor = color;
}
"""

# Fragment shader
fragment_shader = """
#version 330 core
in vec3 fragColor;
out vec4 color;
void main()
{
    color = vec4(fragColor, 1.0f);
}
"""

def create_shader(shader_type, source):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(shader))
    return shader

def create_program(vertex_shader, fragment_shader):
    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(program))
    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)
    return program

class GraphRenderer:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        self.window = glfw.create_window(800, 600, "Graph Visualization", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        
        vertex_shader = create_shader(gl.GL_VERTEX_SHADER, vertex_shader)
        fragment_shader = create_shader(gl.GL_FRAGMENT_SHADER, fragment_shader)
        self.shader_program = create_program(vertex_shader, fragment_shader)
        
        self.setup_buffers()
    
    def setup_buffers(self):
        vertices = self.vertices.astype(np.float32)
        edges = self.edges.astype(np.uint32)
        
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        
        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        
        ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, edges.nbytes, edges, gl.GL_STATIC_DRAW)
        
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertices.itemsize, c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertices.itemsize, c_void_p(3 * vertices.itemsize))
        gl.glEnableVertexAttribArray(1)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
    
    def framebuffer_size_callback(self, window, width, height):
        gl.glViewport(0, 0, width, height)
    
    def render(self):
        while not glfw.window_should_close(self.window):
            self.process_input()
            
            gl.glClearColor(0.2, 0.3, 0.3, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            
            gl.glUseProgram(self.shader_program)
            gl.glBindVertexArray(self.vao)
            gl.glDrawElements(gl.GL_LINES, len(self.edges) * 2, gl.GL_UNSIGNED_INT, None)
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        
        glfw.terminate()
    
    def process_input(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

def read_dimacs_and_prepare_data(filename):
    # ... (Use the optimized read_dimacs_mmap function from the previous answer)

    num_vars, clauses = read_dimacs_mmap(filename)

    # ... (Generate the graph using generate_interaction_graph_optimized)

    G = generate_interaction_graph_optimized(num_vars, clauses)
    
    # Prepare vertex and edge data for rendering
    vertices = []
    edges = []
    for i, v in enumerate(G.vs):
        pos = v['position']
        color = [0.5, 0.5, 0.5]  # Default color
        vertices.extend(pos + color)
    
    for edge in G.es:
        edges.extend([edge.source, edge.target])
    
    return np.array(vertices), np.array(edges)

# Usage
filename = 'CoinsGrid_N90_C35.cnf'
vertices, edges = read_dimacs_and_prepare_data(filename)
renderer = GraphRenderer(vertices, edges)
renderer.render()