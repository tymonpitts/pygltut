# import sys
# tut_name = sys.argv[1]
# exec 'import %s as tut_mod' % tut_name
# tut = tut_mod.Tutorial()
# tut.run()

# import tut_02_playing_with_colors as tut_name
# import tut_04_objects_at_rest as tut_name
# import tut_05_objects_in_depth as tut_name
# import tut_06_objects_in_motion as tut_name
import tut_07_world_in_motion as tut_name
tut = tut_name.Tutorial()
tut.run()




# import glfw
 
# from OpenGL.GL import *
 
# glfw.Init()
 
# glfw.OpenWindowHint( glfw.OPENGL_VERSION_MAJOR, 3);
# glfw.OpenWindowHint( glfw.OPENGL_VERSION_MINOR, 2)
# glfw.OpenWindowHint( glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
# glfw.OpenWindowHint( glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
 
# glfw.OpenWindow(
#     800, 600,
#     8, 8, 8,
#     8, 24, 0,
#     glfw.WINDOW
#     )
 
# glfw.SetWindowTitle( "GLFW" )
 
# def draw():
#     glClearColor( 0.5, 0.5, 0.5, 1.0 )
#     glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
 
 
# print glGetString( GL_VERSION )
 
# while glfw.GetWindowParam( glfw.OPENED ):
#     if glfw.GetKey(glfw.KEY_ESC) == glfw.GLFW_PRESS:
#         break

#     draw()
    
#     glfw.SwapBuffers()

# glfw.Terminate()

