import os
import math
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial
from .data.vertices_ortho import VERTICES

#Load shaders from files.
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, "data","OrthoWithOffset.vert"),'r') as myfile:
    VERTEX_SHADER = myfile.read()
with open(os.path.join(dirname, "data","StandardColors.frag"),'r') as myfile:
    FRAGMENT_SHADER = myfile.read()

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None
        self.offsetUniform = None
        self.vertexData = VERTICES

        self.vertexBufferObject = None
        self.vao = None

        self.num_vertex_components = 4
        self.float_size = 4

    def initializeProgram(self):
        shaderList = []

        shaderList.append(compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        self.theProgram = compileProgram(*shaderList)

        self.offsetUniform = GL.glGetUniformLocation(self.theProgram, "offset")

    def initializeVertexBuffer(self):
        self.vertexBufferObject = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self.vertexBufferObject)
        array_type = (GL.GLfloat*len(self.vertexData))
        GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(self.vertexData)*self.float_size,
                array_type(*self.vertexData),
                GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)

    def init(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.initializeProgram()
        self.initializeVertexBuffer()

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CW)

    def display(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glUseProgram(self.theProgram)

        GL.glUniform2f(self.offsetUniform, 0.5, 0.25)

        colorData = GL.GLvoidp((len(self.vertexData) * self.float_size) / 2)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertexBufferObject)
        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(0, self.num_vertex_components, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glVertexAttribPointer(1, self.num_vertex_components, GL.GL_FLOAT, GL.GL_FALSE, 0, colorData)

        num_verts = len(self.vertexData)/self.num_vertex_components/2
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, num_verts)

        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)
        GL.glUseProgram(0)

        glfw.SwapBuffers()

    def reshape(self, w, h):
        GL.glViewport(0, 0, w, h);

    def keyboard(self, key, press):
        if key == glfw.KEY_ESC:
            glfw.Terminate()
            return

