#version 330 core
uniform vec2 iResolution;uniform float u,t,u_audioVolume,u_audioBeat;out vec4 fragColor;
#include "primitives.glsl"
#include "visionary.glsl"
#include "cinema.glsl"
#include "include/perceptual_crystal.glsl"
void main(){vec2 uv=gl_FragCoord.xy/iResolution,p=aspectUV(uv,iResolution);fragColor=vec4(renderPerceptualCrystal(p,uv,12,u,t,u_audioVolume,u_audioBeat),1);}
