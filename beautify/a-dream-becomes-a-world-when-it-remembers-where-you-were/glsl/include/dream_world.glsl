#ifndef QUEUE_DREAM_WORLD_GLSL
#define QUEUE_DREAM_WORLD_GLSL

const vec3 DW_VOID=vec3(0.008,0.010,0.035);
const vec3 DW_INK=vec3(0.035,0.055,0.110);
const vec3 DW_BLUE=vec3(0.060,0.440,1.050);
const vec3 DW_VIOLET=vec3(0.580,0.180,1.120);
const vec3 DW_GOLD=vec3(1.280,0.650,0.130);
const vec3 DW_MINT=vec3(0.100,1.000,0.690);
const vec3 DW_ROSE=vec3(1.050,0.170,0.420);
const vec3 DW_PEARL=vec3(0.800,0.920,1.100);

vec3 dreamSky(vec2 uv,vec2 p,float time) {
    float mist=fbmWarp(p*1.18+vec2(time*0.013,-time*0.009),time);
    float cloud=fbmWarp(p*2.45+vec2(-time*0.019,time*0.006),time+19.0);
    vec3 col=mix(DW_VOID,DW_INK,0.42+0.42*mist);
    col+=mix(DW_VIOLET,DW_BLUE,cloud)*pow(max(cloud-0.56,0.0),2.6)*0.22;
    float horizon=exp(-pow((p.y+0.29+0.05*mist)/0.17,2.0));
    col+=mix(DW_GOLD,DW_ROSE,cloud)*horizon*0.075;
    float stars=step(0.996,hash21(floor((p+3.0)*260.0)));
    col+=DW_PEARL*stars*(0.25+0.75*hash21(floor(p*260.0)+9.0));
    return col*(0.72+0.28*vignette(uv));
}
float dreamPathDistance(vec2 p,float phase,float time,float reveal) {
    float best=10.0;
    vec2 previous=vec2(-0.88,-0.20+0.06*sin(phase-time*0.08));
    for (int i=1;i<72;i++) {
        float s=float(i)/71.0;
        float x=mix(-0.88,0.88,s);
        float y=-0.20+0.10*sin(s*TAU*1.45+phase+time*0.11)
            +0.026*sin(s*TAU*4.2-phase-time*0.08);
        vec2 current=vec2(x,y);
        if (s<reveal+0.025) best=min(best,sdSegment(p,previous,current));
        previous=current;
    }
    return best;
}
void dreamPath(inout vec3 col,vec2 p,float phase,float time,float reveal,vec3 hue,float energy) {
    float d=dreamPathDistance(p,phase,time,reveal);
    float broken=0.60+0.40*noise21(p*53.0+vec2(time*0.04,phase));
    col+=hue*(exp(-d*d/0.000020)*0.75+exp(-d*d/0.0022)*0.105)*broken*energy;
}
float landmarkSDF(vec2 p,int kind) {
    if (kind==0) {
        float trunk=sdRoundBox(p-vec2(0.0,-0.045),vec2(0.025,0.13),0.012);
        float crown=sdCircle(p-vec2(0.0,0.105),0.115);
        crown=smoothUnion(crown,sdCircle(p-vec2(-0.075,0.075),0.075),0.045);
        crown=smoothUnion(crown,sdCircle(p-vec2(0.082,0.070),0.082),0.045);
        return min(trunk,crown);
    }
    if (kind==1) {
        float deck=sdRoundBox(p-vec2(0.0,-0.035),vec2(0.17,0.018),0.01);
        float arch=abs(length((p-vec2(0.0,-0.055))/vec2(1.0,0.62))-0.15)-0.012;
        return min(deck,arch);
    }
    if (kind==2) {
        float body=sdRoundBox(p-vec2(0.0,0.02),vec2(0.065,0.18),0.014);
        float roof=sdSegment(p,vec2(-0.10,0.20),vec2(0.0,0.31));
        roof=min(roof,sdSegment(p,vec2(0.0,0.31),vec2(0.10,0.20)))-0.014;
        return min(body,roof);
    }
    float posts=min(sdRoundBox(p-vec2(-0.10,0.02),vec2(0.022,0.20),0.008),
                    sdRoundBox(p-vec2(0.10,0.02),vec2(0.022,0.20),0.008));
    float lintel=sdRoundBox(p-vec2(0.0,0.20),vec2(0.125,0.022),0.008);
    return min(posts,lintel);
}
void paintLandmark(inout vec3 col,vec2 p,vec2 c,float scale,int kind,vec3 hue,float energy) {
    float d=landmarkSDF((p-c)/scale,kind)*scale;
    float fill=aaFill(d);
    float rim=aaStroke(d,0.005);
    col=mix(col,col+hue*0.11,fill*energy);
    col+=hue*(rim*0.72+glow(d,0.045)*0.11)*energy;
}
void memoryContour(inout vec3 col,vec2 p,vec2 c,float radius,vec3 hue,float energy,float time) {
    vec2 q=p-c;
    float angle=atan(q.y,q.x);
    float rough=0.018*sin(angle*9.0+time*0.12)+0.010*noise21(vec2(angle*3.0,time*0.03));
    float d=abs(length(q/vec2(1.0,0.62))-radius-rough);
    col+=hue*(exp(-d*d/0.000030)*0.35+exp(-d*d/0.0016)*0.055)*energy;
}
void cartography(inout vec3 col,vec2 p,float energy,float time) {
    vec2 warped=p+0.025*vec2(fbm(p*4.0+time*0.01),fbm(p*4.0-time*0.01));
    vec2 grid=abs(fract((warped+1.4)*8.0)-0.5);
    float fine=1.0-smoothstep(0.47,0.49,min(grid.x,grid.y));
    float topo=pow(0.5+0.5*cos(fbmWarp(p*3.1,time)*74.0),18.0);
    col+=DW_BLUE*fine*energy*0.030+DW_GOLD*topo*energy*0.042;
}
void memoryCity(inout vec3 col,vec2 p,float reveal,float energy,float time) {
    for (int i=0;i<17;i++) {
        float fi=float(i), x=mix(-0.86,0.86,fi/16.0);
        float h=(0.08+0.34*hash11(fi*4.17))*reveal;
        float w=0.025+0.030*hash11(fi+8.0);
        float d=sdRoundBox(p-vec2(x,-0.28+h*0.5),vec2(w,h*0.5),0.006);
        float windows=step(0.79,noise21(floor((p-vec2(x,-0.28))*vec2(95.0,55.0))+fi));
        col+=mix(DW_VIOLET,DW_GOLD,hash11(fi))*glow(d,0.020)*0.055*energy;
        col+=DW_PEARL*aaFill(d)*windows*0.12*energy;
    }
    float haze=exp(-pow((p.y+0.29)/0.12,2.0))*fbm(p*7.0+time*0.02);
    col+=DW_GOLD*haze*0.035*energy;
}
void orbitField(inout vec3 col,vec2 p,vec2 c,float radius,float squash,vec3 hue,float energy,float time) {
    vec2 q=(p-c)/vec2(1.0,squash);
    float d=abs(length(q)-radius-0.008*sin(atan(q.y,q.x)*11.0+time*0.1));
    col+=hue*(exp(-d*d/0.000020)*0.38+exp(-d*d/0.0020)*0.065)*energy;
}
void answerLoop(inout vec3 col,vec2 p,vec2 a,vec2 b,float q,float ae) {
    lightFilament(col,p,a,vec2(0.0,0.22),DW_BLUE,q*ae);
    lightFilament(col,p,vec2(0.0,0.22),b,DW_BLUE,q*ae);
    lightFilament(col,p,b,vec2(0.0,-0.27),DW_GOLD,smoothstep(0.24,0.92,q)*ae);
    lightFilament(col,p,vec2(0.0,-0.27),a,DW_GOLD,smoothstep(0.24,0.92,q)*ae);
    radiantNode(col,p,a,0.045,DW_MINT,ae);
    radiantNode(col,p,b,0.045,DW_GOLD,ae);
}
vec3 renderDreamWorld(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat) {
    float q=easeInOut(progress), ae=audioEnergy(volume,beat);
    vec3 col=dreamSky(uv,p,time);
    float fog=fbmWarp(p*2.2+vec2(time*0.009,0.0),time);
    col+=mix(DW_BLUE,DW_VIOLET,fog)*pow(max(fog-0.60,0.0),3.0)*0.08;

    if (mode==0) {
        dreamPath(col,p,0.2,time,q,DW_PEARL,ae*(1.0-smoothstep(0.70,1.0,progress)*0.58));
        float erasure=smoothstep(0.55,0.98,progress)*fbmWarp(p*5.0,time);
        col=mix(col,DW_VOID,erasure*0.34);
    } else if (mode==1) {
        dreamPath(col,p,0.5,time,q,DW_BLUE,ae);
        paintLandmark(col,p,vec2(0.24,-0.02),mix(0.10,0.68,q),2,DW_GOLD,q*ae);
        for (int i=0;i<6;i++) memoryContour(col,p,vec2(0.24,-0.02),0.12+float(i)*0.085,DW_GOLD,q*ae*(0.62-float(i)*0.07),time);
    } else if (mode==2) {
        cartography(col,p,q,time);
        dreamPath(col,p,0.7,time,q,DW_BLUE,ae);
        paintLandmark(col,p,vec2(-0.48,-0.03),0.65,0,DW_MINT,q*ae);
        paintLandmark(col,p,vec2(-0.13,-0.08),0.70,1,DW_VIOLET,q*ae);
        paintLandmark(col,p,vec2(0.30,-0.02),0.64,2,DW_GOLD,q*ae);
        paintLandmark(col,p,vec2(0.63,-0.05),0.62,3,DW_BLUE,q*ae);
    } else if (mode==3) {
        vec2 left=vec2(-0.60,-0.02), right=vec2(0.60,-0.02);
        for (int i=0;i<8;i++) orbitField(col,p,vec2(0.0),0.10+float(i)*0.055,0.68,mix(DW_BLUE,DW_VIOLET,float(i)/7.0),q*ae, time);
        answerLoop(col,p,left,right,q,ae);
        float lens=glow(sdVesica(p,0.56,0.24),0.055);
        col+=mix(DW_GOLD,DW_BLUE,fog)*lens*q*0.17*ae;
    } else if (mode==4) {
        for (int i=0;i<4;i++) {
            vec2 c=vec2(mix(-0.60,0.60,float(i)/3.0),0.0);
            vec2 lp=(p-c)*rot(time*0.03*float(i+1));
            float law=abs(length(lp)-0.15-0.030*sin(atan(lp.y,lp.x)*float(3+i)+time*0.2));
            col+=spectral(float(i)*0.21)*(glow(law,0.030)*0.16+aaStroke(law,0.006)*0.55)*q*ae;
            radiantNode(col,p,c,0.040,spectral(float(i)*0.21),q*ae);
        }
    } else if (mode==5) {
        answerLoop(col,p,vec2(-0.50,-0.04),vec2(0.50,-0.04),q,ae);
        paintLandmark(col,p,vec2(0.0,-0.02),0.38,3,DW_GOLD,smoothstep(0.48,0.90,q)*ae);
        radiantNode(col,p,vec2(0.0,-0.02),0.070,DW_PEARL,smoothstep(0.5,0.9,q)*ae);
    } else if (mode==6) {
        vec2 kp=kaleido(p*vec2(1.0,1.4),8.0,time*0.018);
        float gate=abs(sdRoundBox(kp,vec2(0.13,0.62),0.055));
        col+=mix(DW_VIOLET,DW_GOLD,fog)*(glow(gate,0.055)*0.16+aaStroke(gate,0.009)*0.68)*q*ae;
        cartography(col,p-vec2(-0.45,0.0),q*0.45,time);
        memoryCity(col,p-vec2(0.46,0.0),q,0.65*ae,time);
    } else if (mode==7) {
        memoryCity(col,p,q,ae,time);
        for (int i=0;i<7;i++) memoryContour(col,p,vec2(0.24,-0.08),0.13+float(i)*0.075,mix(DW_VIOLET,DW_GOLD,float(i)/6.0),q*ae*0.48,time);
        paintLandmark(col,p,vec2(0.25,-0.04),0.72,2,DW_GOLD,q*ae);
    } else if (mode==8) {
        cartography(col,p,q,time);
        vec2 hand=vec2(-0.60,-0.06);
        radiantNode(col,p,hand,0.055,DW_PEARL,ae);
        for (int i=0;i<4;i++) {
            float fi=float(i);
            vec2 c=vec2(-0.12+fi*0.25,0.08*sin(fi*2.0+time*0.2));
            paintLandmark(col,p,c,0.43+0.06*fi,i,DW_MINT,q*ae);
            lightFilament(col,p,hand,c,DW_BLUE,q*ae*0.62);
        }
    } else if (mode==9) {
        vec2 a=vec2(-0.65,-0.05), wall=vec2(0.34,-0.02);
        lightFilament(col,p,a,vec2(-0.05,0.22),DW_ROSE,q*ae);
        lightFilament(col,p,vec2(-0.05,0.22),wall,DW_ROSE,q*ae);
        lightFilament(col,p,wall,vec2(0.02,-0.26),DW_GOLD,smoothstep(0.32,0.95,q)*ae);
        lightFilament(col,p,vec2(0.02,-0.26),a,DW_GOLD,smoothstep(0.32,0.95,q)*ae);
        paintLandmark(col,p,wall,0.72,3,DW_GOLD,q*ae);
    } else if (mode==10) {
        for (int i=0;i<3;i++) {
            vec2 c=vec2(mix(-0.52,0.52,float(i)/2.0),0.0);
            float bubble=abs(length(p-c)-0.17);
            float crack=abs(sin((p.x-c.x)*23.0+(p.y-c.y)*17.0+float(i)))*0.015;
            vec3 hue=i==0?DW_ROSE:(i==1?DW_VIOLET:DW_GOLD);
            col+=hue*(glow(bubble,0.035)*0.10+aaStroke(bubble+crack,0.007)*0.55)*q*ae;
            lightFilament(col,p,c-vec2(0.15,0.14),c+vec2(0.15,-0.14),DW_ROSE,q*ae);
        }
    } else if (mode==11) {
        for (int i=0;i<26;i++) {
            float fi=float(i), a=TAU*hash11(fi*3.1)+time*0.025;
            float r=(0.08+0.64*hash11(fi+11.0))*q;
            vec2 c=vec2(cos(a),sin(a)*0.62)*r;
            radiantNode(col,p,c,0.018+0.014*beat,spectral(fi/26.0),q*ae);
            lightFilament(col,p,vec2(0.0),c,spectral(fi/26.0),q*ae*0.18);
        }
        radiantNode(col,p,vec2(0.0),0.070,DW_GOLD,q*ae);
    } else if (mode==12) {
        answerLoop(col,p,vec2(-0.52,-0.04),vec2(0.52,-0.04),q,ae);
        for (int i=0;i<7;i++) memoryContour(col,p,vec2(0.0),0.10+float(i)*0.072,DW_GOLD,q*ae*(0.66-float(i)*0.065),time);
    } else if (mode==13) {
        vec3 dawn=mix(vec3(0.05,0.08,0.12),vec3(0.36,0.55,0.70),smoothstep(-0.3,0.45,p.y));
        col=mix(col,dawn,0.28*q);
        cartography(col,p,q*0.65,time);
        dreamPath(col,p,1.4,time,q,DW_MINT,ae);
        memoryCity(col,p,q,0.42*ae,time);
    } else {
        cartography(col,p,q*0.65,time);
        memoryCity(col,p,q,0.68*ae,time);
        dreamPath(col,p,0.7,time,q,DW_MINT,ae);
        paintLandmark(col,p,vec2(-0.48,-0.03),0.65,0,DW_MINT,q*ae);
        paintLandmark(col,p,vec2(-0.13,-0.08),0.70,1,DW_VIOLET,q*ae);
        paintLandmark(col,p,vec2(0.30,-0.02),0.64,2,DW_GOLD,q*ae);
        paintLandmark(col,p,vec2(0.63,-0.05),0.62,3,DW_BLUE,q*ae);
        radiantNode(col,p,vec2(0.30,0.18),0.070,DW_GOLD,q*ae*(0.8+beat));
    }
    col+=DW_GOLD*lensFlare(p,vec2(0.55,0.38))*0.012*q*ae;
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
