#version 330 core
#define NAV_MODE 13
uniform vec2 iResolution;uniform float u,t,u_audioVolume,u_audioBeat;out vec4 fragColor;
#include "include/navigation_atlas.glsl"
