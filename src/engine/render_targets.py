from OpenGL.GL import *


class ShadowMap:
    def __init__(self, size=2048):
        self.size = size
        self.texture = glGenTextures(1); self.fbo = glGenFramebuffers(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, size, size, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1., 1., 1., 1.])
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo); glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.texture, 0)
        glDrawBuffer(GL_NONE); glReadBuffer(GL_NONE)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE: raise RuntimeError("Shadow FBO incomplete")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def begin(self): glViewport(0, 0, self.size, self.size); glBindFramebuffer(GL_FRAMEBUFFER, self.fbo); glClear(GL_DEPTH_BUFFER_BIT)


class HdrTarget:
    def __init__(self, width, height): self.fbo = None; self.resize(width, height)
    def resize(self, width, height):
        if self.fbo: glDeleteFramebuffers(1, [self.fbo]); glDeleteTextures([self.color, self.depth])
        self.width, self.height = width, height; self.fbo, self.color, self.depth = glGenFramebuffers(1), glGenTextures(1), glGenTextures(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glBindTexture(GL_TEXTURE_2D, self.color); glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, width, height, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color, 0)
        glBindTexture(GL_TEXTURE_2D, self.depth); glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, width, height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth, 0)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE: raise RuntimeError("HDR FBO incomplete")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
