#version 410 core
in vec3 aPosition;
out float vHeight;
void main(){ vHeight=aPosition.z*.5+.5; gl_Position=vec4(aPosition.x,aPosition.z,1.,1.); }
