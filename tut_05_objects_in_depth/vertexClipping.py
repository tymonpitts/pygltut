import os
import math
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial
from .data.vertex_data import VERTEX_DATA, INDICES, NUMBER_OF_VERTICES

#Load shaders from files.
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, "data","Standard.vert"),'r') as myfile:
    VERTEX_SHADER = myfile.read()
with open(os.path.join(dirname, "data","Standard.frag"),'r') as myfile:
    FRAGMENT_SHADER = myfile.read()

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None

        self.offsetUniform = None
        self.perspectiveMatrixUnif = None
        
        self.perspectiveMatrix = None
        self.fFrustumScale = 1.0
        
        self.vertexData = VERTEX_DATA
        self.numberOfVertices = NUMBER_OF_VERTICES
        self.indexData = INDICES

        self.vertexBufferObject = None
        self.indexBufferObject = None
        self.vao = None

        self.num_vertex_components = 4
        self.float_size = 4
        self.short_size = 2

    def initializeProgram(self):
        shaderList = []

        shaderList.append(compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        self.theProgram = compileProgram(*shaderList)

        self.offsetUniform = GL.glGetUniformLocation(self.theProgram, "offset")

        self.perspectiveMatrixUnif = GL.glGetUniformLocation(self.theProgram, "perspectiveMatrix")

        fzNear = 1.0
        fzFar = 3.0

        self.perspectiveMatrix = [0.0 for i in range(16)]
        self.perspectiveMatrix[0] = self.fFrustumScale
        self.perspectiveMatrix[5] = self.fFrustumScale
        self.perspectiveMatrix[10] = (fzFar+fzNear)/(fzNear-fzFar)
        self.perspectiveMatrix[14] = (2*fzFar*fzNear)/(fzNear-fzFar)
        self.perspectiveMatrix[11] = -1.0

        GL.glUseProgram(self.theProgram)
        GL.glUniformMatrix4fv(self.perspectiveMatrixUnif,1,GL.GL_FALSE,self.perspectiveMatrix)
        GL.glUseProgram(0)

    def initializeVertexBuffer(self):
        self.vertexBufferObject = GL.glGenBuffers(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertexBufferObject)
        array_type = (GL.GLfloat*len(self.vertexData))
        GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(self.vertexData)*self.float_size,
                array_type(*self.vertexData),
                GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)

        self.indexBufferObject = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.indexBufferObject)
        array_type = (GL.GLushort*len(self.indexData))
        GL.glBufferData(
                GL.GL_ELEMENT_ARRAY_BUFFER,
                len(self.indexData)*self.short_size,
                array_type(*self.indexData),
                GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,0)

    def init(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.initializeProgram()
        self.initializeVertexBuffer()

        colorDataOffset = 3*self.float_size*self.numberOfVertices
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self.vertexBufferObject)
        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glVertexAttribPointer(1, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, GL.GLvoidp(colorDataOffset))
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,self.indexBufferObject)

        GL.glBindVertexArray(0)

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CW)

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glDepthRange(0.0, 1.0)

    def display(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClearDepth(1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glUseProgram(self.theProgram)

        GL.glBindVertexArray(self.vao)

        GL.glUniform3f(self.offsetUniform, 0.0, 0.0, 0.5)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indexData), GL.GL_UNSIGNED_SHORT, None)

        GL.glUniform3f(self.offsetUniform, 0.0, 0.0, -1.0)
        GL.glDrawElementsBaseVertex(GL.GL_TRIANGLES, len(self.indexData), GL.GL_UNSIGNED_SHORT, None, self.numberOfVertices/2)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        glfw.SwapBuffers()

    def reshape(self, w, h):
        self.perspectiveMatrix[0] = self.fFrustumScale / (w/float(h))
        self.perspectiveMatrix[5] = self.fFrustumScale

        GL.glUseProgram(self.theProgram)
        GL.glUniformMatrix4fv(self.perspectiveMatrixUnif,1,GL.GL_FALSE,self.perspectiveMatrix)
        GL.glUseProgram(0)

        GL.glViewport(0, 0, w, h);

    def keyboard(self, key, press):
        if key == glfw.KEY_ESC:
            glfw.Terminate()
            return

