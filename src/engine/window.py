import glfw

glfw.init()

window = glfw.create_window(1200,720,"Castaway",None,None)

glfw.make_context_current(window)

while not glfw.window_should_close(window):
    glfw.poll_events()

glfw.terminate()