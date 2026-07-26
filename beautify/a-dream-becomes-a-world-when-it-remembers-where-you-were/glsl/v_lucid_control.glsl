#version 330 core
uniform vec2 iResolution; uniform float u,t,u_audioVolume,u_audioBeat;
out vec4 fragColor;
#include "primitives.glsl"
#include "visionary.glsl"
#include "include/dream_world.glsl"
void main(){vec2 uv=gl_FragCoord.xy/iResolution;vec2 p=aspectUV(uv,iResolution);fragColor=vec4(renderDreamWorld(p,uv,8,u,t,u_audioVolume,u_audioBeat),1.0);}
