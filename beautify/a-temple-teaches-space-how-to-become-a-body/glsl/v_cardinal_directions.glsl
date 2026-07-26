#version 330 core
uniform vec2 iResolution;uniform float u,t,u_audioVolume,u_audioBeat;out vec4 fragColor;
#include "primitives.glsl"
#include "visionary.glsl"
#include "include/living_temple.glsl"
void main(){vec2 uv=gl_FragCoord.xy/iResolution,p=aspectUV(uv,iResolution);fragColor=vec4(renderLivingTemple(p,uv,3,u,t,u_audioVolume,u_audioBeat),1);}
