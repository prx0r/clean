#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack03_bioluminescent.glsl"

float heartSdf(vec2 p) {
    p.x=abs(p.x);
    p.y+=0.12;
    float a=atan(p.x,p.y)/PI;
    float r=length(p);
    float h=abs(a);
    return r-(0.26-0.15*h+0.05*sin(h*PI));
}

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=gutBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    vec2 heart=vec2(0.0,-0.34), gut=vec2(0.0,0.46);
    float hd=heartSdf((p-heart)*vec2(1.5,1.2));
    col+=GUT_RED*(aaFill(hd)*0.17+aaStroke(hd,0.008)*0.68+glow(hd,0.10)*0.20)*ae;
    float beatRing=sdCircle(p-heart,0.19+0.025*u_audioBeat);
    col+=GUT_RED*glow(beatRing,0.024)*0.22*ae;
    gutTube(col,p-gut,0.44,0.11,t,0.2,ae);
    gutVagus(col,p,heart+vec2(0.0,0.15),gut-vec2(0.0,0.10),t,GUT_AMBER,q*ae);
    float travel=easeInOut(smoothstep(0.14,0.94,u));
    vec2 s=mix(gut-vec2(0.0,0.08),heart+vec2(0.0,0.14),travel);
    s.x+=0.03*sin(travel*TAU*3.0+t)*sin(PI*travel);
    gutSignal(col,p,s,0.032,mix(GUT_AMBER,GUT_RED,travel),q*ae);
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
