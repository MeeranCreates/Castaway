from OpenGL.GL import *
import numpy as np
import glfw


# -------------------------
# GLFW / Window
# -------------------------

glfw.init()

window = glfw.create_window(
    1200,
    720,
    "Castaway",
    None,
    None
)

glfw.make_context_current(window)


# -------------------------
# Triangle vertices
# -------------------------

vertices = [
     0.0,  0.5, 0.0,
    -0.5, -0.5, 0.0,
     0.5, -0.5, 0.0
]

vertices = np.array(vertices, dtype=np.float32)


# -------------------------
# VAO
# -------------------------

vao = glGenVertexArrays(1)
glBindVertexArray(vao)


# -------------------------
# VBO
# -------------------------

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)

glBufferData(
    GL_ARRAY_BUFFER,
    vertices.nbytes,
    vertices,
    GL_STATIC_DRAW
)


# -------------------------
# Vertex attributes
# -------------------------

glVertexAttribPointer(
    0,
    3,
    GL_FLOAT,
    GL_FALSE,
    3 * vertices.itemsize,
    None
)

glEnableVertexAttribArray(0)


# -------------------------
# Main loop
# -------------------------

while not glfw.window_should_close(window):
    glfw.poll_events()


# -------------------------
# Cleanup
# -------------------------

glDeleteBuffers(1, [vbo])
glDeleteVertexArrays(1, [vao])

glfw.terminate()