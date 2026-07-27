#version 330 core
uniform vec2 iResolution;
uniform float u;
uniform float t;
uniform float u_audioVolume;
uniform float u_audioBeat;
uniform vec4 u_stateA;
uniform vec2 u_stateB;
uniform float u_stage;
uniform float u_local;
uniform float u_tattva;
out vec4 fragColor;

#include "primitives.glsl"
#include "visionary.glsl"
#include "cinema.glsl"
#include "signature.glsl"
#include "phononic_film.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution.xy;
    vec2 p=aspectUV(uv,iResolution);
    MeaningState state=meaningState(
        u_stateA,
        u_stateB,
        u_tattva,
        u_audioVolume,
        u_audioBeat
    );
    vec3 color=renderPhononicFilm(
        p,
        uv,
        gl_FragCoord.xy,
        t,
        u,
        int(floor(u_stage+0.5)),
        u_local,
        state
    );
    fragColor=vec4(color,1.0);
}
