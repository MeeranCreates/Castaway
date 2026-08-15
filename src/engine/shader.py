from pathlib import Path
from OpenGL.GL import *
import glm


class Shader:
    """GLSL 4.10 program. Attribute indices are linked in Python, not shader layouts."""
    def __init__(self, vertex_file, fragment_file, attributes):
        self.program = glCreateProgram()
        for stage, filename in ((GL_VERTEX_SHADER, vertex_file), (GL_FRAGMENT_SHADER, fragment_file)):
            source = Path(filename).read_text(encoding="utf-8")
            if not source.lstrip().startswith("#version 410 core"):
                raise ValueError(f"{filename} must target #version 410 core")
            shader = glCreateShader(stage)
            glShaderSource(shader, source)
            glCompileShader(shader)
            if not glGetShaderiv(shader, GL_COMPILE_STATUS):
                raise RuntimeError(f"Shader compile error in {filename}:\n{glGetShaderInfoLog(shader).decode()}")
            glAttachShader(self.program, shader)
            glDeleteShader(shader)
        for name, index in attributes.items():
            glBindAttribLocation(self.program, index, name)
        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            raise RuntimeError(f"Program link error:\n{glGetProgramInfoLog(self.program).decode()}")

    def use(self): glUseProgram(self.program)

    def set(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        if loc < 0: return
        if isinstance(value, glm.mat4): glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(value))
        elif isinstance(value, glm.vec3): glUniform3fv(loc, 1, glm.value_ptr(value))
        elif isinstance(value, glm.vec2): glUniform2fv(loc, 1, glm.value_ptr(value))
        elif isinstance(value, int): glUniform1i(loc, value)
        else: glUniform1f(loc, float(value))

    def delete(self): glDeleteProgram(self.program)
