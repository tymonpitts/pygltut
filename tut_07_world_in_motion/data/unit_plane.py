from OpenGL import GL

VERTICES = [
        0.5, 0, -0.5, 
        0.5, 0, 0.5, 
        -0.5, 0, 0.5, 
        -0.5, 0, -0.5, 
        ]
DRAW_METHOD = GL.GL_TRIANGLES
INDICES = [
        0, 1, 2, 
        0, 2, 1, 
        2, 3, 0, 
        2, 0, 3, 
        ]

def create_mesh():
    from gltut_framework import Mesh
    return Mesh(VERTICES, INDICES, DRAW_METHOD)
