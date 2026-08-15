"""macOS-safe GLFW window creation and Retina framebuffer handling."""
import glfw
from OpenGL.GL import glViewport


class Window:
    def __init__(self, width=1440, height=900, title="Castaway — M1 OpenGL 4.1"):
        if not glfw.init():
            raise RuntimeError("GLFW initialization failed. Install GLFW with Homebrew.")
        # macOS exposes OpenGL through a 4.1 core, forward-compatible driver only.
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.COCOA_GRAPHICS_SWITCHING, glfw.TRUE)
        glfw.window_hint(glfw.SAMPLES, 4)
        self.handle = glfw.create_window(width, height, title, None, None)
        if not self.handle:
            glfw.terminate()
            raise RuntimeError("Could not create an OpenGL 4.1 Core context.")
        glfw.make_context_current(self.handle)
        glfw.swap_interval(1)
        glfw.set_framebuffer_size_callback(self.handle, self._on_framebuffer_resize)
        self._on_framebuffer_resize(self.handle, *glfw.get_framebuffer_size(self.handle))

    @staticmethod
    def _on_framebuffer_resize(_window, width, height):
        # Window points and framebuffer pixels differ on Retina displays.
        glViewport(0, 0, width, height)

    @property
    def framebuffer_size(self):
        return glfw.get_framebuffer_size(self.handle)

    @property
    def should_close(self):
        return glfw.window_should_close(self.handle)

    def destroy(self):
        glfw.destroy_window(self.handle)
        glfw.terminate()
