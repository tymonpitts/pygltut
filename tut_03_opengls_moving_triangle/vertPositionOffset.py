import os
import math
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial

#Load shaders from files.
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, "data","positionOffset.vert"),'r') as myfile:
    VERTEX_SHADER = myfile.read()
with open(os.path.join(dirname, "data","standard.frag"),'r') as myfile:
    FRAGMENT_SHADER = myfile.read()

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None
        self.offsetLocation = None
        self.vertexPositions = [
             0.25, 0.25, 0.0, 1.0,
             0.25,-0.25, 0.0, 1.0,
            -0.25,-0.25, 0.0, 1.0]
        self.positionBufferObject = None
        self.vao = None

        self.num_vertex_components = 4
        self.vertex_size = 4

    def initializeProgram(self):
        shaderList = []

        shaderList.append(compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        self.theProgram = compileProgram(*shaderList)
        self.offsetLocation = GL.glGetUniformLocation(self.theProgram, "offset");

    def initializeVertexBuffer(self):
        self.positionBufferObject = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self.positionBufferObject)
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

    def computePostionOffsets(self):
        loop_duration = 5.0
        scale = (2.0 * math.pi) / loop_duration
        current_time_through_loop = self.elapsed_time % loop_duration
        x_offset = math.cos(current_time_through_loop * scale) * 0.5
        y_offset = math.sin(current_time_through_loop * scale) * 0.5
        return x_offset, y_offset

    def display(self):
        x_offset, y_offset = self.computePostionOffsets()

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glUseProgram(self.theProgram)

        GL.glUniform2f(self.offsetLocation, x_offset, y_offset)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.positionBufferObject)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, self.num_vertex_components, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

        GL.glDisableVertexAttribArray(0)
        GL.glUseProgram(0)

        glfw.SwapBuffers()

    def reshape(self, w, h):
        GL.glViewport(0, 0, w, h);

    def keyboard(self, key, press):
        if key == glfw.KEY_ESC:
            glfw.Terminate()
            return

