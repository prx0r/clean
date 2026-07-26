#version 330 core
uniform vec2 iResolution;
uniform float u, t, u_audioVolume, u_audioBeat;
out vec4 fragColor;
#include "../include/primitives.glsl"
#include "../include/pack03_bioluminescent.glsl"

void main() {
    vec2 uv=gl_FragCoord.xy/iResolution, p=aspectUV(uv,iResolution);
    vec3 col=gutBackground(uv,p,t);
    float q=easeInOut(u), ae=audioEnergy(u_audioVolume,u_audioBeat);
    vec2 left=vec2(-0.44,0.0), right=vec2(0.44,0.0);
    float l=sdEllipse(p-left,vec2(0.24,0.18));
    float r=sdEllipse(p-right,vec2(0.24,0.18));
    col+=GUT_BLUE*(aaFill(l)*0.12+aaStroke(l,0.009)*0.62+glow(l,0.08)*0.12)*q*ae;
    col+=GUT_CYAN*(aaFill(r)*0.12+aaStroke(r,0.009)*0.62+glow(r,0.08)*0.12)*q*ae;
    gutVagus(col,p,left+vec2(0.20,0.0),right-vec2(0.20,0.0),t,GUT_AMBER,q*ae);
    for (int i=0;i<10;i++) {
        float a=TAU*float(i)/10.0+t*0.13;
        vec2 a0=left+vec2(cos(a),sin(a))*vec2(0.20,0.14);
        vec2 b0=right+vec2(cos(a+PI*0.5),sin(a+PI*0.5))*vec2(0.20,0.14);
        float connect=smoothstep(0.36,0.88,u);
        gutNerve(col,p,a0,b0,mix(GUT_BLUE,GUT_CYAN,float(i)/10.0),connect*0.27*ae);
    }
    float travel=fract(t*0.18);
    gutSignal(col,p,mix(left,right,travel),0.026,GUT_AMBER,q*ae);
    fragColor=vec4(gutFinish(col,uv,gl_FragCoord.xy,t),1.0);
}
