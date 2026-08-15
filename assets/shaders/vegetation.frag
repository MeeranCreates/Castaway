#version 410 core
in float vLight;
in float vVariation;
out vec4 fragColor;
void main(){ vec3 dry=vec3(.18,.30,.045), fresh=vec3(.035,.32,.055); fragColor=vec4(mix(fresh,dry,vVariation)*vLight,1.); }
