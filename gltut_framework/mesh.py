from OpenGL import GL
class Mesh(object):
    def __init__(self, vertices, indices, draw_method):
        from . import SHORT_SIZE, FLOAT_SIZE
        self.draw_method = draw_method
        self.indices = indices

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        vertexBufferObject = GL.glGenBuffers(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertexBufferObject)
        array_type = (GL.GLfloat*len(vertices))
        GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(vertices)*FLOAT_SIZE,
                array_type(*vertices),
                GL.GL_STATIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        indexBufferObject = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
        array_type = (GL.GLushort*len(self.indices))
        GL.glBufferData(
                GL.GL_ELEMENT_ARRAY_BUFFER,
                len(self.indices)*SHORT_SIZE,
                array_type(*self.indices),
                GL.GL_STATIC_DRAW)

        GL.glBindVertexArray(0)

    def render(self):
        GL.glBindVertexArray(self.vao)
        GL.glDrawElements(self.draw_method, len(self.indices), GL.GL_UNSIGNED_SHORT, None)
        GL.glBindVertexArray(0)

