#version 410 core
in vec3 vWorldPos;
in vec3 vNormal;
in vec4 vLightPos;
uniform sampler2D uShadowMap;
uniform vec3 uColor, uCameraPos, uSunDirection, uAmbientSky;
out vec4 fragColor;
float shadow(vec4 lightPos, vec3 n){ vec3 p=lightPos.xyz/lightPos.w*.5+.5; if(p.z>1.) return 0.; float bias=max(.002*(1.-dot(n,-uSunDirection)),.0005), result=0.; vec2 texel=1./vec2(textureSize(uShadowMap,0)); for(int x=-1;x<=1;x++) for(int y=-1;y<=1;y++) result+=p.z-bias>texture(uShadowMap,p.xy+vec2(x,y)*texel).r?1.:0.; return result/9.; }
void main(){ vec3 N=normalize(vNormal), L=normalize(-uSunDirection), V=normalize(uCameraPos-vWorldPos), H=normalize(L+V); float diffuse=max(dot(N,L),0.), spec=pow(max(dot(N,H),0.),48.)*.17; vec3 color=uColor*(uAmbientSky*.58+diffuse*(1.-shadow(vLightPos,N)))+spec; fragColor=vec4(color,1.); }
