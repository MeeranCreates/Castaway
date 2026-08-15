#version 410 core
in vec2 vUV;
uniform sampler2D uHdr;
uniform sampler2D uDepth;
uniform float uExposure;
uniform vec3 uFogColor;
out vec4 fragColor;
void main(){ vec3 hdr=texture(uHdr,vUV).rgb; float depth=texture(uDepth,vUV).r; float fog=smoothstep(.84,.998,depth)*.16; hdr=mix(hdr,uFogColor,fog); vec3 mapped=vec3(1.)-exp(-hdr*uExposure); mapped=pow(mapped,vec3(1./2.2)); fragColor=vec4(mapped,1.); }
