#version 410 core
in float vHeight;
out vec4 fragColor;
void main(){ float h=clamp(vHeight,0.,1.); vec3 low=vec3(.89,.66,.43), horizon=vec3(.35,.53,.70), zenith=vec3(.055,.16,.34); vec3 color=mix(low,horizon,smoothstep(0.,.45,h)); color=mix(color,zenith,smoothstep(.45,1.,h)); fragColor=vec4(color,1.); }
