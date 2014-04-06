"""
NOTE: order of multiplication is different because numpy matrices 
      are row-major and the tutorial's matrices are column-major
"""
import os
import math
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial, Matrix, Vector, Point, clamp
from .data.hierarchy_data import VERTEX_DATA, INDICES, NUMBER_OF_VERTICES

#Load shaders from files.
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, "data","PosColorLocalTransform.vert"),'r') as myfile:
    VERTEX_SHADER = myfile.read()
with open(os.path.join(dirname, "data","ColorPassthrough.frag"),'r') as myfile:
    FRAGMENT_SHADER = myfile.read()

def rotateX(fAngDeg):
    fAngRad = math.radians(fAngDeg)
    fCos = math.cos(fAngRad)
    fSin = math.sin(fAngRad)

    theMat = Matrix()
    theMat[1,1] = fCos
    theMat[1,2] = fSin
    theMat[2,1] = -fSin
    theMat[2,2] = fCos

    return theMat

def rotateY(fAngDeg):
    fAngRad = math.radians(fAngDeg)
    fCos = math.cos(fAngRad)
    fSin = math.sin(fAngRad)

    theMat = Matrix()
    theMat[0,0] = fCos
    theMat[0,2] = -fSin
    theMat[2,0] = fSin
    theMat[2,2] = fCos

    return theMat

def rotateZ(fAngDeg):
    fAngRad = math.radians(fAngDeg)
    fCos = math.cos(fAngRad)
    fSin = math.sin(fAngRad)

    theMat = Matrix()
    theMat[0,0] = fCos
    theMat[0,1] = fSin
    theMat[1,0] = -fSin
    theMat[1,1] = fCos

    return theMat

class MatrixStack(object):
    def __init__(self):
        self.m_currMat = Matrix()
        self.m_matrices = []

    def top(self):
        return self.m_currMat

    def rotateX(self, fAngDeg):
        self.m_currMat = rotateX(fAngDeg) * self.m_currMat

    def rotateY(self, fAngDeg):
        self.m_currMat = rotateY(fAngDeg) * self.m_currMat

    def rotateZ(self, fAngDeg):
        self.m_currMat = rotateZ(fAngDeg) * self.m_currMat

    def scale(self, scaleVec):
        scaleMat = Matrix()
        for index in xrange(3):
            scaleMat[index, index] = scaleVec[index]

        self.m_currMat = scaleMat * self.m_currMat

    def translate(self, offsetVec):
        translateMat = Matrix()
        for index in xrange(3):
            translateMat[3, index] = offsetVec[index]

        self.m_currMat = translateMat * self.m_currMat

    def push(self):
        self.m_matrices.append(self.m_currMat.copy())

    def pop(self):
        self.m_currMat = self.m_matrices.pop()

class Hierarchy(object):
    STANDARD_ANGLE_INCREMENT = 11.25
    SMALL_ANGLE_INCREMENT = 9.0
    def __init__(self):
        self.posBase = (3.0, -5.0, -40.0)
        self.angBase = -45.0
        self.posBaseLeft = (2.0, 0.0, 0.0)
        self.posBaseRight = (-2.0, 0.0, 0.0)
        self.scaleBaseZ = 3.0
        self.angUpperArm = -33.75
        self.sizeUpperArm = 9.0
        self.posLowerArm = (0.0, 0.0, 8.0)
        self.angLowerArm = 146.25
        self.lenLowerArm = 5.0
        self.widthLowerArm = 1.5
        self.posWrist = (0.0, 0.0, 5.0)
        self.angWristRoll = 0.0
        self.angWristPitch = 67.5
        self.lenWrist = 2.0
        self.widthWrist = 2.0
        self.posLeftFinger = (1.0, 0.0, 1.0)
        self.posRightFinger = (-1.0, 0.0, 1.0)
        self.angFingerOpen = 180.0
        self.lenFinger = 2.0
        self.widthFinger = 0.5
        self.angLowerFinger = 45.0

    def draw(self, tutorial_object):
        modelToCameraStack = MatrixStack()

        GL.glUseProgram(tutorial_object.theProgram)
        GL.glBindVertexArray(tutorial_object.vao)

        modelToCameraStack.translate(self.posBase)
        modelToCameraStack.rotateY(self.angBase)

        # Draw left base
        #
        modelToCameraStack.push()
        modelToCameraStack.translate(self.posBaseLeft)
        modelToCameraStack.scale([1.0, 1.0, self.scaleBaseZ])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        # Draw right base
        #
        modelToCameraStack.push()
        modelToCameraStack.translate(self.posBaseRight)
        modelToCameraStack.scale([1.0, 1.0, self.scaleBaseZ])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        # Draw main arm
        self.drawUpperArm(modelToCameraStack, tutorial_object)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def adjBase(self, bIncrement):
        self.angBase += self.STANDARD_ANGLE_INCREMENT if bIncrement else -self.STANDARD_ANGLE_INCREMENT
        self.angBase = self.angBase % 360.0

    def adjUpperArm(self, bIncrement):
        self.angUpperArm += self.STANDARD_ANGLE_INCREMENT if bIncrement else -self.STANDARD_ANGLE_INCREMENT
        self.angUpperArm = clamp(self.angUpperArm, -90.0, 0.0)

    def adjLowerArm(self, bIncrement):
        self.angLowerArm += self.STANDARD_ANGLE_INCREMENT if bIncrement else -self.STANDARD_ANGLE_INCREMENT
        self.angLowerArm = clamp(self.angLowerArm, 0.0, 146.25)

    def adjWristPitch(self, bIncrement):
        self.angWristPitch += self.STANDARD_ANGLE_INCREMENT if bIncrement else -self.STANDARD_ANGLE_INCREMENT
        self.angWristPitch = clamp(self.angWristPitch, 0.0, 90.0)

    def adjWristRoll(self, bIncrement):
        self.angWristRoll += self.STANDARD_ANGLE_INCREMENT if bIncrement else -self.STANDARD_ANGLE_INCREMENT
        self.angWristRoll = self.angWristRoll % 360.0

    def adjFingerOpen(self, bIncrement):
        self.angFingerOpen += self.SMALL_ANGLE_INCREMENT if bIncrement else -self.SMALL_ANGLE_INCREMENT
        self.angFingerOpen = clamp(self.angFingerOpen, 9.0, 180.0)

    def writePose(self):
        print ('angBase:\t%f' % self.angBase)
        print ('angUpperArm:\t%f' % self.angUpperArm)
        print ('angLowerArm:\t%f' % self.angLowerArm)
        print ('angWristPitch:\t%f' % self.angWristPitch)
        print ('angWristRoll:\t%f' % self.angWristRoll)
        print ('angFingerOpen:\t%f' % self.angFingerOpen)
        print 

    def drawFingers(self, modelToCameraStack, tutorial_object):
        # draw left finger
        #
        modelToCameraStack.push()
        modelToCameraStack.translate(self.posLeftFinger)
        modelToCameraStack.rotateY(self.angFingerOpen)

        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenFinger / 2.0])
        modelToCameraStack.scale([self.widthFinger / 2.0, self.widthFinger / 2.0, self.lenFinger / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()


        # draw left lower finger
        #
        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenFinger])
        modelToCameraStack.rotateY(-self.angLowerFinger)

        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenFinger / 2.0])
        modelToCameraStack.scale([self.widthFinger / 2.0, self.widthFinger / 2.0, self.lenFinger / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        modelToCameraStack.pop()


        modelToCameraStack.pop()

        # draw right finger
        #
        modelToCameraStack.push()
        modelToCameraStack.translate(self.posRightFinger)
        modelToCameraStack.rotateY(-self.angFingerOpen)

        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenFinger / 2.0])
        modelToCameraStack.scale([self.widthFinger / 2.0, self.widthFinger / 2.0, self.lenFinger / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()


        # draw right lower finger
        #
        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenFinger])
        modelToCameraStack.rotateY(self.angLowerFinger)

        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenFinger / 2.0])
        modelToCameraStack.scale([self.widthFinger / 2.0, self.widthFinger / 2.0, self.lenFinger / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        modelToCameraStack.pop()


        modelToCameraStack.pop()

    def drawWrist(self, modelToCameraStack, tutorial_object):
        modelToCameraStack.push()
        modelToCameraStack.translate(self.posWrist)
        modelToCameraStack.rotateZ(self.angWristRoll)
        modelToCameraStack.rotateX(self.angWristPitch)

        modelToCameraStack.push()
        modelToCameraStack.scale([self.widthWrist / 2.0, self.widthWrist / 2.0, self.lenWrist / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        self.drawFingers(modelToCameraStack, tutorial_object)

        modelToCameraStack.pop()

    def drawLowerArm(self, modelToCameraStack, tutorial_object):
        modelToCameraStack.push()
        modelToCameraStack.translate(self.posLowerArm)
        modelToCameraStack.rotateX(self.angLowerArm)

        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, self.lenLowerArm / 2.0])
        modelToCameraStack.scale([self.widthLowerArm / 2.0, self.widthLowerArm / 2.0, self.lenLowerArm / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        self.drawWrist(modelToCameraStack, tutorial_object)

        modelToCameraStack.pop()

    def drawUpperArm(self, modelToCameraStack, tutorial_object):
        modelToCameraStack.push()
        modelToCameraStack.rotateX(self.angUpperArm)

        modelToCameraStack.push()
        modelToCameraStack.translate([0.0, 0.0, (self.sizeUpperArm / 2.0) - 1.0])
        modelToCameraStack.scale([1.0, 1.0, self.sizeUpperArm / 2.0])
        GL.glUniformMatrix4fv(tutorial_object.modelToCameraMatrixUnif, 1, GL.GL_FALSE, modelToCameraStack.top().tolist())
        GL.glDrawElements(GL.GL_TRIANGLES, len(tutorial_object.indexData), GL.GL_UNSIGNED_SHORT, None)
        modelToCameraStack.pop()

        self.drawLowerArm(modelToCameraStack, tutorial_object)

        modelToCameraStack.pop()

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.theProgram = None

        self.positionAttrib = None
        self.colorAttrib = None

        self.modelToCameraMatrixUnif = None
        self.cameraToClipMatrixUnif = None

        self.cameraToClipMatrix = Matrix()

        self.fFrustumScale = self.calcFrustumScale(45.0)

        self.armature = Hierarchy()

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

        self.positionAttrib = GL.glGetAttribLocation(self.theProgram, "position")
        self.colorAttrib = GL.glGetAttribLocation(self.theProgram, "color")

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

    def initializeVAO(self):
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

        # NOTE: generating vao before initializeProgram due to a validation
        #       problem on OSX.  For some reason a vao must be bound to 
        #       compile properly on OSX
        GL.glBindVertexArray(self.vao)

        colorDataOffset = 3*self.float_size*self.numberOfVertices
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self.vertexBufferObject)
        GL.glEnableVertexAttribArray(self.positionAttrib)
        GL.glEnableVertexAttribArray(self.colorAttrib)
        GL.glVertexAttribPointer(self.positionAttrib, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glVertexAttribPointer(self.colorAttrib, 4, GL.GL_FLOAT, GL.GL_FALSE, 0, GL.GLvoidp(colorDataOffset))
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,self.indexBufferObject)

        GL.glBindVertexArray(0)

    def init(self):
        # NOTE: see initializeVAO for an explaination of why this is 
        #       being generated here 
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.initializeProgram()
        self.initializeVAO()


        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CW)

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)

    def display(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClearDepth(1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.armature.draw(self)

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
        elif key == 'A': self.armature.adjBase(True)
        elif key == 'D': self.armature.adjBase(False)
        elif key == 'W': self.armature.adjUpperArm(True)
        elif key == 'S': self.armature.adjUpperArm(False)
        elif key == 'R': self.armature.adjLowerArm(True)
        elif key == 'F': self.armature.adjLowerArm(False)
        elif key == 'T': self.armature.adjWristPitch(True)
        elif key == 'G': self.armature.adjWristPitch(False)
        elif key == 'Z': self.armature.adjWristRoll(True)
        elif key == 'C': self.armature.adjWristRoll(False)
        elif key == 'Q': self.armature.adjFingerOpen(True)
        elif key == 'E': self.armature.adjFingerOpen(False)
        elif key == ' ': self.armature.writePose()


