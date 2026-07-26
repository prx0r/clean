#ifndef QUEUE_CYMATIC_NAME_GLSL
#define QUEUE_CYMATIC_NAME_GLSL

const vec3 CN_VOID=vec3(0.007,0.004,0.018);
const vec3 CN_INK=vec3(0.030,0.018,0.075);
const vec3 CN_MAGENTA=vec3(1.18,0.08,0.62);
const vec3 CN_CYAN=vec3(0.02,0.92,1.20);
const vec3 CN_GOLD=vec3(1.30,0.64,0.08);
const vec3 CN_VIOLET=vec3(0.48,0.12,1.22);
const vec3 CN_GREEN=vec3(0.05,1.10,0.56);
const vec3 CN_PEARL=vec3(0.92,0.96,1.12);
const vec3 CN_SILVER=vec3(0.50,0.66,0.86);

vec3 phononicBackground(vec2 uv,vec2 p,float time) {
    float aurora=fbmWarp(p*1.55+vec2(time*0.012,-time*0.008),time);
    float veil=fbmWarp(p*3.0+vec2(-time*0.016,time*0.006),time+31.0);
    vec3 col=mix(CN_VOID,CN_INK,0.38+0.44*aurora);
    col+=mix(CN_MAGENTA,CN_CYAN,veil)*pow(max(veil-0.62,0.0),3.0)*0.17;
    float specks=step(0.997,hash21(floor((p+2.0)*290.0)));
    col+=CN_PEARL*specks*(0.15+0.65*hash21(floor(p*290.0)+5.0));
    return col*(0.68+0.32*vignette(uv));
}
float cymaticField(vec2 p,float frequency,float phase) {
    vec2 f1=vec2(-0.28,0.0),f2=vec2(0.28,0.0);
    float a=sin(length(p-f1)*frequency-phase);
    float b=sin(length(p-f2)*frequency+phase*0.87);
    float c=sin((p.x*0.72+p.y)*frequency*0.62-phase*0.43);
    return abs((a+b+c)/3.0);
}
float calligraphicGlyph(vec2 p,float seed,float pulseAmount) {
    vec2 q=kaleido(p,5.0+mod(seed,5.0),seed*0.13);
    float radius=length(q);
    float angle=atan(q.y,q.x);
    float ring=abs(radius-(0.22+0.018*sin(angle*7.0+seed)+pulseAmount))-0.012;
    float stem=sdSegment(q,vec2(0.0,-0.31),vec2(0.0,0.31))-0.013;
    float arm=sdSegment(q,vec2(0.0,0.04),vec2(0.24,0.16))-0.012;
    float seedDot=length(q-vec2(0.09,-0.09))-0.034;
    return min(min(ring,stem),min(arm,seedDot));
}
void livingGlyph(inout vec3 col,vec2 p,vec2 c,float scale,float seed,vec3 hue,float energy,float beat,float time) {
    vec2 q=(p-c)/scale;
    q+=0.018*vec2(
        fbm(q*5.0+vec2(time*0.04,seed)),
        fbm(q*5.0+vec2(seed,time*0.03))
    );
    float d=calligraphicGlyph(q,seed,0.018*beat*sin(time*0.8+seed))*scale;
    float ink=0.72+0.28*noise21(q*38.0+seed);
    col+=hue*(aaStroke(d,0.006)*0.76+glow(d,0.045)*0.12)*ink*energy;
    col+=spectral(seed*0.071+time*0.01)*glow(d+0.010,0.025)*0.045*energy;
}
void breathRibbon(inout vec3 col,vec2 p,float y,float phase,float reveal,vec3 hue,float energy,float volume) {
    vec2 previous=vec2(-0.88,y);
    for (int i=1;i<84;i++) {
        float s=float(i)/83.0, x=mix(-0.88,0.88,s);
        float envelope=sin(PI*s);
        float yy=y+envelope*(0.075+0.055*volume)*sin(s*TAU*2.2+phase)
            +0.018*sin(s*TAU*8.0-phase);
        vec2 current=vec2(x,yy);
        float shown=1.0-smoothstep(reveal,reveal+0.022,s);
        lightFilament(col,p,previous,current,hue,shown*energy);
        previous=current;
    }
}
void soundRing(inout vec3 col,vec2 p,vec2 c,float radius,float frequency,float phase,vec3 hue,float energy) {
    vec2 q=p-c;
    float a=atan(q.y,q.x);
    float d=abs(length(q/vec2(1.0,0.64))-radius-0.014*sin(a*frequency+phase));
    col+=hue*(exp(-d*d/0.000022)*0.42+exp(-d*d/0.0018)*0.065)*energy;
}
void voiceAperture(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float energy,float phase) {
    vec2 q=(p-c)/scale;
    float lips=abs(length(q/vec2(1.0,0.34))-0.22)-0.013;
    float breath=exp(-dot(q-vec2(0.34,0.0),q-vec2(0.34,0.0))/0.07);
    col+=hue*(aaStroke(lips*scale,0.006)*0.72+glow(lips*scale,0.045)*0.10)*energy;
    col+=mix(hue,CN_PEARL,0.55)*breath*(0.06+0.04*sin(phase))*energy;
}
void listeningSpiral(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float energy,float time) {
    vec2 q=(p-c)/scale;
    vec2 lp=logPolar(q);
    float spiral=abs(sin(lp.x*5.5+lp.y*2.0-time*0.2));
    float mask=smoothstep(0.72,0.08,length(q));
    col+=hue*pow(1.0-spiral,10.0)*mask*energy*0.34;
    soundRing(col,p,c,scale*0.48,7.0,time*0.2,hue,energy);
}
void phonemeWheel(inout vec3 col,vec2 p,vec2 c,float radius,int count,float q,float ae,float time) {
    for (int i=0;i<24;i++) {
        if (i<count) {
            float fi=float(i), a=TAU*fi/float(count)+time*0.018;
            vec2 node=c+vec2(cos(a),sin(a))*vec2(radius,radius*0.64)*q;
            vec3 hue=spectral(fi/float(count)+0.06);
            radiantNode(col,p,node,0.018+0.006*sin(time+fi),hue,q*ae);
            lightFilament(col,p,c,node,hue,q*ae*0.24);
        }
    }
}
void namingFeedback(inout vec3 col,vec2 p,vec2 source,vec2 form,float q,float ae) {
    lightFilament(col,p,source,vec2(0.0,0.22),CN_CYAN,q*ae);
    lightFilament(col,p,vec2(0.0,0.22),form,CN_CYAN,q*ae);
    lightFilament(col,p,form,vec2(0.0,-0.24),CN_GOLD,smoothstep(0.28,0.94,q)*ae);
    lightFilament(col,p,vec2(0.0,-0.24),source,CN_GOLD,smoothstep(0.28,0.94,q)*ae);
}
void responseForm(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float energy,float time) {
    vec2 q=(p-c)/scale;
    float shell=abs(length(q/vec2(0.70,1.0))-0.30)-0.010;
    float inner=cymaticField(q,28.0,time*0.16);
    col+=hue*(aaStroke(shell*scale,0.006)*0.70+glow(shell*scale,0.050)*0.11)*energy;
    col+=mix(hue,CN_PEARL,0.5)*pow(1.0-inner,14.0)*smoothstep(0.35,0.05,length(q))*energy*0.28;
}
vec3 renderCymaticName(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat) {
    float q=easeInOut(progress),ae=audioEnergy(volume,beat);
    vec3 col=phononicBackground(uv,p,time);
    float pressure=cymaticField(p,22.0+8.0*beat,time*0.26);
    col+=mix(CN_VIOLET,CN_CYAN,pressure)*pow(1.0-pressure,18.0)*0.018*ae;

    if (mode==0) {
        livingGlyph(col,p,vec2(0.0),mix(0.14,0.65,q),2.0,mix(CN_SILVER,CN_GOLD,q),q*ae,beat,time);
    } else if (mode==1) {
        voiceAperture(col,p,vec2(-0.68,0.0),0.78,CN_PEARL,ae,time);
        breathRibbon(col,p,0.0,time*0.35,q,CN_CYAN,ae,volume);
        livingGlyph(col,p,vec2(0.50,0.0),0.60,4.0,CN_GOLD,q*ae,beat,time);
    } else if (mode==2) {
        livingGlyph(col,p,vec2(0.0),0.58,7.0,CN_GOLD,ae,beat,time);
        for (int i=0;i<10;i++) soundRing(col,p,vec2(0.0),0.12+float(i)*0.062,9.0+float(i),time*0.18+float(i),mix(CN_CYAN,CN_GOLD,float(i)/9.0),q*ae*(0.68-float(i)*0.052));
    } else if (mode==3) {
        livingGlyph(col,p,vec2(-0.46,0.0),0.60,10.0,CN_CYAN,ae,beat,time);
        responseForm(col,p,vec2(0.46,0.0),mix(0.20,0.78,q),CN_GOLD,q*ae,time);
        namingFeedback(col,p,vec2(-0.38,0.0),vec2(0.38,0.0),q,ae);
    } else if (mode==4) {
        livingGlyph(col,p,vec2(0.0),0.38,13.0,CN_GOLD,ae,beat,time);
        phonemeWheel(col,p,vec2(0.0),0.62,16,q,ae,time);
        for (int i=0;i<5;i++) soundRing(col,p,vec2(0.0),0.18+float(i)*0.095,8.0+float(i)*2.0,time,CN_VIOLET,q*ae*0.38);
    } else if (mode==5) {
        for (int i=0;i<4;i++) {
            float fi=float(i),y=mix(0.44,-0.44,fi/3.0);
            float local=smoothstep(fi/3.0-0.18,fi/3.0+0.06,q);
            livingGlyph(col,p,vec2(0.0,y),0.28+0.10*fi,17.0+fi,mix(CN_GOLD,CN_CYAN,fi/3.0),local*ae,beat,time);
            if(i>0)lightFilament(col,p,vec2(0.0,y+0.12),vec2(0.0,mix(0.44,-0.44,(fi-1.0)/3.0)-0.12),mix(CN_GOLD,CN_CYAN,fi/3.0),local*ae);
        }
    } else if (mode==6) {
        livingGlyph(col,p,vec2(0.0),mix(0.16,0.82,q),23.0,CN_GOLD,ae*(0.8+beat),beat,time);
        phonemeWheel(col,p,vec2(0.0),0.68,8,q,ae,time);
        col+=CN_GOLD*lensFlare(p,vec2(0.0))*0.035*q*ae;
    } else if (mode==7) {
        listeningSpiral(col,p,vec2(-0.62,0.0),0.56,CN_CYAN,ae,time);
        livingGlyph(col,p,vec2(0.62,0.0),0.48,28.0,CN_MAGENTA,ae,beat,time);
        namingFeedback(col,p,vec2(-0.52,0.0),vec2(0.52,0.0),q,ae);
        radiantNode(col,p,vec2(0.0),0.055,CN_GOLD,q*ae);
    } else if (mode==8) {
        livingGlyph(col,p,vec2(0.0),0.52,31.0,CN_GOLD,ae,beat,time);
        for(int i=0;i<9;i++){
            float fi=float(i),a=TAU*fi/9.0;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.70,0.39);
            voiceAperture(col,p,c,0.30,mix(CN_SILVER,CN_GOLD,fi/8.0),q*ae,time+fi);
            lightFilament(col,p,c,vec2(0.0),mix(CN_SILVER,CN_GOLD,fi/8.0),q*ae*0.32);
        }
    } else if (mode==9) {
        voiceAperture(col,p,vec2(0.0,-0.50),0.56,CN_PEARL,ae,time);
        livingGlyph(col,p,vec2(0.0),0.44,37.0,CN_VIOLET,q*ae,beat,time);
        responseForm(col,p,vec2(0.0,0.48),mix(0.18,0.64,q),CN_GOLD,q*ae,time);
        lightFilament(col,p,vec2(0.0,-0.38),vec2(0.0,0.38),CN_GOLD,q*ae);
    } else if (mode==10) {
        livingGlyph(col,p,vec2(-0.48,0.0),0.48,41.0,CN_MAGENTA,ae,beat,time);
        livingGlyph(col,p,vec2(0.48,0.0),0.48,47.0,CN_GOLD,q*ae,beat,time);
        for(int i=0;i<5;i++)soundRing(col,p,vec2(-0.48,0.0),0.12+float(i)*0.07,8.0,time,CN_MAGENTA,ae*0.34);
        lightFilament(col,p,vec2(0.48,0.0),vec2(0.10,-0.30),CN_GREEN,q*ae);
    } else if (mode==11) {
        for(int i=0;i<3;i++){
            vec2 c=vec2(mix(-0.52,0.52,float(i)/2.0),0.0);
            livingGlyph(col,p,c,0.42,51.0+float(i)*3.0,i==1?CN_MAGENTA:CN_VIOLET,q*ae,beat,time);
            lightFilament(col,p,c-vec2(0.14,0.15),c+vec2(0.14,-0.15),CN_MAGENTA,q*ae);
        }
    } else if (mode==12) {
        for(int i=0;i<4;i++){
            float fi=float(i),y=mix(0.44,-0.44,fi/3.0);
            livingGlyph(col,p,vec2(0.0,y),0.26+fi*0.07,60.0+fi,mix(CN_GOLD,CN_VIOLET,fi/3.0),q*ae,beat,time);
            if(i>0)lightFilament(col,p,vec2(0.0,y+0.11),vec2(0.0,mix(0.44,-0.44,(fi-1.0)/3.0)-0.11),CN_GOLD,q*ae);
        }
    } else if (mode==13) {
        livingGlyph(col,p,vec2(0.0),0.42,67.0,CN_GOLD,ae,beat,time);
        phonemeWheel(col,p,vec2(0.0),0.64,18,q,ae,time);
        for(int i=0;i<30;i++){
            float fi=float(i),a=TAU*hash11(fi*5.1)+time*0.025;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.72,0.43)*(0.28+0.72*hash11(fi+4.0))*q;
            radiantNode(col,p,c,0.014,spectral(fi/30.0),q*ae);
        }
    } else if (mode==14) {
        voiceAperture(col,p,vec2(-0.50,0.0),0.58,CN_PEARL,ae,time);
        livingGlyph(col,p,vec2(0.50,0.0),0.55,71.0,CN_GOLD,q*ae,beat,time);
        namingFeedback(col,p,vec2(-0.42,0.0),vec2(0.42,0.0),q,ae);
    } else if (mode==15) {
        float axis=sdSegment(p,vec2(-0.46,0.0),vec2(0.20,0.0));
        col+=CN_PEARL*(aaStroke(axis,0.012)*0.55+glow(axis,0.045)*0.08)*ae;
        for(int i=0;i<7;i++){
            float y=mix(-0.40,0.40,float(i)/6.0);
            vec2 c=vec2(-0.36+0.04*sin(float(i)),y);
            radiantNode(col,p,c,0.035,spectral(float(i)/7.0),q*ae);
            lightFilament(col,p,c,vec2(0.46,0.0),spectral(float(i)/7.0),q*ae*0.48);
        }
        livingGlyph(col,p,vec2(0.48,0.0),0.48,79.0,CN_GOLD,q*ae,beat,time);
    } else if (mode==16) {
        livingGlyph(col,p,vec2(-0.54,0.0),0.42,83.0,CN_GOLD,ae,beat,time);
        for(int i=0;i<4;i++){
            float a=TAU*float(i)/4.0+0.4;
            vec2 c=vec2(0.24,0.0)+vec2(cos(a),sin(a))*vec2(0.38,0.28);
            vec3 hue=spectral(float(i)*0.22);
            radiantNode(col,p,c,0.052,hue,q*ae);
            lightFilament(col,p,vec2(-0.34,0.0),c,hue,q*ae*0.70);
        }
    } else if (mode==17) {
        livingGlyph(col,p,vec2(-0.64,0.0),0.36,89.0,CN_GOLD,ae,beat,time);
        breathRibbon(col,p,-0.20,time*0.2,q,CN_GREEN,ae,volume);
        for(int i=0;i<14;i++){
            float fi=float(i),x=mix(-0.18,0.82,fi/13.0);
            radiantNode(col,p,vec2(x,-0.20+0.055*sin(fi*1.7+time*0.12)),0.016,CN_GREEN,q*ae);
        }
    } else {
        breathRibbon(col,p,0.0,time*0.32,q,CN_CYAN,ae,volume);
        livingGlyph(col,p,vec2(0.18,0.0),mix(0.18,0.72,q),97.0,CN_GOLD,q*ae,beat,time);
        responseForm(col,p,vec2(0.18,0.0),mix(0.16,0.74,q),CN_PEARL,smoothstep(0.48,0.95,q)*ae,time);
        phonemeWheel(col,p,vec2(0.18,0.0),0.64,12,q,ae,time);
        for(int i=0;i<7;i++)soundRing(col,p,vec2(0.18,0.0),0.12+float(i)*0.072,9.0+float(i),time,spectral(float(i)/7.0),q*ae*(0.60-float(i)*0.055));
    }
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
