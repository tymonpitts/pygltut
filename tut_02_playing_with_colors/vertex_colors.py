import os
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial

#Load shaders from files.
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, "data","VertexColors.vert"),'r') as myfile:
    VERTEX_SHADER = myfile.read()
with open(os.path.join(dirname, "data","VertexColors.frag"),'r') as myfile:
    FRAGMENT_SHADER = myfile.read()

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None
        self.vertexPositions = [
             0.0, 0.5, 0.0, 1.0,
             0.5,-0.366, 0.0, 1.0,
            -0.5,-0.366, 0.0, 1.0,

             1.0, 0.0, 0.0, 1.0,
             0.0, 1.0, 0.0, 1.0,
             0.0, 0.0, 1.0, 1.0]
        self.vertexBufferObject = None
        self.vao = None

        self.num_vertex_components = 4
        self.vertex_size = 4

    def initializeProgram(self):
        shaderList = []

        shaderList.append(compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        self.theProgram = compileProgram(*shaderList)

    def initializeVertexBuffer(self):
        self.vertexBufferObject = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self.vertexBufferObject)
        array_type = (GL.GLfloat*len(self.vertexPositions))
        GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(self.vertexPositions)*self.vertex_size,
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

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertexBufferObject)


        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(0, self.num_vertex_components, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        colorData = GL.GLvoidp((len(self.vertexPositions) * 4) / 2)
        GL.glVertexAttribPointer(1, self.num_vertex_components, GL.GL_FLOAT, GL.GL_FALSE, 0, colorData)

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

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

