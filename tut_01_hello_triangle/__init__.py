import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial

VERTEX_SHADER = """
#version 330
layout(location = 0) in vec4 position;
void main()
{
    gl_Position = position;
}
"""

FRAGMENT_SHADER = """
#version 330
out vec4 outputColor;
void main()
{
    outputColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
}
"""


class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None
        self.vertexPositions = [
                0.75,  0.75,  0.0,  1.0,
                0.75, -0.75,  0.0,  1.0,
                -0.75, -0.75,  0.0,  1.0]
        self.positionBufferObject = None
        self.vao = None

        self.vert_components = 4
        self.size_float = 4

    def initializeProgram(self):
        shaderList = []

        shaderList.append(compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        self.theProgram = compileProgram(*shaderList)

    def initializeVertexBuffer(self):
        self.positionBufferObject = GL.glGenBuffers(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self.positionBufferObject)
        array_type = (GL.GLfloat*len(self.vertexPositions))
        GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(self.vertexPositions)*self.size_float,
                array_type(*self.vertexPositions),
                GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)

    def init(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.initializeProgram()
        self.initializeVertexBuffer()

    def display(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glUseProgram(self.theProgram)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.positionBufferObject)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, self.vert_components, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.vertexPositions)//self.vert_components)

        GL.glDisableVertexAttribArray(0)
        GL.glUseProgram(0)

        glfw.SwapBuffers()

    def reshape(self, w, h):
        GL.glViewport(0, 0, w, h);

    def keyboard(self, key, press):
        if key == glfw.KEY_ESC:
            glfw.Terminate()
            return





# import glfw
# from OpenGL.GL import *
# from OpenGL.raw.GL.ARB.vertex_array_object import \
#         glGenVertexArrays, glBindVertexArray
# import numpy
# from gltut_framework import AbstractTutorial
# from OpenGL.GL import shaders
# from OpenGL.arrays import vbo
# from OpenGL.arrays.arraydatatype import ArrayDatatype
# # print OpenGL.GL.__file__

# class Tutorial(AbstractTutorial):
#     VERTEX_SHADER = """
# #version 330
# layout(location = 0) in vec4 position;
# void main()
# {
#     gl_Position = position;
# }
# """
#     FRAGMENT_SHADER = """
# #version 330
# out vec4 outputColor;
# void main()
# {
#     outputColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
# }
# """
#     def __init__(self, *args, **kwargs):
#         super(Tutorial, self).__init__(*args, **kwargs)
#         self.theProgram = None
#         self.vertexPositions = numpy.array([
#                 [0.75, 0.75, 0.0, 1.0],
#                 [0.75, -0.75, 0.0, 1.0],
#                 [-0.75, -0.75, 0.0, 1.0]], dtype='f')
#         # self.positionBufferObject = None
#         self.positionBufferObject = GLuint(0)
#         self.vao = GLuint(0)

#     def initializeProgram(self):
#         shaderList = []

#         shaderList.append(shaders.compileShader(self.VERTEX_SHADER, GL_VERTEX_SHADER))
#         shaderList.append(shaders.compileShader(self.FRAGMENT_SHADER, GL_FRAGMENT_SHADER))

#         self.theProgram = shaders.compileProgram(*shaderList)

#     def initializeVertexBuffer(self):
#         glGenBuffers(1, self.positionBufferObject)

#         glBindBuffer(GL_ARRAY_BUFFER, self.positionBufferObject)
#         glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self.vertexPositions), self.vertexPositions, GL_STATIC_DRAW);
#         glBindBuffer(GL_ARRAY_BUFFER, 0);
#         # self.positionBufferObject = vbo.VBO(self.vertexPositions)

#     def init(self):
#         glGenVertexArrays(1, self.vao)
#         glBindVertexArray(self.vao)

#         self.initializeProgram()
#         self.initializeVertexBuffer()

#         # glGenVertexArrays(1, self.vao)
#         # glBindVertexArray(self.vao)

#     def display(self):
#         glClearColor(0.0, 0.0, 0.0, 0.0)
#         glClear(GL_COLOR_BUFFER_BIT)

#         glUseProgram(self.theProgram)

#         # glBindBuffer(GL_ARRAY_BUFFER, self.positionBufferObject)
#         self.positionBufferObject.bind()

#         glEnableVertexAttribArray(0)
#         glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, 0)

#         glDrawArrays(GL_TRIANGLES, 0, 3)

#         glDisableVertexAttribArray(0)
#         glUseProgram(0)

#         glfw.SwapBuffers()

#     def reshape(self, w, h):
#         glViewport(0, 0, w, h);

#     def keyboard(self, key, press):
#         if key == glfw.KEY_ESC:
#             glfw.Terminate()
#             return

