#ifndef QUEUE_SACRED_MIRROR_GLSL
#define QUEUE_SACRED_MIRROR_GLSL

const vec3 SM_VOID=vec3(0.004,0.006,0.012);
const vec3 SM_SILVER=vec3(0.62,0.76,0.92);
const vec3 SM_GOLD=vec3(1.30,0.66,0.12);
const vec3 SM_CYAN=vec3(0.05,0.82,1.18);
const vec3 SM_VIOLET=vec3(0.68,0.12,1.15);
const vec3 SM_ROSE=vec3(1.10,0.08,0.34);
const vec3 SM_GREEN=vec3(0.06,1.00,0.52);
const vec3 SM_PEARL=vec3(0.90,0.96,1.10);

float mirrorOval(vec2 p,vec2 c,vec2 radius) {
    return length((p-c)/radius)-1.0;
}
float mirrorHeight(vec2 p,float time,float phase) {
    vec2 q=p+0.055*vec2(
        fbmWarp(p*2.4+phase,time),
        fbmWarp(p*2.4+phase+8.0,time+13.0)
    );
    return fbmWarp(q*3.2+vec2(time*0.018,-time*0.012),time+phase)
        +0.10*sin(q.x*13.0+q.y*9.0+time*0.25+phase);
}
vec3 liquidMirror(vec2 p,float time,float phase,float darkness) {
    float eps=0.006;
    float h=mirrorHeight(p,time,phase);
    float hx=mirrorHeight(p+vec2(eps,0),time,phase)-h;
    float hy=mirrorHeight(p+vec2(0,eps),time,phase)-h;
    vec3 n=normalize(vec3(-hx/eps,-hy/eps,1.75));
    vec3 view=normalize(vec3(p*0.42,-1.0));
    vec3 reflected=reflect(view,n);
    float fres=fresnelTerm(view,n,3.4);
    float band=reflected.x*0.41+reflected.y*0.29+h*0.32+phase*0.07;
    vec3 env=spectral(band+time*0.008);
    vec3 metal=mix(SM_SILVER,env,0.50+0.40*fres);
    metal+=SM_GOLD*pow(max(reflected.y,0.0),7.0)*1.2;
    metal+=SM_CYAN*pow(max(-reflected.x,0.0),9.0)*0.55;
    return mix(metal*0.42,SM_VOID,darkness)*(0.55+0.75*fres);
}
float mirrorCaustic(vec2 p,float time,float phase) {
    vec2 v=voronoi2(p*5.8+vec2(time*0.045,-time*0.025)+phase);
    float ridge=max(v.y-v.x,0.0);
    return pow(saturate(1.0-ridge*3.6),6.0);
}
void sacredSurface(inout vec3 col,vec2 p,vec2 c,vec2 radius,float time,float phase,
                   float darkness,vec3 rimHue,float energy) {
    vec2 q=(p-c)/radius;
    float d=length(q)-1.0;
    float inside=aaFill(d);
    vec3 material=liquidMirror(q,time,phase,darkness);
    float caustic=mirrorCaustic(q,time,phase);
    col=mix(col,material+rimHue*caustic*0.11,inside*energy);
    col+=rimHue*(aaStroke(d,0.018)*0.62+glow(d,0.09)*0.11)*energy;
}
float visageSDF(vec2 p) {
    float head=length(p/vec2(0.68,1.0))-0.34;
    float eyeL=length(p-vec2(-0.095,0.055))-0.026;
    float eyeR=length(p-vec2(0.095,0.055))-0.026;
    float mouth=sdSegment(p,vec2(-0.10,-0.105),vec2(0.10,-0.105))-0.012;
    return min(abs(head),min(eyeL,min(eyeR,mouth)));
}
void spectralVisage(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float energy,float phase) {
    vec2 q=(p-c)/scale;
    q.x+=0.025*sin(q.y*13.0+phase);
    float d=visageSDF(q)*scale;
    col+=hue*(aaStroke(d,0.006)*0.72+glow(d,0.042)*0.12)*energy;
}
void echoRing(inout vec3 col,vec2 p,vec2 c,float radius,float phase,vec3 hue,float energy) {
    vec2 q=p-c;
    float a=atan(q.y,q.x);
    float d=abs(length(q/vec2(1.0,0.66))-radius-0.012*sin(a*9.0+phase));
    col+=hue*(exp(-d*d/0.000025)*0.38+exp(-d*d/0.0018)*0.06)*energy;
}
void catoptricPortal(inout vec3 col,vec2 p,float time,float q,float ae) {
    vec2 kp=kaleido(p,10.0,time*0.025);
    for (int i=0;i<7;i++) {
        float fi=float(i), d=abs(length(kp)-0.10-fi*0.075);
        vec3 hue=spectral(fi*0.13+time*0.01);
        col+=hue*(glow(d,0.026)*0.095+aaStroke(d,0.005)*0.38)*q*ae;
    }
    float center=exp(-dot(p,p)/(0.018+0.045*q));
    col+=mix(SM_GOLD,SM_PEARL,center)*center*q*ae;
}
void mirrorFeedback(inout vec3 col,vec2 p,vec2 a,vec2 b,float q,float ae) {
    lightFilament(col,p,a,vec2(0.0,0.24),SM_CYAN,q*ae);
    lightFilament(col,p,vec2(0.0,0.24),b,SM_CYAN,q*ae);
    lightFilament(col,p,b,vec2(0.0,-0.26),SM_GOLD,smoothstep(0.22,0.92,q)*ae);
    lightFilament(col,p,vec2(0.0,-0.26),a,SM_GOLD,smoothstep(0.22,0.92,q)*ae);
}
vec3 mirrorBackground(vec2 uv,vec2 p,float time) {
    float smoke=fbmWarp(p*1.55+vec2(time*0.010,-time*0.006),time);
    vec3 col=mix(SM_VOID,vec3(0.025,0.035,0.075),smoke*0.72);
    col+=mix(SM_VIOLET,SM_CYAN,smoke)*pow(max(smoke-0.68,0.0),3.0)*0.12;
    float dust=step(0.997,hash21(floor((p+2.0)*310.0)));
    col+=SM_PEARL*dust*0.42;
    return col*(0.70+0.30*vignette(uv));
}
void mirrorFracture(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float energy,float seed) {
    vec2 q=(p-c)/scale;
    float angle=atan(q.y,q.x);
    for (int i=0;i<9;i++) {
        float a=TAU*hash11(float(i)+seed);
        vec2 end=vec2(cos(a),sin(a))*mix(0.30,0.95,hash11(float(i)*3.1+seed));
        lightFilament(col,q,vec2(0.0),end,hue,energy*(0.35+0.4*hash11(float(i)+7.0)));
    }
    col+=hue*pow(max(0.0,cos(angle*17.0+seed)),28.0)*exp(-length(q)*2.5)*energy*0.12;
}
vec3 renderSacredMirror(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat) {
    float q=easeInOut(progress), ae=audioEnergy(volume,beat);
    vec3 col=mirrorBackground(uv,p,time);
    if (mode==0) {
        sacredSurface(col,p,vec2(0.24,0.0),vec2(0.34,0.52),time,0.0,0.0,SM_SILVER,ae);
        spectralVisage(col,p,vec2(-0.43,-0.02),0.65,SM_PEARL,ae,0.0);
        spectralVisage(col,p,vec2(0.24,-0.02),0.65,SM_SILVER,q*ae,0.0);
        lightFilament(col,p,vec2(-0.25,0.0),vec2(-0.10,0.0),SM_CYAN,q*ae);
    } else if (mode==1) {
        sacredSurface(col,p,vec2(0.20,0.0),vec2(0.36,0.53),time,time*0.18,0.0,SM_GOLD,ae);
        spectralVisage(col,p,vec2(-0.43,-0.02),0.65,SM_PEARL,ae,time*0.30);
        spectralVisage(col,p,vec2(0.20+0.045*sin(max(time-0.9,0.0)),0.0),0.64,SM_GOLD,q*ae,time*0.30-0.8);
        echoRing(col,p,vec2(0.20),0.39,time,SM_CYAN,q*ae);
    } else if (mode==2) {
        spectralVisage(col,p,vec2(-0.58,0.0),0.62,SM_PEARL,ae,0.0);
        sacredSurface(col,p,vec2(0.58,0.0),vec2(0.25,0.42),time,2.0,0.0,SM_SILVER,q*ae);
        catoptricPortal(col,p,time,q*0.72,ae);
        mirrorFeedback(col,p,vec2(-0.48,0.0),vec2(0.48,0.0),q,ae);
    } else if (mode==3) {
        sacredSurface(col,p,vec2(0.0),vec2(0.45,0.56),time,3.0,0.0,SM_GOLD,ae);
        spectralVisage(col,p,vec2(-0.14,0.0),0.70,SM_PEARL,ae,0.3);
        spectralVisage(col,p,vec2(0.16,0.01),0.70,SM_GOLD,q*ae,1.2+time*0.12);
        lightFilament(col,p,vec2(0.14,0.02),vec2(0.62,0.31),SM_GOLD,q*ae);
    } else if (mode==4) {
        sacredSurface(col,p,vec2(0.0),vec2(0.44,0.56),time,5.0,0.15,SM_VIOLET,ae);
        for (int i=0;i<9;i++) {
            float fi=float(i), r=0.09+fi*0.055*q;
            echoRing(col,p,vec2(0.0),r,time*0.1+fi, mix(SM_SILVER,SM_VIOLET,fi/8.0),ae*(0.75-fi*0.065));
        }
        spectralVisage(col,p,vec2(0.0),0.64,SM_GOLD,q*ae*0.62,time*0.2);
    } else if (mode==5) {
        sacredSurface(col,p,vec2(0.0),vec2(0.14,0.58),time,7.0,0.35,SM_GOLD,q*ae);
        spectralVisage(col,p,vec2(-0.46,0.0),0.72,SM_PEARL,ae,0.0);
        spectralVisage(col,p,vec2(0.46,0.0),0.72,SM_VIOLET,q*ae,1.7);
        mirrorFeedback(col,p,vec2(-0.40,0.0),vec2(0.40,0.0),q,ae);
    } else if (mode==6) {
        sacredSurface(col,p,vec2(0.0),vec2(0.42,0.55),time,9.0,0.28,SM_GOLD,q*ae);
        catoptricPortal(col,p,time,q,ae);
        for (int i=0;i<4;i++) {
            float a=TAU*float(i)/4.0+time*0.04;
            radiantNode(col,p,vec2(cos(a),sin(a))*vec2(0.30,0.20),0.030,spectral(float(i)*0.24),q*ae);
        }
    } else if (mode==7) {
        sacredSurface(col,p,vec2(0.0),vec2(0.43,0.56),time,11.0,mix(0.25,0.92,q),SM_VIOLET,ae);
        float aperture=exp(-dot(p,p)/(0.024+0.016*q));
        col+=SM_GOLD*aperture*q*ae;
        for (int i=0;i<6;i++) echoRing(col,p,vec2(0.0),0.10+float(i)*0.065,time,SM_GOLD,q*ae*(0.54-float(i)*0.055));
    } else if (mode==8) {
        sacredSurface(col,p,vec2(-0.42,0.0),vec2(0.28,0.45),time,13.0,0.0,SM_ROSE,ae);
        sacredSurface(col,p,vec2(0.42,0.0),vec2(0.28,0.45),time,17.0,0.05,SM_GOLD,q*ae);
        mirrorFracture(col,p,vec2(-0.42),0.35,SM_ROSE,ae,2.0);
        lightFilament(col,p,vec2(0.42,0.0),vec2(0.08,-0.27),SM_GREEN,q*ae);
    } else if (mode==9) {
        for (int i=0;i<3;i++) {
            vec2 c=vec2(mix(-0.52,0.52,float(i)/2.0),0.0);
            sacredSurface(col,p,c,vec2(0.20,0.34),time,20.0+float(i),0.30, i==1?SM_VIOLET:SM_ROSE,q*ae);
            mirrorFracture(col,p,c,0.22,SM_ROSE,q*ae,float(i)*5.0);
        }
    } else if (mode==10) {
        for (int i=0;i<4;i++) {
            float fi=float(i), y=mix(-0.43,0.43,fi/3.0);
            sacredSurface(col,p,vec2(0.0,y),vec2(0.15,0.095),time,fi*3.0,0.15,mix(SM_GOLD,SM_VIOLET,fi/3.0),q*ae);
            if (i>0) lightFilament(col,p,vec2(0.0,mix(-0.43,0.43,(fi-1.0)/3.0)+0.09),vec2(0.0,y-0.09),SM_GOLD,q*ae);
        }
    } else if (mode==11) {
        catoptricPortal(col,p,time,q,ae);
        for (int i=0;i<24;i++) {
            float fi=float(i), a=TAU*hash11(fi*2.7)+time*0.02;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.55,0.34)*(0.25+0.75*hash11(fi+5.0))*q;
            radiantNode(col,p,c,0.019,spectral(fi/24.0),q*ae);
        }
    } else if (mode==12) {
        sacredSurface(col,p,vec2(0.42,0.0),vec2(0.29,0.46),time,23.0,0.05,SM_GOLD,q*ae);
        spectralVisage(col,p,vec2(-0.45,0.0),0.70,SM_PEARL,ae,0.0);
        mirrorFeedback(col,p,vec2(-0.38,0.0),vec2(0.34,0.0),q,ae);
        radiantNode(col,p,vec2(0.0,-0.24),0.050,SM_GOLD,q*ae);
    } else if (mode==13) {
        float physical=exp(-dot(p-vec2(-0.42,0.0),p-vec2(-0.42,0.0))/0.035);
        col+=SM_GOLD*physical*ae;
        sacredSurface(col,p,vec2(0.42,0.0),vec2(0.28,0.46),time,29.0,0.08,SM_VIOLET,q*ae);
        catoptricPortal(col,p-vec2(0.42,0.0),time,q,ae*0.52);
        lightFilament(col,p,vec2(0.0,-0.52),vec2(0.0,0.52),SM_ROSE,q*ae);
    } else if (mode==14) {
        sacredSurface(col,p,vec2(0.0),vec2(0.42,0.55),time,31.0,0.04,SM_GOLD,q*ae);
        spectralVisage(col,p,vec2(0.0),0.75,SM_PEARL,q*ae,time*0.1);
        for (int i=0;i<5;i++) {
            float a=TAU*float(i)/5.0+0.5;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.61,0.38);
            lightFilament(col,p,vec2(0.0),c,spectral(float(i)/5.0),q*ae*0.58);
        }
    } else if (mode==15) {
        sacredSurface(col,p,vec2(-0.52,0.0),vec2(0.22,0.37),time,33.0,0.08,SM_GOLD,q*ae);
        for (int i=0;i<4;i++) {
            float a=TAU*float(i)/4.0+0.35;
            vec2 c=vec2(0.32,0.0)+vec2(cos(a),sin(a))*vec2(0.36,0.28);
            radiantNode(col,p,c,0.052,spectral(float(i)*0.23),q*ae);
            lightFilament(col,p,vec2(-0.32,0.0),c,spectral(float(i)*0.23),q*ae*0.72);
        }
    } else if (mode==16) {
        sacredSurface(col,p,vec2(-0.60,0.0),vec2(0.18,0.32),time,35.0,0.12,SM_GOLD,ae);
        for (int i=0;i<13;i++) {
            float fi=float(i), x=mix(-0.22,0.82,fi/12.0);
            float y=-0.23+0.08*sin(fi*1.4+time*0.12);
            if (i>0) {
                float fp=float(i-1), xp=mix(-0.22,0.82,fp/12.0);
                float yp=-0.23+0.08*sin(fp*1.4+time*0.12);
                lightFilament(col,p,vec2(xp,yp),vec2(x,y),SM_GREEN,q*ae);
            }
            radiantNode(col,p,vec2(x,y),0.017,SM_GREEN,q*ae);
        }
    } else {
        sacredSurface(col,p,vec2(0.16,0.0),vec2(mix(0.22,0.43,q),mix(0.34,0.56,q)),time,40.0,0.06,SM_GOLD,ae);
        spectralVisage(col,p,vec2(-0.56,0.0),0.68,SM_PEARL,ae,0.0);
        spectralVisage(col,p,vec2(0.16,0.0),mix(0.22,0.72,q),SM_GOLD,q*ae,1.8+time*0.12);
        mirrorFeedback(col,p,vec2(-0.46,0.0),vec2(0.08,0.0),q,ae);
        for (int i=0;i<7;i++) echoRing(col,p,vec2(0.16),0.12+float(i)*0.072,time+float(i),spectral(float(i)/7.0),q*ae*(0.60-float(i)*0.055));
    }
    col+=SM_GOLD*lensFlare(p,vec2(0.52,0.38))*0.011*q*ae;
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
