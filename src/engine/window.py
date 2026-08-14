import glfw
from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT
import sys

def main():
    # 1. Initialize GLFW
    if not glfw.init():
        print("Failed to initialize GLFW", file=sys.stderr)
        return


    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)


    window = glfw.create_window(1200, 800, "Castaway", None, None)
    if not window:
        print("Failed to create GLFW window", file=sys.stderr)
        glfw.terminate()
        return


    glfw.make_context_current(window)

    while not glfw.window_should_close(window):

        glClear(GL_COLOR_BUFFER_BIT)

        glfw.swap_buffers(window)

        glfw.poll_events()

    # 6. Clean up and exit
    glfw.terminate()

if __name__ == "__main__":
    main()
