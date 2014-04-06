"""
NOTE: order of multiplication is different because numpy matrices 
      are row-major and the tutorial's matrices are column-major
"""
import os
import math
import glfw
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from gltut_framework import AbstractTutorial, MatrixStack, Matrix, Vector, Point, clamp
from .data.tree_positions import FOREST as g_forest
from .data import unit_cube, unit_plane

#TMP
from .data.tmp_vertex_data import VERTEX_DATA, INDICES, NUMBER_OF_VERTICES
#TMP

# NOTE:
# import depth_clamp as an ARB extension to make this work.
# OpenGL.GL should include GL_DEPTH_CLAMP, but it doesn't.
from OpenGL.GL.ARB import depth_clamp

TUT_DIR = os.path.abspath(os.path.dirname(__file__))

class ProgramData(object):
    def __init__(self):
        self.theProgram = None
        self.modelToWorldMatrixUnif = None
        self.worldToCameraMatrixUnif = None
        self.cameraToClipMatrixUnif = None
        self.baseColorUnif = None

class Tutorial(AbstractTutorial):
    def __init__(self, *args, **kwargs):
        super(Tutorial, self).__init__(*args, **kwargs)
        self.uniformColor = None
        self.objectColor = None
        self.uniformColorTint = None

        self.fzNear = 1.0
        self.fzFar = 1000.0

        self.pConeMesh = None
        self.pCylinderMesh = None
        self.pCubeTintMesh = None
        self.pCubeColorMesh = None
        self.pPlaneMesh = None

        self.fYAngle = 0.0
        self.fXAngle = 0.0

        self.fColumnBaseHeight = 0.25

        self.fParthenonWidth = 14.0
        self.fParthenonLength = 20.0
        self.fParthenonColumnHeight = 5.0
        self.fParthenonBaseHeight = 1.0
        self.fParthenonTopHeight = 2.0

        self.bDrawLookatPoint = False
        self.camTarget = Point(0.0, 0.4, 0.0)

        self.sphereCamRelPos = Point(67.5, -46.0, 150.0)

        self._lshift_pressed = False
        self._rshift_pressed = False

    def loadProgram(self, strVertexShader, strFragmentShader):
        with open(os.path.join(TUT_DIR, "data",strVertexShader),'r') as myfile:
            vertex_shader = myfile.read()
        with open(os.path.join(TUT_DIR, "data",strFragmentShader),'r') as myfile:
            fragment_shader = myfile.read()

        shaderList = []

        shaderList.append(compileShader(vertex_shader, GL.GL_VERTEX_SHADER))
        shaderList.append(compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER))

        data = ProgramData()
        data.theProgram = compileProgram(*shaderList)
        data.modelToWorldMatrixUnif = GL.glGetUniformLocation(data.theProgram, "modelToWorldMatrix")
        data.worldToCameraMatrixUnif = GL.glGetUniformLocation(data.theProgram, "worldToCameraMatrix")
        data.cameraToClipMatrixUnif = GL.glGetUniformLocation(data.theProgram, "cameraToClipMatrix")
        data.baseColorUnif = GL.glGetUniformLocation(data.theProgram, "baseColor")

        return data

    def initializeProgram(self):
        self.uniformColor = self.loadProgram("PosOnlyWorldTransform.vert", "ColorUniform.frag")
        self.objectColor = self.loadProgram("PosColorWorldTransform.vert", "ColorPassthrough.frag")
        # self.uniformColorTint = self.loadProgram("PosColorWorldTransform.vert", "ColorMultUniform.frag")
        self.uniformColorTint = self.loadProgram("PosOnlyWorldTransform.vert", "ColorUniform.frag")

    def calcLookAtMatrix(self, cameraPt, lookPt, upPt):
        lookDir = (lookPt - cameraPt).normal()
        upDir = upPt.normal()

        rightDir = (lookDir ^ upDir).normal()
        perpUpDir = rightDir ^ lookDir

        rotMat = Matrix()
        for i in xrange(3):
            rotMat[0, i] = rightDir[i]
            rotMat[1, i] = perpUpDir[i]
            rotMat[2, i] = -lookDir[i]



            rotMat[3, i] = cameraPt[i]
        rotMat = rotMat.inverse()
        return rotMat

        # rotMat = rotMat.transpose()

        # transMat = Matrix()
        # for i in xrange(3):
        #     transMat[3, i] = -cameraPt[i]

        # return transMat * rotMat

    def init(self):
        tmp_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(tmp_vao)

        self.initializeProgram()

        self.pConeMesh = unit_cube.create_mesh()
        self.pCylinderMesh = unit_cube.create_mesh()
        self.pCubeTintMesh = unit_cube.create_mesh()
        self.pCubeColorMesh = unit_cube.create_mesh()
        self.pPlaneMesh = unit_plane.create_mesh()

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CW)

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)
        GL.glEnable(depth_clamp.GL_DEPTH_CLAMP)

    def drawTree(self, modelMatrix, fTrunkHeight=2.0, fConeHeight=3.0):
        # Draw trunk.
        with modelMatrix:
            modelMatrix.scale(Vector(1.0, fTrunkHeight, 1.0))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 0.694, 0.4, 0.106, 1.0)
            self.pCylinderMesh.render()
            GL.glUseProgram(0)

        # Draw the treetop.
        with modelMatrix:
            modelMatrix.translate(Vector(0.0, fTrunkHeight, 0.0))
            modelMatrix.scale(Vector(3.0, fConeHeight, 3.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 0.0, 1.0, 0.0, 1.0)
            self.pConeMesh.render()
            GL.glUseProgram(0)

    def drawColumn(self, modelMatrix, fHeight=5.0):
        # Draw the bottom of the column.
        with modelMatrix:
            modelMatrix.scale(Vector(1.0, self.fColumnBaseHeight, 1.0))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 1.0, 1.0, 1.0, 1.0)
            self.pConeMesh.render()
            GL.glUseProgram(0)

        # Draw the top of the column.
        with modelMatrix:
            modelMatrix.translate(Vector(0.0, fHeight - self.fColumnBaseHeight, 0.0))
            modelMatrix.scale(Vector(1.0, self.fColumnBaseHeight, 1.0))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 0.9, 0.9, 0.9, 0.9)
            self.pCubeTintMesh.render()
            GL.glUseProgram(0)

        # Draw the main column.
        with modelMatrix:
            modelMatrix.translate(Vector(0.0, self.fColumnBaseHeight, 0.0))
            modelMatrix.scale(Vector(1.0, fHeight - (self.fColumnBaseHeight * 2.0), 0.8))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 0.9, 0.9, 0.9, 0.9)
            self.pCubeTintMesh.render()
            GL.glUseProgram(0)

    def drawParthenon(self, modelMatrix):
        # Draw base.
        with modelMatrix:
            modelMatrix.scale(Vector(self.fParthenonWidth, self.fParthenonBaseHeight, self.fParthenonLength))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 0.9, 0.9, 0.9, 0.9)
            self.pConeMesh.render()
            GL.glUseProgram(0)

        # Draw top.
        with modelMatrix:
            modelMatrix.translate(Vector(0.0, self.fParthenonColumnHeight + self.fParthenonBaseHeight, 0.0))
            modelMatrix.scale(Vector(self.fParthenonWidth, self.fParthenonTopHeight, self.fParthenonLength))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            GL.glUseProgram(self.uniformColorTint.theProgram)
            GL.glUniformMatrix4fv(self.uniformColorTint.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColorTint.baseColorUnif, 0.9, 0.9, 0.9, 0.9)
            self.pConeMesh.render()
            GL.glUseProgram(0)

        # Draw columns.
        fFrontZVal = (self.fParthenonLength / 2.0) - 1.0
        fRightXVal = (self.fParthenonWidth / 2.0) - 1.0

        for iColumnNum in xrange(int(self.fParthenonWidth / 2.0)):
            with modelMatrix:
                modelMatrix.translate(Vector((2.0 * iColumnNum) - (self.fParthenonWidth / 2.0) + 1.0,
                        self.fParthenonBaseHeight, fFrontZVal))

                self.drawColumn(modelMatrix, self.fParthenonColumnHeight)

            with modelMatrix:
                modelMatrix.translate(Vector((2.0 * iColumnNum) - (self.fParthenonWidth / 2.0) + 1.0,
                        self.fParthenonBaseHeight, -fFrontZVal))

                self.drawColumn(modelMatrix, self.fParthenonColumnHeight)

        # Don't draw the first or last columns, since they've been drawn already.
        for iColumnNum in xrange(1, int((self.fParthenonLength - 2.0) / 2.0)):
            with modelMatrix:
                modelMatrix.translate(Vector(fRightXVal, self.fParthenonBaseHeight,
                        (2.0 * iColumnNum) - (self.fParthenonLength / 2.0) + 1.0))

                self.drawColumn(modelMatrix, self.fParthenonColumnHeight)

            with modelMatrix:
                modelMatrix.translate(Vector(-fRightXVal, self.fParthenonBaseHeight,
                        (2.0 * iColumnNum) - (self.fParthenonLength / 2.0) + 1.0))

                self.drawColumn(modelMatrix, self.fParthenonColumnHeight)

        # Draw interior.
        with modelMatrix:
            modelMatrix.translate(Vector(0.0, 1.0, 0.0))
            modelMatrix.scale(Vector(self.fParthenonWidth - 6.0, self.fParthenonColumnHeight,
                    self.fParthenonLength - 6.0))
            modelMatrix.translate(Vector(0.0, 0.5, 0.0))

            # GL.glUseProgram(self.objectColor.theProgram)
            # GL.glUniformMatrix4fv(self.objectColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            # TMP COLOR
            GL.glUseProgram(self.uniformColor.theProgram)
            GL.glUniformMatrix4fv(self.uniformColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColor.baseColorUnif, 1.0, 1.0, 1.0, 1.0)

            self.pCubeColorMesh.render()
            GL.glUseProgram(0)

        # Draw headpiece
        with modelMatrix:
            modelMatrix.translate(Vector(
                    0.0, 
                    self.fParthenonColumnHeight + self.fParthenonBaseHeight + (self.fParthenonTopHeight / 2.0),
                    self.fParthenonLength / 2.0))
            modelMatrix.rotateX(-135.0)
            modelMatrix.rotateY(45.0)

            # GL.glUseProgram(self.objectColor.theProgram)
            # GL.glUniformMatrix4fv(self.objectColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            # TMP COLOR
            GL.glUseProgram(self.uniformColor.theProgram)
            GL.glUniformMatrix4fv(self.uniformColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColor.baseColorUnif, 1.0, 1.0, 1.0, 1.0)

            self.pCubeColorMesh.render()
            GL.glUseProgram(0)

    def drawForest(self, modelMatrix):
        for currTree in g_forest:
            with modelMatrix:
                modelMatrix.translate(Vector(currTree.fXPos, 0.0, currTree.fZPos))
                self.drawTree(modelMatrix, currTree.fTrunkHeight, currTree.fConeHeight)

    def resolveCamPosition(self):
        tempMat = MatrixStack() # not needed?

        phi = math.radians(self.sphereCamRelPos.x)
        theta = math.radians(self.sphereCamRelPos.y + 90.0)

        fSinTheta = math.sin(theta)
        fCosTheta = math.cos(theta)
        fSinPhi = math.sin(phi)
        fCosPhi = math.cos(phi)

        dirToCamera = Vector(fSinTheta * fCosPhi, fCosTheta, fSinTheta * fSinPhi)
        result = (dirToCamera * self.sphereCamRelPos.z)
        result = result + self.camTarget
        return Point(result[0], result[1], result[2])

    def display(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClearDepth(1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        camPos = self.resolveCamPosition()

        camMatrix = MatrixStack()
        camMatrix.m_currMat = self.calcLookAtMatrix(camPos, self.camTarget, Vector(0,1,0))
        camMatrix.push()

        GL.glUseProgram(self.uniformColor.theProgram)
        GL.glUniformMatrix4fv(self.uniformColor.worldToCameraMatrixUnif,1,GL.GL_FALSE,camMatrix.top().tolist())
        GL.glUseProgram(self.objectColor.theProgram)
        GL.glUniformMatrix4fv(self.objectColor.worldToCameraMatrixUnif,1,GL.GL_FALSE,camMatrix.top().tolist())
        GL.glUseProgram(self.uniformColorTint.theProgram)
        GL.glUniformMatrix4fv(self.uniformColorTint.worldToCameraMatrixUnif,1,GL.GL_FALSE,camMatrix.top().tolist())
        GL.glUseProgram(0)

        modelMatrix = MatrixStack()

        # Render the ground plane.
        with modelMatrix:
            modelMatrix.scale(Vector(100.0, 1.0, 100.0))

            GL.glUseProgram(self.uniformColor.theProgram)
            GL.glUniformMatrix4fv(self.uniformColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
            GL.glUniform4f(self.uniformColor.baseColorUnif, 0.302, 0.416, 0.0589, 1.0)
            self.pPlaneMesh.render()
            GL.glUseProgram(0)

        # Draw the trees
        self.drawForest(modelMatrix)

        # Draw the building.
        with modelMatrix:
            modelMatrix.translate(Vector(20.0, 0.0, -10.0))

            self.drawParthenon(modelMatrix)

        if self.bDrawLookatPoint:
            GL.glDisable(GL.GL_DEPTH_TEST)
            identity = Matrix()

            with modelMatrix:
                cameraAimVec = self.camTarget - camPos
                modelMatrix.translate(Vector(0.0, 0.0, -cameraAimVec.length()))
                modelMatrix.scale(Vector(1.0, 1.0, 1.0))

                # GL.glUseProgram(self.objectColor.theProgram)
                # GL.glUniformMatrix4fv(self.objectColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
                # GL.glUniformMatrix4fv(self.objectColor.worldToCameraMatrixUnif,1,GL.GL_FALSE,identity.tolist())
                # TMP COLOR
                GL.glUseProgram(self.uniformColor.theProgram)
                GL.glUniformMatrix4fv(self.uniformColor.modelToWorldMatrixUnif,1,GL.GL_FALSE,modelMatrix.top().tolist())
                GL.glUniformMatrix4fv(self.uniformColor.worldToCameraMatrixUnif,1,GL.GL_FALSE,identity.tolist())
                GL.glUniform4f(self.uniformColor.baseColorUnif, 1.0, 1.0, 1.0, 1.0)

                self.pCubeColorMesh.render()
                GL.glUseProgram(0)
                GL.glEnable(GL.GL_DEPTH_TEST)

        glfw.SwapBuffers()

    def reshape(self, w, h):
        persMatrix = MatrixStack()
        persMatrix.perspective(45.0, (w/float(h)), self.fzNear, self.fzFar)

        GL.glUseProgram(self.uniformColor.theProgram)
        GL.glUniformMatrix4fv(self.uniformColor.cameraToClipMatrixUnif,1,GL.GL_FALSE,persMatrix.top().tolist())
        GL.glUseProgram(self.objectColor.theProgram)
        GL.glUniformMatrix4fv(self.objectColor.cameraToClipMatrixUnif,1,GL.GL_FALSE,persMatrix.top().tolist())
        GL.glUseProgram(self.uniformColorTint.theProgram)
        GL.glUniformMatrix4fv(self.uniformColorTint.cameraToClipMatrixUnif,1,GL.GL_FALSE,persMatrix.top().tolist())
        GL.glUseProgram(0)

        GL.glViewport(0, 0, w, h)

    def keyboard(self, key, press):
        shift = self._lshift_pressed or self._rshift_pressed
        speed_modifier = 0.1 if shift else 1.0
        move_speed = 4.0
        if key == glfw.KEY_ESC:
            glfw.Terminate()
            return
        elif key == glfw.KEY_LSHIFT:
            self._lshift_pressed = press
            return
        elif key == glfw.KEY_RSHIFT:
            self._rshift_pressed = press
            return
        elif not press:
            return

        elif key == 'W': self.camTarget.z -= move_speed * speed_modifier
        elif key == 'S': self.camTarget.z += move_speed * speed_modifier
        elif key == 'D': self.camTarget.x += move_speed * speed_modifier
        elif key == 'A': self.camTarget.x -= move_speed * speed_modifier
        elif key == 'E': self.camTarget.y -= move_speed * speed_modifier
        elif key == 'Q': self.camTarget.y += move_speed * speed_modifier
        elif key == 'I': self.sphereCamRelPos.y -= 11.25 * speed_modifier
        elif key == 'K': self.sphereCamRelPos.y += 11.25 * speed_modifier
        elif key == 'J': self.sphereCamRelPos.x -= 11.25 * speed_modifier
        elif key == 'L': self.sphereCamRelPos.x += 11.25 * speed_modifier
        elif key == 'O': self.sphereCamRelPos.z -= 5.0 * speed_modifier
        elif key == 'U': self.sphereCamRelPos.z += 5.0 * speed_modifier

        elif key == ' ':
            self.bDrawLookatPoint = not self.bDrawLookatPoint
            print 'Target: %f, %f, %f' % (self.camTarget.x, self.camTarget.y, self.camTarget.z)
            print 'Position: %f, %f, %f' % (self.sphereCamRelPos.x, self.sphereCamRelPos.y, self.sphereCamRelPos.z)

        self.sphereCamRelPos.y = clamp(self.sphereCamRelPos.y, -78.75, -1.0)
        self.camTarget.y = max(self.camTarget.y, 0.0)
        self.sphereCamRelPos.z = max(self.sphereCamRelPos.z, 5.0)

