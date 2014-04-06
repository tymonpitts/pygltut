import os
import math
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial, Matrix, Vector, Point
from .data.vertex_data import VERTEX_DATA, INDICES, NUMBER_OF_VERTICES

#Load shaders from files.
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, "data","PosColorLocalTransform.vert"),'r') as myfile:
    VERTEX_SHADER = myfile.read()
with open(os.path.join(dirname, "data","ColorPassthrough.frag"),'r') as myfile:
    FRAGMENT_SHADER = myfile.read()

class Instance(object):
    def __init__(self, offset):
        self.offset = offset

    def calcLerpFactor(self, fElapsedTime, fLoopDuration):
        fValue = fElapsedTime % fLoopDuration / fLoopDuration
        if fValue > 0.5:
            fValue = 1.0 - fValue
        return fValue * 2.0

    def computeAngleRad(self, fElapsedTime, fLoopDuration):
        fScale = math.pi * 2.0 / fLoopDuration
        fCurrTimeThroughLoop = fElapsedTime % fLoopDuration
        return fCurrTimeThroughLoop * fScale

    def calcRotation(self, fElapsedTime):
        raise NotImplementedError

    def constructMatrix(self, fElapsedTime):
        theMat = self.calcRotation(fElapsedTime)
        for index in xrange(3):
            theMat[3, index] = self.offset[index]

        return theMat

class NullRotation(Instance):
    def calcRotation(self, fElapsedTime):
        return Matrix()

class RotateX(Instance):
    def calcRotation(self, fElapsedTime):
        fAngRad = self.computeAngleRad(fElapsedTime, 3.0)
        fCos = math.cos(fAngRad)
        fSin = math.sin(fAngRad)

        theMat = Matrix()
        theMat[1,1] = fCos
        theMat[1,2] = fSin
        theMat[2,1] = -fSin
        theMat[2,2] = fCos

        return theMat

class RotateY(Instance):
    def calcRotation(self, fElapsedTime):
        fAngRad = self.computeAngleRad(fElapsedTime, 3.0)
        fCos = math.cos(fAngRad)
        fSin = math.sin(fAngRad)

        theMat = Matrix()
        theMat[0,0] = fCos
        theMat[0,2] = -fSin
        theMat[2,0] = fSin
        theMat[2,2] = fCos

        return theMat

class RotateZ(Instance):
    def calcRotation(self, fElapsedTime):
        fAngRad = self.computeAngleRad(fElapsedTime, 3.0)
        fCos = math.cos(fAngRad)
        fSin = math.sin(fAngRad)

        theMat = Matrix()
        theMat[0,0] = fCos
        theMat[0,1] = fSin
        theMat[1,0] = -fSin
        theMat[1,1] = fCos

        return theMat

class RotateAxis(Instance):
    def calcRotation(self, fElapsedTime):
        fAngRad = self.computeAngleRad(fElapsedTime, 2.0)
        fCos = math.cos(fAngRad)
        fInvCos = 1.0 - fCos
        fSin = math.sin(fAngRad)
        fInvSin = 1.0 - fSin

        axis = Vector(1, 1, 1)
        axis.normalize()
        theMat = Matrix()
        theMat[0,0] = (axis.x * axis.x) + ((1- axis.x * axis.x) * fCos)
        theMat[1,0] = axis.x * axis.y * (fInvCos) - (axis.z * fSin)
        theMat[2,0] = axis.x * axis.z * (fInvCos) + (axis.y * fSin)

        theMat[0,1] = axis.x * axis.y * (fInvCos) + (axis.z * fSin)
        theMat[1,1] = (axis.y * axis.y) + ((1 - axis.y * axis.y) * fCos)
        theMat[2,1] = axis.y * axis.z * (fInvCos) - (axis.x * fSin)

        theMat[0,2] = axis.x * axis.z * (fInvCos) - (axis.y * fSin)
        theMat[1,2] = axis.y * axis.z * (fInvCos) + (axis.x * fSin)
        theMat[2,2] = (axis.z * axis.z) + ((1 - axis.z * axis.z) * fCos)
        return theMat

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None

        self.modelToCameraMatrixUnif = None
        self.cameraToClipMatrixUnif = None

        self.cameraToClipMatrix = Matrix()

        self.fFrustumScale = self.calcFrustumScale(45.0)

        self.instanceList = [
                NullRotation([0.0, 0.0, -25.0]),
                RotateX([-5.0, -5.0, -25.0]),
                RotateY([-5.0, 5.0, -25.0]),
                RotateZ([5.0, 5.0, -25.0]),
                RotateAxis([5.0, -5.0, -25.0])]
        
        self.vertexData = VERTEX_DATA
        self.numberOfVertices = NUMBER_OF_VERTICES
        self.indexData = INDICES

        self.vertexBufferObject = None
        self.indexBufferObject = None
        self.vao = None

    def calcFrustumScale(self, fFovDeg):
        return 1.0 / math.tan(math.radians(fFovDeg / 2.0))

    def initializeProgram(self):
        shaderList = []

        shaderList.append(compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        self.theProgram = compileProgram(*shaderList)

        self.modelToCameraMatrixUnif = GL.glGetUniformLocation(self.theProgram, "modelToCameraMatrix")
        self.cameraToClipMatrixUnif = GL.glGetUniformLocation(self.theProgram, "cameraToClipMatrix")

        fzNear = 1.0
        fzFar = 61.0

        self.cameraToClipMatrix[0, 0] = self.fFrustumScale
        self.cameraToClipMatrix[1, 1] = self.fFrustumScale
        self.cameraToClipMatrix[2, 2] = (fzFar+fzNear)/(fzNear-fzFar)
        self.cameraToClipMatrix[2, 3] = -1.0
        self.cameraToClipMatrix[3, 2] = (2*fzFar*fzNear)/(fzNear-fzFar)

        GL.glUseProgram(self.theProgram)
        GL.glUniformMatrix4fv(self.cameraToClipMatrixUnif,1,GL.GL_FALSE,self.cameraToClipMatrix.tolist())
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

        for currInst in self.instanceList:
            transformMatrix = currInst.constructMatrix(self.elapsed_time)

            GL.glUniformMatrix4fv(self.modelToCameraMatrixUnif, 1, GL.GL_FALSE, transformMatrix.tolist())
            GL.glDrawElements(GL.GL_TRIANGLES, len(self.indexData), GL.GL_UNSIGNED_SHORT, None)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        glfw.SwapBuffers()

    def reshape(self, w, h):
        self.cameraToClipMatrix[0, 0] = self.fFrustumScale / (w/float(h))
        self.cameraToClipMatrix[1, 1] = self.fFrustumScale

        GL.glUseProgram(self.theProgram)
        GL.glUniformMatrix4fv(self.cameraToClipMatrixUnif,1,GL.GL_FALSE,self.cameraToClipMatrix.tolist())
        GL.glUseProgram(0)

        GL.glViewport(0, 0, w, h);

    def keyboard(self, key, press):
        if key == glfw.KEY_ESC:
            glfw.Terminate()
            return

