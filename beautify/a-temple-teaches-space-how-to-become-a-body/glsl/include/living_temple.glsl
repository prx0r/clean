#ifndef QUEUE_LIVING_TEMPLE_GLSL
#define QUEUE_LIVING_TEMPLE_GLSL

const vec3 LT_VOID=vec3(0.004,0.006,0.012);
const vec3 LT_STONE=vec3(0.090,0.110,0.145);
const vec3 LT_GOLD=vec3(1.32,0.66,0.10);
const vec3 LT_CYAN=vec3(0.04,0.82,1.12);
const vec3 LT_VIOLET=vec3(0.48,0.14,1.08);
const vec3 LT_GREEN=vec3(0.04,0.92,0.49);
const vec3 LT_RED=vec3(1.02,0.07,0.18);
const vec3 LT_PEARL=vec3(0.88,0.94,1.08);

int LT_MODE;
float LT_Q;
float LT_TIME;
float LT_BEAT;

vec2 materialUnion(vec2 a,vec2 b) { return a.x<b.x?a:b; }
float archSDF(vec3 p) {
    float shell=sdRoundBox3(p,vec3(0.52,0.72,0.13),0.045);
    float lower=sdRoundBox3(p-vec3(0.0,-0.20,0.0),vec3(0.25,0.42,0.20),0.11);
    float roundOpening=max(length(p.xy-vec2(0.0,0.20))-0.25,abs(p.z)-0.20);
    return max(shell,-min(lower,roundOpening));
}
vec2 livingTempleMap(vec3 world) {
    vec3 p=world;
    float pulseScale=1.0;
    if(LT_MODE==11||LT_MODE==20)pulseScale=0.94+0.06*sin(LT_TIME*0.65)*(0.4+LT_BEAT);
    p/=pulseScale;
    vec2 result=vec2(p.y+0.76,1.0);
    float zCell=mod(p.z+0.58,1.16)-0.58;
    float columns=sdRoundBox3(vec3(abs(p.x)-0.78,p.y,zCell),vec3(0.075,0.73,0.075),0.028);
    result=materialUnion(result,vec2(columns,2.0));
    float beam=sdRoundBox3(vec3(abs(p.x)-0.78,p.y-0.66,zCell),vec3(0.19,0.055,0.11),0.025);
    result=materialUnion(result,vec2(beam,2.0));
    float threshold=archSDF(p-vec3(0.0,0.0,-0.62));
    result=materialUnion(result,vec2(threshold,2.0));
    float sanctumShell=abs(sdRoundBox3(p-vec3(0.0,-0.02,-2.16),vec3(0.58,0.61,0.58),0.08))-0.055;
    result=materialUnion(result,vec2(sanctumShell,2.0));
    float core=sdSphere3(p-vec3(0.0,-0.27,-2.14),0.115+0.018*LT_BEAT);
    result=materialUnion(result,vec2(core,3.0));
    float axis=sdCapsule3(p,vec3(0.0,-0.74,-2.14),vec3(0.0,0.70,-2.14),0.024);
    if(LT_MODE==1||LT_MODE==2||LT_MODE==10||LT_MODE==14||LT_MODE==18||LT_MODE==20)
        result=materialUnion(result,vec2(axis,3.0));
    if(LT_MODE==6||LT_MODE==13) {
        float orbit=sdTorus3((p-vec3(0.0,-0.58,-2.14)).xzy,vec2(0.52,0.045));
        result=materialUnion(result,vec2(orbit,4.0));
    }
    if(LT_MODE==15) {
        float monolith=sdRoundBox3(p-vec3(0.0,-0.02,-1.12),vec3(0.52,0.74,0.28),0.025);
        result=materialUnion(result,vec2(monolith,5.0));
    }
    if(LT_MODE==16) {
        float gateA=sdRoundBox3(p-vec3(-0.22,-0.05,-0.34),vec3(0.20,0.50,0.065),0.018);
        float gateB=sdRoundBox3(p-vec3(0.22,-0.05,-0.34),vec3(0.20,0.50,0.065),0.018);
        result=materialUnion(result,vec2(min(gateA,gateB),5.0));
    }
    if(LT_MODE==19) {
        vec3 cityP=p;
        cityP.x=mod(cityP.x+0.36,0.72)-0.36;
        cityP.z=mod(cityP.z+0.48,0.96)-0.48;
        float towers=sdRoundBox3(cityP-vec3(0.0,-0.25,-1.8),vec3(0.12,0.48,0.12),0.018);
        result=materialUnion(result,vec2(towers,4.0));
    }
    result.x*=pulseScale;
    return result;
}
vec3 templeNormal(vec3 p) {
    vec2 e=vec2(0.0017,0.0);
    return normalize(vec3(
        livingTempleMap(p+e.xyy).x-livingTempleMap(p-e.xyy).x,
        livingTempleMap(p+e.yxy).x-livingTempleMap(p-e.yxy).x,
        livingTempleMap(p+e.yyx).x-livingTempleMap(p-e.yyx).x
    ));
}
float templeShadow(vec3 ro,vec3 rd) {
    float shade=1.0,travel=0.025;
    for(int i=0;i<24;i++){
        float d=livingTempleMap(ro+rd*travel).x;
        shade=min(shade,14.0*d/travel);
        travel+=clamp(d,0.012,0.14);
        if(travel>3.2)break;
    }
    return saturate(shade);
}
float sacredVolume(vec3 p) {
    float mist=fbm3(p*0.72+vec3(0.0,LT_TIME*0.018,0.0));
    float centerBeam=exp(-p.x*p.x*32.0)*(1.0-smoothstep(-0.65,0.72,p.y));
    float sanctum=exp(-length(p-vec3(0.0,-0.12,-2.14))*1.8);
    float diagonal=exp(-pow((p.x+p.z*0.20+0.18)/0.11,2.0))*(1.0-smoothstep(-0.60,0.72,p.y));
    float density=(0.08+0.24*mist)*centerBeam+0.15*sanctum;
    if(LT_MODE==8)density+=diagonal*0.65;
    if(LT_MODE==9)density+=pow(0.5+0.5*cos(length(p.xz)*28.0-LT_TIME*0.9),18.0)*0.18;
    if(LT_MODE==13||LT_MODE==17)density*=1.7;
    return density;
}
vec3 templeMaterial(vec3 p,vec3 n,vec3 rd,float id,float travel) {
    float stoneNoise=fbm3(p*4.8+vec3(0.0,0.0,LT_TIME*0.012));
    float strata=pow(0.5+0.5*cos(p.y*31.0+stoneNoise*8.0),18.0);
    vec3 albedo=mix(LT_STONE,vec3(0.20,0.16,0.26),stoneNoise);
    if(id>2.5&&id<3.5)albedo=mix(LT_GOLD,LT_PEARL,0.35+0.25*LT_BEAT);
    if(id>3.5&&id<4.5)albedo=mix(LT_VIOLET,LT_CYAN,stoneNoise);
    if(id>4.5)albedo=LT_RED;
    albedo+=LT_GOLD*strata*0.10;
    vec3 lightDir=normalize(vec3(-0.42,0.78,0.40));
    float diffuse=max(dot(n,lightDir),0.0);
    float shadow=templeShadow(p+n*0.012,lightDir);
    vec3 halfVector=normalize(lightDir-rd);
    float specular=pow(max(dot(n,halfVector),0.0),id>2.5?72.0:26.0);
    float fres=fresnelTerm(rd,n,3.8);
    vec3 color=albedo*(0.12+0.95*diffuse*shadow);
    color+=mix(LT_PEARL,LT_GOLD,saturate(id-2.0))*specular*0.72;
    color+=spectral(p.z*0.08+LT_TIME*0.008)*fres*0.10;
    color*=exp(-travel*0.018);
    return color;
}
vec3 raymarchTemple(vec2 p,float time,float q,float beat) {
    vec3 eye=vec3(0.0,0.03,3.65-q*0.28);
    if(LT_MODE==6)eye.x=0.25*sin(q*PI);
    if(LT_MODE==7)eye.z=3.25-q*0.55;
    vec3 target=vec3(0.0,-0.10,-1.35);
    mat3 camera=cameraBasis(eye,target);
    vec3 ray=normalize(camera*vec3(p*0.72,1.45));
    float travel=0.0,transmittance=1.0;
    vec3 volumeColor=vec3(0.0);
    bool hit=false;
    vec3 position=eye;
    float materialId=0.0;
    for(int i=0;i<112;i++){
        position=eye+ray*travel;
        vec2 scene=livingTempleMap(position);
        float density=sacredVolume(position);
        vec3 volumeHue=mix(LT_CYAN,LT_GOLD,saturate((-position.z-0.2)*0.25));
        volumeColor+=transmittance*volumeHue*density*0.022*(0.65+0.55*beat);
        transmittance*=exp(-density*0.018);
        if(scene.x<0.0018){hit=true;materialId=scene.y;break;}
        travel+=scene.x*0.72;
        if(travel>10.0)break;
    }
    if(!hit)return volumeColor;
    vec3 normal=templeNormal(position);
    return templeMaterial(position,normal,ray,materialId,travel)*transmittance+volumeColor;
}
vec3 templeBackground(vec2 uv,vec2 p,float time) {
    float dusk=fbmWarp(p*1.15+vec2(time*0.008,-time*0.005),time);
    vec3 col=mix(LT_VOID,vec3(0.025,0.035,0.070),0.34+0.48*dusk);
    float stars=step(0.998,hash21(floor((p+2.0)*330.0)));
    col+=LT_PEARL*stars*0.28;
    return col*(0.70+0.30*vignette(uv));
}
void planLine(inout vec3 col,vec2 p,vec2 a,vec2 b,vec3 hue,float energy) {
    lightFilament(col,p,a,b,hue,energy);
}
void templePlan(inout vec3 col,vec2 p,vec2 c,float size,float q,float ae,float time) {
    vec2 lp=(p-c)*rot(time*0.008);
    for(int i=0;i<5;i++){
        float fi=float(i),s=size*(1.0-fi*0.15);
        float d=abs(sdRoundBox(lp,vec2(s,s*0.62),0.018));
        col+=mix(LT_CYAN,LT_GOLD,fi/4.0)*(aaStroke(d,0.005)*0.34+glow(d,0.030)*0.055)*q*ae;
    }
    planLine(col,p,c-vec2(size,0.0),c+vec2(size,0.0),LT_GOLD,q*ae*0.52);
    planLine(col,p,c-vec2(0.0,size*0.70),c+vec2(0.0,size*0.70),LT_GOLD,q*ae*0.52);
}
void compassField(inout vec3 col,vec2 p,float q,float ae) {
    vec3 hues[4]=vec3[4](LT_GOLD,LT_RED,LT_VIOLET,LT_CYAN);
    for(int i=0;i<4;i++){
        float a=TAU*float(i)/4.0;
        vec2 node=vec2(cos(a),sin(a))*vec2(0.70,0.43);
        planLine(col,p,vec2(0.0),node,hues[i],q*ae);
        radiantNode(col,p,node,0.040,hues[i],q*ae);
    }
}
void processionPath(inout vec3 col,vec2 p,float q,float ae,float time,vec3 hue) {
    vec2 previous=vec2(-0.88,-0.36);
    for(int i=1;i<72;i++){
        float s=float(i)/71.0;
        vec2 current=vec2(mix(-0.88,0.12,s),mix(-0.36,0.02,s)+0.07*sin(s*TAU*1.4+time*0.12));
        planLine(col,p,previous,current,hue,(1.0-smoothstep(q,q+0.025,s))*ae);
        previous=current;
    }
    radiantNode(col,p,previous,0.042,hue,q*ae);
}
void circumPath(inout vec3 col,vec2 p,float q,float ae,float time) {
    vec2 previous=vec2(0.10,0.0);
    for(int i=1;i<96;i++){
        float s=float(i)/95.0,a=s*TAU*2.25+time*0.025,r=mix(0.10,0.68,s);
        vec2 current=vec2(cos(a),sin(a))*vec2(r,r*0.62);
        planLine(col,p,previous,current,mix(LT_CYAN,LT_GREEN,s),(1.0-smoothstep(q,q+0.018,s))*ae);
        previous=current;
    }
}
void resonanceArchitecture(inout vec3 col,vec2 p,float q,float ae,float time) {
    for(int i=0;i<11;i++){
        float fi=float(i),r=0.10+fi*0.060;
        float d=abs(length(p/vec2(1.0,0.62))-r-0.010*sin(atan(p.y,p.x)*(6.0+fi)+time*0.2));
        col+=mix(LT_CYAN,LT_GOLD,fi/10.0)*(aaStroke(d,0.005)*0.34+glow(d,0.030)*0.06)*q*ae*(0.74-fi*0.052);
    }
}
vec3 renderLivingTemple(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat) {
    LT_MODE=mode;LT_Q=easeInOut(progress);LT_TIME=time;LT_BEAT=beat;
    float q=LT_Q,ae=audioEnergy(volume,beat);
    vec3 col=templeBackground(uv,p,time);
    col+=raymarchTemple(p,time,q,beat);
    if(mode==0){
        templePlan(col,p,vec2(0.0),mix(0.12,0.72,q),q,ae,time);
    }else if(mode==1){
        planLine(col,p,vec2(0.0,-0.58),vec2(0.0,0.58),LT_GOLD,q*ae);
        planLine(col,p,vec2(-0.76,0.0),vec2(0.76,0.0),LT_CYAN,q*ae*0.62);
        radiantNode(col,p,vec2(0.0),0.075,LT_GOLD,q*ae);
    }else if(mode==2){
        templePlan(col,p,vec2(0.0),0.66,q,ae,time);
        planLine(col,p,vec2(-0.48,-0.38),vec2(0.48,0.38),LT_VIOLET,q*ae);
        for(int i=0;i<7;i++){
            vec2 c=mix(vec2(-0.48,-0.38),vec2(0.48,0.38),float(i)/6.0);
            radiantNode(col,p,c,0.028,spectral(float(i)/7.0),q*ae);
        }
    }else if(mode==3){
        compassField(col,p,q,ae);
        templePlan(col,p,vec2(0.0),0.50,q*0.45,ae,time);
    }else if(mode==4){
        float gate=abs(sdRoundBox(p,vec2(0.18,0.54),0.055));
        col+=LT_GOLD*(aaStroke(gate,0.009)*0.72+glow(gate,0.060)*0.13)*q*ae;
        processionPath(col,p,q,ae,time,LT_CYAN);
    }else if(mode==5){
        processionPath(col,p,q,ae,time,LT_GREEN);
        templePlan(col,p,vec2(0.22,0.0),0.48,q*0.55,ae,time);
    }else if(mode==6){
        circumPath(col,p,q,ae,time);
        templePlan(col,p,vec2(0.0),0.46,q*0.62,ae,time);
    }else if(mode==7){
        for(int i=0;i<7;i++){
            float d=abs(sdRoundBox(p,vec2(0.58-float(i)*0.065,0.39-float(i)*0.044),0.025));
            col+=mix(LT_VIOLET,LT_GOLD,float(i)/6.0)*(aaStroke(d,0.005)*0.35+glow(d,0.035)*0.055)*q*ae;
        }
        radiantNode(col,p,vec2(0.0),0.085,LT_GOLD,q*ae*(0.8+beat));
    }else if(mode==8){
        float blade=exp(-pow((p.x+p.y*0.34-0.18)/0.055,2.0))*(1.0-smoothstep(-0.48,0.55,p.y));
        col+=mix(LT_GOLD,LT_PEARL,blade)*blade*q*ae*0.42;
        radiantNode(col,p,vec2(0.0,-0.20),0.080,LT_GOLD,q*ae);
    }else if(mode==9){
        resonanceArchitecture(col,p,q,ae,time);
    }else if(mode==10){
        float axis=sdSegment(p,vec2(-0.48,-0.46),vec2(-0.48,0.46));
        col+=LT_PEARL*(aaStroke(axis,0.010)*0.54+glow(axis,0.042)*0.08)*ae;
        templePlan(col,p,vec2(0.40,0.0),0.40,q,ae,time);
        for(int i=0;i<6;i++){
            vec2 c=vec2(-0.48,mix(-0.40,0.40,float(i)/5.0));
            radiantNode(col,p,c,0.034,spectral(float(i)/6.0),q*ae);
            planLine(col,p,c,vec2(0.40,mix(-0.28,0.28,float(i)/5.0)),spectral(float(i)/6.0),q*ae*0.45);
        }
    }else if(mode==11){
        templePlan(col,p,vec2(0.0),0.52+0.06*sin(time*0.65)*(0.4+beat),q,ae,time);
        resonanceArchitecture(col,p,q*0.55,ae,time);
    }else if(mode==12){
        radiantNode(col,p,vec2(-0.62,0.0),0.066,LT_PEARL,ae);
        templePlan(col,p,vec2(0.48,0.0),0.30,q,ae,time);
        planLine(col,p,vec2(-0.54,0.0),vec2(0.0,0.22),LT_CYAN,q*ae);
        planLine(col,p,vec2(0.0,0.22),vec2(0.42,0.0),LT_CYAN,q*ae);
        planLine(col,p,vec2(0.42,0.0),vec2(0.0,-0.24),LT_GOLD,q*ae);
        planLine(col,p,vec2(0.0,-0.24),vec2(-0.54,0.0),LT_GOLD,q*ae);
    }else if(mode==13){
        templePlan(col,p,vec2(0.0),0.62,q,ae,time);
        for(int i=0;i<8;i++){
            float fi=float(i),r=0.15+fi*0.074;
            float d=abs(length(p/vec2(1.0,0.62))-r);
            col+=spectral(fi/8.0)*(aaStroke(d,0.005)*0.35+glow(d,0.032)*0.065)*q*ae;
        }
    }else if(mode==14){
        templePlan(col,p,vec2(0.0),0.58,q*0.62,ae,time);
        compassField(col,p,q,ae*0.70);
        radiantNode(col,p,vec2(0.0),0.105,LT_GOLD,q*ae*(0.9+beat));
    }else if(mode==15){
        float frame=abs(sdRoundBox(p,vec2(0.52,0.50),0.015));
        col+=LT_RED*(aaStroke(frame,0.010)*0.75+glow(frame,0.055)*0.12)*q*ae;
        planLine(col,p,vec2(0.0,0.58),vec2(0.0,0.10),LT_RED,q*ae);
    }else if(mode==16){
        templePlan(col,p,vec2(0.0),0.58,q*0.70,ae,time);
        planLine(col,p,vec2(-0.58,-0.10),vec2(-0.58,0.10),LT_RED,q*ae);
        planLine(col,p,vec2(0.58,-0.10),vec2(0.58,0.10),LT_RED,q*ae);
        planLine(col,p,vec2(-0.10,-0.36),vec2(0.10,-0.36),LT_RED,q*ae);
        planLine(col,p,vec2(-0.10,0.36),vec2(0.10,0.36),LT_RED,q*ae);
    }else if(mode==17){
        templePlan(col,p,vec2(0.0),0.45,q,ae,time);
        for(int i=0;i<30;i++){
            float fi=float(i),a=TAU*hash11(fi*3.4)+time*0.020;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.74,0.44)*(0.20+0.80*hash11(fi+5.0))*q;
            radiantNode(col,p,c,0.014,spectral(fi/30.0),q*ae);
            planLine(col,p,vec2(0.0),c,spectral(fi/30.0),q*ae*0.14);
        }
    }else if(mode==18){
        radiantNode(col,p,vec2(-0.58,0.0),0.070,LT_PEARL,ae);
        templePlan(col,p,vec2(0.42,0.0),0.36,q,ae,time);
        planLine(col,p,vec2(-0.50,0.0),vec2(0.0,0.22),LT_CYAN,q*ae);
        planLine(col,p,vec2(0.0,0.22),vec2(0.38,0.0),LT_CYAN,q*ae);
        planLine(col,p,vec2(0.38,0.0),vec2(0.0,-0.24),LT_GOLD,q*ae);
        planLine(col,p,vec2(0.0,-0.24),vec2(-0.50,0.0),LT_GOLD,q*ae);
    }else if(mode==19){
        processionPath(col,p,q,ae,time,LT_GREEN);
        for(int i=0;i<9;i++){
            float x=mix(-0.72,0.72,float(i)/8.0);
            planLine(col,p,vec2(x,-0.44),vec2(x,0.44),LT_CYAN,q*ae*0.16);
        }
    }else{
        templePlan(col,p,vec2(0.0),0.62,q,ae,time);
        compassField(col,p,q,ae*0.72);
        circumPath(col,p,q,ae*0.64,time);
        resonanceArchitecture(col,p,q*0.52,ae,time);
        radiantNode(col,p,vec2(0.0),0.105,LT_GOLD,q*ae*(0.9+beat));
    }
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
