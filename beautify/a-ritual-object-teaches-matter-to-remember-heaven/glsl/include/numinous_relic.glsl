#ifndef QUEUE_NUMINOUS_RELIC_GLSL
#define QUEUE_NUMINOUS_RELIC_GLSL

const vec3 RO_VOID=vec3(0.006,0.005,0.010);
const vec3 RO_STONE=vec3(0.075,0.065,0.090);
const vec3 RO_GOLD=vec3(1.35,0.63,0.09);
const vec3 RO_CYAN=vec3(0.03,0.80,1.12);
const vec3 RO_VIOLET=vec3(0.55,0.12,1.08);
const vec3 RO_GREEN=vec3(0.04,0.95,0.46);
const vec3 RO_RED=vec3(1.05,0.06,0.18);
const vec3 RO_PEARL=vec3(0.92,0.91,1.05);

int RO_MODE;
float RO_Q;
float RO_TIME;
float RO_BEAT;
float RO_SHIFT;
float RO_SCALE;

vec3 relicSpace(vec3 p) {
    p.x-=RO_SHIFT;
    p/=RO_SCALE;
    p=rotateY(RO_TIME*0.10+RO_Q*0.28)*rotateX(-0.22+0.08*sin(RO_TIME*0.13))*p;
    return p;
}
float relicMap(vec3 world) {
    vec3 p=relicSpace(world);
    float crystal=sdOctahedron3(p,0.69)-0.065;
    float inner=sdSphere3(p,0.47);
    crystal=smoothSubtract(inner,crystal,0.10);
    float belt=sdTorus3(p,vec2(0.48,0.052));
    float crown=sdTorus3(p.yzx,vec2(0.39,0.038));
    float axis=sdCapsule3(p,vec3(0,-0.68,0),vec3(0,0.68,0),0.035);
    float d=smoothUnion(crystal,belt,0.085);
    d=smoothUnion(d,crown,0.065);
    if (RO_MODE==0) d=crystal;
    if (RO_MODE==6) {
        float yantra=min(sdTorus3(p,vec2(0.54,0.032)),sdTorus3(p.yzx,vec2(0.42,0.027)));
        d=smoothUnion(d,yantra,0.045);
    }
    if (RO_MODE==8 || RO_MODE==19) d=smoothUnion(d,axis,0.055);
    return d*RO_SCALE;
}
vec3 relicNormal(vec3 p) {
    vec2 e=vec2(0.0015,0.0);
    return normalize(vec3(
        relicMap(p+e.xyy)-relicMap(p-e.xyy),
        relicMap(p+e.yxy)-relicMap(p-e.yxy),
        relicMap(p+e.yyx)-relicMap(p-e.yyx)
    ));
}
float relicShadow(vec3 ro,vec3 rd) {
    float shade=1.0, travel=0.02;
    for (int i=0;i<20;i++) {
        float d=relicMap(ro+rd*travel);
        shade=min(shade,12.0*d/travel);
        travel+=clamp(d,0.012,0.12);
        if (travel>2.4) break;
    }
    return saturate(shade);
}
vec3 relicMaterial(vec3 p,vec3 n,vec3 rd,float travel) {
    vec3 local=relicSpace(p);
    float mineral=fbm3(local*5.8+vec3(RO_TIME*0.025,0,0));
    float vein=pow(1.0-abs(2.0*fbm3(local*8.2+vec3(4.0,9.0,2.0))-1.0),13.0);
    float angle=atan(local.y,local.x);
    float inscription=pow(0.5+0.5*cos(angle*12.0+length(local)*34.0-RO_TIME*0.20),24.0);
    float metallic=saturate(vein*1.3+inscription*0.48+RO_Q*0.10);
    vec3 base=mix(RO_STONE,vec3(0.20,0.13,0.28),mineral);
    vec3 metal=mix(RO_GOLD,spectral(mineral+RO_TIME*0.006),0.24+0.20*RO_BEAT);
    vec3 albedo=mix(base,metal,metallic);
    if (RO_MODE==13) albedo=mix(albedo,RO_RED,0.48);
    if (RO_MODE==14) albedo=mix(albedo,spectral(mineral),0.34);
    vec3 lightDir=normalize(vec3(-0.55,0.72,0.48));
    float diffuse=max(dot(n,lightDir),0.0);
    float shadow=relicShadow(p+n*0.012,lightDir);
    vec3 halfVector=normalize(lightDir-rd);
    float specular=pow(max(dot(n,halfVector),0.0),mix(22.0,88.0,metallic));
    float fres=fresnelTerm(rd,n,4.0);
    vec3 color=albedo*(0.14+0.92*diffuse*shadow);
    color+=mix(RO_PEARL,RO_GOLD,metallic)*specular*(0.35+1.5*metallic);
    color+=spectral(angle/TAU+RO_TIME*0.01)*fres*(0.10+0.30*RO_Q);
    color+=RO_GOLD*inscription*(0.22+0.50*RO_Q);
    color*=0.94+0.06*cos(travel*18.0);
    return color;
}
vec4 raymarchRelic(vec2 p,float shift,float scale) {
    RO_SHIFT=shift;
    RO_SCALE=scale;
    vec3 eye=vec3(0.0,0.0,3.2);
    vec3 ray=normalize(vec3(p*0.88,-1.72));
    float travel=0.0, aura=0.0;
    bool hit=false;
    vec3 position=eye;
    for (int i=0;i<88;i++) {
        position=eye+ray*travel;
        float d=relicMap(position);
        aura+=exp(-abs(d)*18.0)*0.0035;
        if (d<0.0015) { hit=true; break; }
        travel+=d*0.72;
        if (travel>6.0) break;
    }
    vec3 glowColor=mix(RO_VIOLET,RO_GOLD,RO_Q)*aura*(0.30+0.55*RO_BEAT);
    if (!hit) return vec4(glowColor,saturate(aura*0.20));
    vec3 normal=relicNormal(position);
    vec3 surface=relicMaterial(position,normal,ray,travel)+glowColor;
    return vec4(surface,1.0);
}
vec3 relicBackground(vec2 uv,vec2 p,float time) {
    float smoke=fbmWarp(p*1.35+vec2(time*0.010,-time*0.006),time);
    float ember=fbmWarp(p*3.4+vec2(-time*0.015,time*0.009),time+22.0);
    vec3 col=mix(RO_VOID,vec3(0.040,0.022,0.055),0.34+smoke*0.48);
    col+=mix(RO_VIOLET,RO_GOLD,ember)*pow(max(ember-0.66,0.0),3.2)*0.12;
    float dust=step(0.997,hash21(floor((p+2.0)*320.0)));
    col+=RO_PEARL*dust*0.30;
    return col*(0.69+0.31*vignette(uv));
}
void relicOrbit(inout vec3 col,vec2 p,vec2 c,float radius,float squash,float phase,vec3 hue,float energy) {
    vec2 q=(p-c)/vec2(1.0,squash);
    float d=abs(length(q)-radius-0.010*sin(atan(q.y,q.x)*9.0+phase));
    col+=hue*(exp(-d*d/0.000020)*0.38+exp(-d*d/0.0018)*0.063)*energy;
}
void consecrationBreath(inout vec3 col,vec2 p,float y,float reveal,float time,float volume,vec3 hue,float energy) {
    vec2 previous=vec2(-0.90,y);
    for (int i=1;i<80;i++) {
        float s=float(i)/79.0,x=mix(-0.90,0.90,s);
        float yy=y+sin(PI*s)*(0.06+0.05*volume)*sin(s*TAU*2.1+time*0.35)
            +0.016*sin(s*TAU*7.0-time*0.18);
        vec2 current=vec2(x,yy);
        lightFilament(col,p,previous,current,hue,(1.0-smoothstep(reveal,reveal+0.025,s))*energy);
        previous=current;
    }
}
void correspondenceNodes(inout vec3 col,vec2 p,vec2 center,float radius,float q,float ae,float time) {
    for (int i=0;i<4;i++) {
        float a=TAU*float(i)/4.0-time*0.025;
        vec2 node=center+vec2(cos(a),sin(a))*vec2(radius,radius*0.66);
        vec3 hue=spectral(float(i)*0.22+0.05);
        radiantNode(col,p,node,0.040,hue,q*ae);
        lightFilament(col,p,center,node,hue,q*ae*0.40);
        relicOrbit(col,p,center,radius*(0.56+float(i)*0.13),0.66,time*0.1+float(i),hue,q*ae*0.24);
    }
}
void verticalChain(inout vec3 col,vec2 p,float q,float ae) {
    for (int i=0;i<4;i++) {
        float fi=float(i),y=mix(-0.48,0.48,fi/3.0);
        vec3 hue=mix(RO_CYAN,RO_GOLD,fi/3.0);
        radiantNode(col,p,vec2(0.0,y),0.055,hue,q*ae);
        if(i>0)lightFilament(col,p,vec2(0.0,mix(-0.48,0.48,(fi-1.0)/3.0)+0.05),vec2(0.0,y-0.05),hue,q*ae);
    }
}
void sigilGeometry(inout vec3 col,vec2 p,vec2 c,float radius,float q,float ae,float time) {
    vec2 kp=kaleido(p-c,12.0,time*0.018);
    for(int i=0;i<7;i++){
        float fi=float(i),d=abs(length(kp)-radius*(0.24+fi*0.12));
        col+=spectral(fi/7.0)*(aaStroke(d,0.005)*0.42+glow(d,0.028)*0.075)*q*ae;
    }
    float tri=max(abs(kp.x)*0.866+kp.y*0.5,-kp.y)-radius*0.42;
    col+=RO_GOLD*(aaStroke(tri,0.006)*0.56+glow(tri,0.035)*0.08)*q*ae;
}
vec3 renderNuminousRelic(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat) {
    RO_MODE=mode;RO_Q=easeInOut(progress);RO_TIME=time;RO_BEAT=beat;
    float q=RO_Q,ae=audioEnergy(volume,beat);
    vec3 col=relicBackground(uv,p,time);
    float shift=0.0,scale=mix(0.68,0.90,q);
    if(mode==5||mode==10||mode==15||mode==17||mode==18)shift=0.42;
    vec4 relic=raymarchRelic(p,shift,scale);
    col=mix(col,col+relic.rgb,relic.a);

    if(mode==0){
        col=mix(col,vec3(dot(col,vec3(0.299,0.587,0.114))),0.42*(1.0-q));
    }else if(mode==1){
        correspondenceNodes(col,p,vec2(0.0),0.66,q,ae,time);
    }else if(mode==2){
        for(int i=0;i<16;i++){
            float a=TAU*float(i)/16.0;
            vec2 node=vec2(cos(a),sin(a))*vec2(0.68,0.42)*q;
            lightFilament(col,p,vec2(0.0),node,mix(RO_PEARL,RO_GOLD,float(i)/15.0),q*ae*0.30);
            radiantNode(col,p,node,0.014,RO_PEARL,q*ae);
        }
    }else if(mode==3){
        consecrationBreath(col,p,0.0,q,time,volume,RO_CYAN,ae);
        radiantNode(col,p,vec2(0.0),0.11,RO_GOLD,q*ae*(0.8+beat));
    }else if(mode==4){
        for(int i=0;i<9;i++)relicOrbit(col,p,vec2(0.0),0.15+float(i)*0.065,0.62,time*0.16+float(i),mix(RO_CYAN,RO_GOLD,float(i)/8.0),q*ae*(0.66-float(i)*0.052));
        sigilGeometry(col,p,vec2(0.0),0.64,q,ae,time);
    }else if(mode==5){
        float axis=sdSegment(p,vec2(-0.48,-0.43),vec2(-0.48,0.43));
        col+=RO_PEARL*(aaStroke(axis,0.010)*0.58+glow(axis,0.040)*0.08)*ae;
        for(int i=0;i<6;i++){
            vec2 c=vec2(-0.48,mix(-0.38,0.38,float(i)/5.0));
            vec3 hue=spectral(float(i)/6.0);
            radiantNode(col,p,c,0.038,hue,q*ae);
            lightFilament(col,p,c,vec2(0.34,0.0),hue,q*ae*0.45);
        }
    }else if(mode==6){
        sigilGeometry(col,p,vec2(0.0),0.72,q,ae,time);
        correspondenceNodes(col,p,vec2(0.0),0.62,q,ae*0.62,time);
    }else if(mode==7){
        for(int i=0;i<5;i++){
            float x=mix(-0.70,0.70,float(i)/4.0);
            lightFilament(col,p,vec2(x,0.62),vec2(0.0,0.08),spectral(float(i)/5.0),q*ae);
        }
        correspondenceNodes(col,p,vec2(0.0),0.58,q,ae,time);
    }else if(mode==8){
        verticalChain(col,p,q,ae);
        sigilGeometry(col,p,vec2(0.0),0.70,q*0.55,ae,time);
    }else if(mode==9){
        float cage=abs(sdRoundBox(p,vec2(0.47,0.50),0.035));
        col+=RO_RED*(aaStroke(cage,0.007)*0.52+glow(cage,0.035)*0.06)*(1.0-q)*ae;
        correspondenceNodes(col,p,vec2(0.0),0.63,q,ae,time);
    }else if(mode==10){
        vec2 source=vec2(-0.56,0.0),object=vec2(0.38,0.0);
        radiantNode(col,p,source,0.065,RO_PEARL,ae);
        lightFilament(col,p,source,vec2(0.0,0.22),RO_CYAN,q*ae);
        lightFilament(col,p,vec2(0.0,0.22),object,RO_CYAN,q*ae);
        lightFilament(col,p,object,vec2(0.0,-0.24),RO_GOLD,q*ae);
        lightFilament(col,p,vec2(0.0,-0.24),source,RO_GOLD,q*ae);
    }else if(mode==11){
        for(int i=0;i<10;i++){
            float fi=float(i),a=TAU*fi/10.0;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.72,0.43);
            radiantNode(col,p,c,0.032,mix(RO_PEARL,RO_GOLD,fi/9.0),q*ae);
            lightFilament(col,p,c,vec2(0.0),mix(RO_PEARL,RO_GOLD,fi/9.0),q*ae*0.32);
        }
    }else if(mode==12){
        float divider=abs(p.x);
        col+=RO_RED*exp(-divider*divider/0.00015)*q*ae*0.45;
        float property=abs(length(p-vec2(-0.46,0.0))-0.22);
        col+=RO_RED*(glow(property,0.038)*0.10+aaStroke(property,0.008)*0.55)*q*ae;
        correspondenceNodes(col,p,vec2(0.46,0.0),0.25,q,ae,time);
    }else if(mode==13){
        for(int i=0;i<10;i++){
            float a=TAU*float(i)/10.0;
            vec2 outer=vec2(cos(a),sin(a))*vec2(0.72,0.45);
            lightFilament(col,p,outer,outer*0.42,RO_RED,q*ae);
        }
        relicOrbit(col,p,vec2(0.0),0.53,0.66,time,RO_RED,q*ae);
    }else if(mode==14){
        for(int i=0;i<28;i++){
            float fi=float(i),a=TAU*hash11(fi*3.7)+time*0.022;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.72,0.43)*(0.24+0.76*hash11(fi+6.0))*q;
            radiantNode(col,p,c,0.016,spectral(fi/28.0),q*ae);
            lightFilament(col,p,vec2(0.0),c,spectral(fi/28.0),q*ae*0.16);
        }
    }else if(mode==15){
        vec2 source=vec2(-0.56,0.0),object=vec2(0.38,0.0);
        radiantNode(col,p,source,0.070,RO_PEARL,ae);
        lightFilament(col,p,source,vec2(0.0,0.22),RO_CYAN,q*ae);
        lightFilament(col,p,vec2(0.0,0.22),object,RO_CYAN,q*ae);
        lightFilament(col,p,object,vec2(0.0,-0.24),RO_GOLD,q*ae);
        lightFilament(col,p,vec2(0.0,-0.24),source,RO_GOLD,q*ae);
    }else if(mode==16){
        for(int i=0;i<9;i++)relicOrbit(col,p,vec2(0.0),0.14+float(i)*0.070,0.62,time+float(i),mix(RO_VIOLET,RO_GOLD,float(i)/8.0),q*ae*(0.68-float(i)*0.055));
        sigilGeometry(col,p,vec2(0.0),0.70,q,ae,time);
    }else if(mode==17){
        for(int i=0;i<4;i++){
            float a=TAU*float(i)/4.0+0.4;
            vec2 c=vec2(-0.12,0.0)+vec2(cos(a),sin(a))*vec2(0.42,0.30);
            vec3 hue=spectral(float(i)*0.22);
            radiantNode(col,p,c,0.052,hue,q*ae);
            lightFilament(col,p,vec2(0.32,0.0),c,hue,q*ae*0.70);
        }
    }else if(mode==18){
        consecrationBreath(col,p,-0.23,q,time,volume,RO_GREEN,ae);
        for(int i=0;i<14;i++){
            float fi=float(i),x=mix(-0.20,0.84,fi/13.0);
            radiantNode(col,p,vec2(x,-0.23+0.05*sin(fi*1.5+time*0.12)),0.016,RO_GREEN,q*ae);
        }
    }else{
        consecrationBreath(col,p,0.0,q,time,volume,RO_CYAN,ae);
        correspondenceNodes(col,p,vec2(0.0),0.66,q,ae,time);
        sigilGeometry(col,p,vec2(0.0),0.72,q,ae,time);
        radiantNode(col,p,vec2(0.0),0.12,RO_GOLD,q*ae*(0.8+beat));
    }
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
