from mesh import Mesh

import os
import sys
import time
import math
import numpy
import glfw
import OpenGL
from OpenGL.GL import *
from OpenGL.GLE import *

SHORT_SIZE = 2
FLOAT_SIZE = 4

def clamp(value, minValue, maxValue):
    return max(minValue, min(maxValue, value))

class AbstractTutorial(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.start_time = time.time()
        self.elapsed_time = 0.0

        self.num_vertex_components = 4
        self.float_size = 4
        self.short_size = 2

    def get_window_title(self):
        return os.path.dirname(__file__)

    def get_window_size(self):
        return (500, 500)

    def init(self):
        pass
        
    def display(self):
        pass
        
    def reshape(self, w, h):
        pass
        
    def keyboard(self, key, press):
        pass
        
    def run(self):
        glfw.Init()
         
        glfw.OpenWindowHint( glfw.OPENGL_VERSION_MAJOR, 3);
        glfw.OpenWindowHint( glfw.OPENGL_VERSION_MINOR, 2)
        glfw.OpenWindowHint( glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        glfw.OpenWindowHint( glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
         
        width, height = self.get_window_size()
        glfw.OpenWindow(
            width, height,
            8, 8, 8,
            8, 24, 0,
            glfw.WINDOW
            )
        
        glfw.SetWindowTitle(self.get_window_title())

        # glload::LoadFunctions()
        # gleIntClear()
        # gleIntLoadBaseFuncs()
        # gleIntLoad_Version_3_2()

        self.init()

        glfw.SetWindowSizeCallback(self.reshape)
        glfw.SetKeyCallback(self.keyboard)

        while glfw.GetWindowParam(glfw.OPENED):
            self.elapsed_time = time.time() - self.start_time
            self.display()


        # # print glGetString(GL_VERSION)
        # glutInit(sys.argv)
        # glutInitDisplayMode(self.get_display_mode())
        # glutInitContextVersion(3, 3)
        # if self.debug:
        #     glutInitContextFlags(GLUT_DEBUG)
        # width, height = self.get_window_size()
        # glutInitWindowSize(width, height)
        # glutInitWindowPosition(300, 200)
        # window = glutCreateWindow(sys.argv[1])

        # # glload::LoadFunctions()
        # gleIntClear()
        # gleIntLoadBaseFuncs()
        # gleIntLoad_Version_3_2()

        # glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)

        # # if(!glload::IsVersionGEQ(3, 3))
        # # {
        # #     printf("Your OpenGL version is %i, %i. You must have at least OpenGL 3.3 to run this tutorial.\n",
        # #         glload::GetMajorVersion(), glload::GetMinorVersion());
        # #     glutDestroyWindow(window);
        # #     return 0;
        # # }

        # # if(glext_ARB_debug_output)
        # # {
        # #     glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS_ARB);
        # #     glDebugMessageCallbackARB(DebugFunc, (void*)15);
        # # }

        # self.init()

        # glutDisplayFunc(self.display) 
        # glutReshapeFunc(self.reshape)
        # glutKeyboardFunc(self.keyboard)
        # glutMainLoop()

class Matrix(object):
    def __init__(self, data=None):
        if data is not None:
            self._data = data.copy()
        else:
            self._data = numpy.matrix([
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]], dtype=float)

    def transpose(self):
         data = numpy.transpose(self._data)
         return type(self)(data=data)

    def copy(self):
        return Matrix(data=self._data)

    def tolist(self):
        return self._data.tolist()

    def inverse(self):
        return type(self)(data=self._data.I)

    def __getitem__(self, index):
        if not hasattr(index, '__iter__'):
            raise IndexError('index must be a sequence, not %s' % type(index).__name__)
        return self._data.item(*index)

    def __setitem__(self, index, value):
        if not hasattr(index, '__iter__'):
            raise IndexError('index must be a sequence, not %s' % type(index).__name__)
        self._data.itemset(index[0], index[1], value)

    def __mul__(self, other):
        data = numpy.dot(self._data, other._data)
        return Matrix(data=data)

    def __imul__(self, other):
        self._data = numpy.dot(self._data, other._data)

class MatrixStack(object):
    def __init__(self):
        self.m_currMat = Matrix()
        self.m_matrices = []
        self.__enter_lengths = []

    def __enter__(self):
        self.__enter_lengths.append(len(self.m_matrices))

    def __exit__(self, typ, val, tb):
        enter_len = self.__enter_lengths.pop()
        self.m_matrices = self.m_matrices[:enter_len]
        if self.m_matrices:
            self.m_currMat = self.m_matrices[-1]
        else:
            self.m_currMat = Matrix()

    def top(self):
        return self.m_currMat

    def rotateX(self, fAngDeg):
        fAngRad = math.radians(fAngDeg)
        fCos = math.cos(fAngRad)
        fSin = math.sin(fAngRad)

        theMat = Matrix()
        theMat[1,1] = fCos
        theMat[1,2] = fSin
        theMat[2,1] = -fSin
        theMat[2,2] = fCos

        self.m_currMat = theMat * self.m_currMat
        self.push()

    def rotateY(self, fAngDeg):
        fAngRad = math.radians(fAngDeg)
        fCos = math.cos(fAngRad)
        fSin = math.sin(fAngRad)

        theMat = Matrix()
        theMat[0,0] = fCos
        theMat[0,2] = -fSin
        theMat[2,0] = fSin
        theMat[2,2] = fCos

        self.m_currMat = theMat * self.m_currMat
        self.push()

    def rotateZ(self, fAngDeg):
        fAngRad = math.radians(fAngDeg)
        fCos = math.cos(fAngRad)
        fSin = math.sin(fAngRad)

        theMat = Matrix()
        theMat[0,0] = fCos
        theMat[0,1] = fSin
        theMat[1,0] = -fSin
        theMat[1,1] = fCos

        self.m_currMat = theMat * self.m_currMat
        self.push()

    def scale(self, scaleVec):
        scaleMat = Matrix()
        for index in xrange(3):
            scaleMat[index, index] = scaleVec[index]

        self.m_currMat = scaleMat * self.m_currMat
        self.push()

    def translate(self, offsetVec):
        translateMat = Matrix()
        for index in xrange(3):
            translateMat[3, index] = offsetVec[index]

        self.m_currMat = translateMat * self.m_currMat
        self.push()

    def push(self):
        self.m_matrices.append(self.m_currMat.copy())

    def pop(self):
        self.m_currMat = self.m_matrices.pop()

    def perspective(self, fovy, aspect, zNear, zFar):
        range = math.tan(math.radians(fovy)/2.0) * zNear
        left = -range * aspect
        right = range * aspect
        bottom = -range
        top = range

        result = Matrix()
        result[0,0] = (2.0 * zNear) / (right - left)
        result[1,1] = (2.0 * zNear) / (top - bottom)
        result[2,2] = -(zFar + zNear) / (zFar - zNear)
        result[2,3] = -1.0
        result[3,2] = -(2.0 * zFar * zNear) / (zFar - zNear)

        self.m_currMat = result * self.m_currMat
        self.push()

class AbstractVector(object):
    def __init__(self, x=0, y=0, z=0, w=0, data=None):
        if data is not None:
            self._data = data.copy()
        else:
            self._data = numpy.matrix([[x, y, z, w]], dtype=float)

    def copy(self):
        return type(self)(data=self._data)

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    @property
    def w(self):
        return self[3]

    @w.setter
    def w(self, value):
        self[3] = value

    def tolist(self):
        return self._data.tolist()[0]

    def __getitem__(self, index):
        return self._data.item(0, index)

    def __setitem__(self, index, value):
        self._data.itemset(0, index, value)

    def __add__(self, other):
        data = numpy.add(self._data, other._data)
        return type(self)(data=data)

    def __iadd__(self, other):
        self._data = numpy.add(self._data, other._data)

    def __sub__(self, other):
        data = numpy.subtract(self._data, other._data)
        return type(self)(data=data)

    def __isub__(self, other):
        self._data = numpy.subtract(self._data, other._data)

    def __mul__(self, other):
        data = self._data * other
        return type(self)(data=data)

    def __imul__(self, other):
        if hasattr(other, '_data'):
            self._data *= other._data
        else:
            self._data *= other

    def __iter__(self):
        for item in self._data:
            yield item

class Vector(AbstractVector):
    def length(self):
        return numpy.linalg.norm(self._data)

    def normalize(self):
        self._data /= self.length()

    def normal(self):
        result = Vector()
        result._data = self._data / self.length()
        return result

    def __xor__(self, other):
        data = numpy.cross(
                [self[0], self[1], self[2]], 
                [other[0], other[1], other[2]])
        return type(self)(data[0], data[1], data[2])

    def __rxor__(self, other):
        data = numpy.cross(
                [other[0], other[1], other[2]],
                [self[0], self[1], self[2]])
        return type(self)(data[0], data[1], data[2])

class Point(AbstractVector):
    def __init__(self, x=0, y=0, z=0, w=1, data=None):
        super(Point, self).__init__(x, y, z, w, data)

    def __add__(self, other):
        result = super(Point, self).__add__(other)
        return Vector(result[0], result[1], result[2])

    def __sub__(self, other):
        result = super(Point, self).__sub__(other)
        return Vector(result[0], result[1], result[2])
