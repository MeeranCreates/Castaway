#version 410 core
in vec3 aPosition;
in vec3 aNormal;
in vec2 aUV;
in vec4 aInstance0, aInstance1, aInstance2, aInstance3;
uniform mat4 uView, uProjection;
uniform float uTime;
out float vLight;
out float vVariation;
void main(){ mat4 model=mat4(aInstance0,aInstance1,aInstance2,aInstance3); vec3 p=aPosition; p.x+=sin(uTime*2.+model[3].x*.21+model[3].z*.13)*p.y*.16; vec4 w=model*vec4(p,1.); vLight=.55+.45*max(dot(vec3(0,1,0),normalize(vec3(.45,.75,-.35))),0.); vVariation=fract(sin(dot(model[3].xz,vec2(12.9898,78.233)))*43758.5453); gl_Position=uProjection*uView*w; }
