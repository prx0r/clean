#ifndef QUEUE_NAVIGATION_ATLAS_GLSL
#define QUEUE_NAVIGATION_ATLAS_GLSL

#include "primitives.glsl"
#include "visionary.glsl"

const vec3 NA_VOID=vec3(0.001,0.005,0.014);
const vec3 NA_NAVY=vec3(0.008,0.030,0.090);
const vec3 NA_CYAN=vec3(0.00,0.96,1.24);
const vec3 NA_BLUE=vec3(0.01,0.22,1.12);
const vec3 NA_GOLD=vec3(1.36,0.61,0.06);
const vec3 NA_RED=vec3(1.10,0.025,0.10);
const vec3 NA_GREEN=vec3(0.08,1.04,0.42);
const vec3 NA_MAGENTA=vec3(1.05,0.035,0.67);
const vec3 NA_VIOLET=vec3(0.46,0.07,1.14);
const vec3 NA_PEARL=vec3(0.86,0.98,1.15);

vec3 naBackground(vec2 p,vec2 uv,float time,int mode){
    float atlas=fbmWarp(p*1.20+vec2(time*0.007,-time*0.009),time+109.0);
    float ridge=ridgedFbm(p*3.0+vec2(-time*0.008,time*0.004));
    vec3 col=mix(NA_VOID,NA_NAVY,0.34+0.38*atlas);
    col+=mix(NA_BLUE,NA_VIOLET,atlas)*pow(max(ridge-0.64,0.0),2.6)*0.065;
    vec2 grid=abs(fract((p+vec2(time*0.003,0.0))*8.0)-0.5);
    float meridian=(1.0-smoothstep(0.46,0.49,min(grid.x,grid.y)));
    col+=NA_CYAN*meridian*0.006;
    if(mode==13||mode==16||mode==22) col+=NA_RED*pow(max(atlas-0.62,0.0),2.2)*0.050;
    return col*(0.70+0.30*vignette(uv));
}
vec3 naScaleHue(float x){
    return cosinePalette(x,vec3(0.54),vec3(0.46),vec3(1.0),vec3(0.47,0.17,0.02));
}
void naNode(inout vec3 col,vec2 p,vec2 c,float r,vec3 hue,float q,float energy){
    radiantNode(col,p,c,r,hue,q*energy);
    float ring=abs(length(p-c)-r*2.0);
    col+=hue*(aaStroke(ring,0.004)*0.26+glow(ring,0.024)*0.04)*q*energy;
}
void naArrow(inout vec3 col,vec2 p,vec2 a,vec2 b,vec3 hue,float q,float energy){
    lightFilament(col,p,a,b,hue,q*energy);
    vec2 n=normalize(b-a),side=vec2(-n.y,n.x);
    lightFilament(col,p,b,b-n*0.11+side*0.055,hue,q*energy);
    lightFilament(col,p,b,b-n*0.11-side*0.055,hue,q*energy);
}
void naAgent(inout vec3 col,vec2 p,vec2 c,float r,float heading,vec3 hue,float q,float time,float energy){
    vec2 lp=(p-c)/r;
    float a=atan(lp.y,lp.x);
    float shell=(length(lp)-1.0-0.08*sin(a*5.0+heading+time*0.14))*r;
    col+=hue*(aaStroke(shell,0.006)*0.48+glow(shell,0.032)*0.06+aaFill(shell)*0.035)*q*energy;
    vec2 dir=vec2(cos(heading),sin(heading));
    naArrow(col,p,c,c+dir*r*0.72,NA_PEARL,q,energy*0.55);
    naNode(col,p,c,r*0.12,NA_GOLD,q,energy*0.65);
}
void naCompass(inout vec3 col,vec2 p,vec2 c,float r,float heading,float q,float time,float energy){
    for(int i=0;i<4;i++){
        float fi=float(i),rr=r*(0.38+fi*0.20);
        float d=abs(length(p-c)-rr);
        col+=mix(NA_BLUE,NA_CYAN,fi/3.0)*(aaStroke(d,0.006)*0.32+glow(d,0.03)*0.042)*q*energy;
    }
    vec2 dir=vec2(cos(heading),sin(heading));
    naArrow(col,p,c,c+dir*r*0.78,NA_CYAN,q,energy);
    naNode(col,p,c,r*0.075,NA_GOLD,q,energy);
}
void naLandscape(inout vec3 col,vec2 p,vec2 goal,float scale,float q,float time,float energy,vec3 hue){
    vec2 lp=(p-goal)/vec2(1.0,0.64);
    float terrain=length(lp)/scale+0.16*fbmWarp((p-goal)*3.0,time+14.0);
    float bands=abs(fract(terrain*10.0-time*0.028)-0.5);
    col+=hue*(1.0-smoothstep(0.035,0.10,bands))*0.16*q*energy;
    col+=mix(hue,NA_GOLD,saturate(1.0-terrain))*pow(max(1.0-terrain,0.0),3.0)*0.20*q;
    naNode(col,p,goal,0.07,hue,q,energy);
}
void naBoundary(inout vec3 col,vec2 p,vec2 c,vec2 radii,vec3 hue,float q,float energy){
    float d=abs(length((p-c)/radii)-1.0)*min(radii.x,radii.y);
    col+=hue*(aaStroke(d,0.009)*0.52+glow(d,0.052)*0.085)*q*energy;
}
void naSwarm(inout vec3 col,vec2 p,vec2 c,float scale,int count,float alignment,float q,float time,float energy){
    for(int i=0;i<24;i++){
        if(i>=count) break;
        float fi=float(i);
        vec2 h=hash22(vec2(fi*3.7,41.0));
        vec2 pos=c+(h*2.0-1.0)*vec2(scale,scale*0.62);
        pos+=0.035*vec2(sin(time*0.18+fi),cos(time*0.14+fi*1.7));
        float heading=mix(TAU*hash11(fi+2.0),0.12*sin(time*0.15),alignment);
        naAgent(col,p,pos,0.055+0.018*hash11(fi),heading,naScaleHue(fi/24.0),q,time,energy*0.62);
    }
}
void naLightCone(inout vec3 col,vec2 p,vec2 origin,vec2 target,float aperture,float reach,float q,float time,float energy){
    vec2 axis=target-origin;
    float L=length(axis),effective=L*reach;
    vec2 dir=axis/L,rel=p-origin;
    float along=dot(rel,dir);
    float side=abs(dot(rel,vec2(-dir.y,dir.x)));
    float width=max(0.012,aperture*along);
    float inside=(1.0-smoothstep(width,width+0.025,side))*smoothstep(-0.02,0.05,along)*(1.0-smoothstep(effective,effective+0.08,along));
    float strata=0.5+0.5*cos(side*76.0-along*18.0+time*0.35);
    col+=mix(NA_CYAN,NA_GOLD,saturate(along/max(effective,0.01)))*inside*(0.06+0.055*strata)*q*energy;
    naArrow(col,p,origin,origin+dir*effective,NA_GOLD,q,energy);
}
void naNested(inout vec3 col,vec2 p,vec2 c,float q,float time,float energy){
    for(int i=0;i<7;i++){
        float fi=float(i),r=0.16+fi*0.15;
        float a=atan(p.y-c.y,p.x-c.x);
        float d=abs(length((p-c)/vec2(1.0,0.68))-r-0.012*sin(a*(4.0+fi)+time*0.12));
        vec3 hue=naScaleHue(fi/7.0);
        col+=hue*(aaStroke(d,0.007)*0.40+glow(d,0.036)*0.055)*q*energy;
        naNode(col,p,c+vec2(cos(fi*2.0),sin(fi*2.0))*vec2(r,r*0.68),0.025,hue,q,energy);
    }
}
float naBodyD(vec2 p,vec2 c,float scale){
    vec2 q=(p-c)/scale;
    float head=sdCircle(q-vec2(0.0,0.45),0.14);
    float torso=sdEllipse(q-vec2(0.0,0.02),vec2(0.28,0.43));
    float arms=sdSegment(q,vec2(-0.50,0.16),vec2(0.50,0.16))-0.065;
    float leg1=sdSegment(q,vec2(-0.10,-0.30),vec2(-0.24,-0.78))-0.065;
    float leg2=sdSegment(q,vec2(0.10,-0.30),vec2(0.24,-0.78))-0.065;
    return min(min(head,torso),min(arms,min(leg1,leg2)))*scale;
}
void naBody(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float q,float energy){
    float d=naBodyD(p,c,scale);
    col+=hue*(aaStroke(d,0.009)*0.52+glow(d,0.052)*0.09+aaFill(d)*0.025)*q*energy;
}
void naBrain(inout vec3 col,vec2 p,vec2 c,float scale,float q,float time,float energy){
    vec2 lp=(p-c)/scale;
    float outer=sdEllipse(lp,vec2(0.62,0.48));
    col+=NA_PEARL*(aaStroke(outer,0.018)*0.50+glow(outer,0.075)*0.09)*q*energy;
    for(int i=0;i<16;i++){
        float fi=float(i),a=TAU*fi/16.0;
        vec2 n=c+scale*vec2(cos(a),sin(a))*vec2(0.43,0.31)*(0.58+0.30*hash11(fi));
        naNode(col,p,n,0.026,naScaleHue(fi/16.0),q,energy);
        if(i>0){
            float pa=TAU*(fi-1.0)/16.0;
            vec2 prev=c+scale*vec2(cos(pa),sin(pa))*vec2(0.43,0.31)*(0.58+0.30*hash11(fi-1.0));
            lightFilament(col,p,prev,n,NA_CYAN,q*energy*0.40);
        }
    }
}
void naFiveSpace(inout vec3 col,vec2 p,int selected,float q,float time,float energy){
    vec2 centers[5]=vec2[5](vec2(-1.20,0.0),vec2(-0.60,0.0),vec2(0.0,0.0),vec2(0.60,0.0),vec2(1.20,0.0));
    vec3 hues[5]=vec3[5](NA_GOLD,NA_MAGENTA,NA_CYAN,NA_GREEN,NA_VIOLET);
    for(int i=0;i<5;i++){
        float emphasis=i==selected?1.0:0.24;
        naBoundary(col,p,centers[i],vec2(0.24,0.42),hues[i],q*emphasis,energy);
        naCompass(col,p,centers[i],0.17,float(i)*0.72+time*0.02,q*emphasis,time,energy);
    }
}
void naFailureCards(inout vec3 col,vec2 p,float q,float time,float energy){
    vec2 centers[4]=vec2[4](vec2(-0.83,0.38),vec2(0.83,0.38),vec2(-0.83,-0.38),vec2(0.83,-0.38));
    for(int i=0;i<4;i++){
        vec3 hue=i==0?NA_RED:(i==1?NA_GOLD:(i==2?NA_MAGENTA:NA_CYAN));
        float d=abs(sdRoundBox(p-centers[i],vec2(0.58,0.25),0.045));
        col+=hue*(aaStroke(d,0.008)*0.46+glow(d,0.040)*0.055)*q*energy;
        float symbol=i==0?abs(p.x-centers[i].x):i==1?abs(p.y-centers[i].y):abs(length(p-centers[i])-0.09);
        col+=hue*(aaStroke(symbol,0.008)*0.42+glow(symbol,0.032)*0.04)*q;
    }
}
void naCompiler(inout vec3 col,vec2 p,float q,float time,float energy){
    for(int y=-2;y<=2;y++) for(int x=-2;x<=2;x++){
        vec2 c=vec2(-1.05+float(x)*0.16,float(y)*0.15);
        float bit=hash11(float(x*17+y*31));
        float d=abs(sdRoundBox(p-c,vec2(0.045,0.035),0.008));
        col+=mix(NA_BLUE,NA_MAGENTA,bit)*aaStroke(d,0.004)*q*energy;
    }
    vec2 waist=vec2(-0.10,0.0);
    naArrow(col,p,vec2(-0.58,0.0),waist,NA_GOLD,q,energy);
    naNode(col,p,waist,0.075,NA_GOLD,q,energy);
    for(int i=0;i<10;i++){
        float fi=float(i),a=TAU*fi/10.0;
        vec2 c=vec2(0.88,0.0)+vec2(cos(a),sin(a))*vec2(0.52,0.36);
        naAgent(col,p,c,0.09,a+time*0.03,NA_GREEN,q,time,energy);
        naArrow(col,p,waist,c,NA_GREEN,q,energy*0.45);
    }
}

vec3 renderNavigationAtlas(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat){
    float q=easeInOut(progress),energy=audioEnergy(volume,beat);
    vec3 col=naBackground(p,uv,time,mode);

    if(mode==0){
        vec2 points[4]=vec2[4](vec2(-1.14,0.0),vec2(-0.38,0.48),vec2(0.42,-0.32),vec2(1.12,0.12));
        for(int i=0;i<4;i++){
            vec3 hue=naScaleHue(float(i)/4.0);
            naNode(col,p,points[i],0.065,hue,q,energy);
            if(i<3) naArrow(col,p,points[i],points[i+1],hue,q,energy);
        }
        naCompass(col,p,points[0],0.24,0.72,q,time,energy);
        naLandscape(col,p,points[3],0.48,q,time,energy,NA_GOLD);
    }else if(mode==1){
        vec2 center=vec2(0.0);
        naLandscape(col,p,center,0.58,q,time,energy,NA_GOLD);
        for(int i=0;i<12;i++){
            float fi=float(i),a=TAU*fi/12.0+time*0.025;
            vec2 c=center+vec2(cos(a),sin(a))*vec2(0.98,0.58);
            vec2 n=center+vec2(cos(a+TAU/12.0),sin(a+TAU/12.0))*vec2(0.98,0.58);
            naNode(col,p,c,0.045,NA_GOLD,q,energy);
            naArrow(col,p,c,n,NA_GOLD,q,energy*0.70);
        }
        naCompass(col,p,center,0.30,time*0.04,q,time,energy);
    }else if(mode==2){
        for(int i=0;i<25;i++){
            float fi=float(i),x=mix(-1.34,1.34,fi/24.0);
            float y=0.34*sin(x*5.6-time*0.52);
            vec2 a=vec2(x,y),b=vec2(x,-y);
            if(i<24){
                float nx=mix(-1.34,1.34,(fi+1.0)/24.0);
                float ny=0.34*sin(nx*5.6-time*0.52);
                lightFilament(col,p,a,vec2(nx,ny),NA_MAGENTA,q*energy);
                lightFilament(col,p,b,vec2(nx,-ny),NA_CYAN,q*energy);
            }
            if(i%2==0) lightFilament(col,p,a,b,NA_PEARL,q*energy*0.52);
            if(i%4==0) naNode(col,p,mix(a,b,0.5),0.026,NA_GOLD,q,energy);
        }
        naLightCone(col,p,vec2(-1.34,0.0),vec2(1.34,0.0),0.12,1.0,q,time,energy*0.45);
    }else if(mode==3){
        naBoundary(col,p,vec2(0.0),vec2(1.32,0.72),NA_CYAN,q,energy);
        for(int i=0;i<9;i++){
            float fi=float(i),y=mix(-0.52,0.52,fi/8.0);
            float wave=y+0.09*sin(p.x*(2.2+fi*0.34)-time*(0.28+fi*0.04));
            float d=abs(p.y-wave);
            vec3 hue=mix(NA_BLUE,NA_CYAN,fi/8.0);
            col+=hue*(aaStroke(d,0.006)*0.48+glow(d,0.040)*0.065)*q*energy;
        }
        naCompass(col,p,vec2(-0.96,0.0),0.20,0.0,q,time,energy);
        naLandscape(col,p,vec2(0.94,0.0),0.44,q,time,energy,NA_GREEN);
    }else if(mode==4){
        for(int i=0;i<20;i++){
            float fi=float(i),a=TAU*fi/20.0;
            float r=0.42+0.12*sin(a*5.0+time*0.08);
            vec2 target=vec2(cos(a),sin(a))*vec2(r,r*0.72);
            vec2 start=vec2(cos(a),sin(a))*vec2(1.28,0.72);
            naAgent(col,p,mix(start,target,q),0.073,a+PI*0.5,NA_GREEN,q,time,energy);
            naArrow(col,p,start,target,NA_GOLD,q,energy*0.42);
        }
        naCompass(col,p,vec2(0.0),0.26,time*0.03,q,time,energy);
        naBoundary(col,p,vec2(0.0),vec2(0.72,0.52),NA_GREEN,q,energy);
    }else if(mode==5){
        vec2 origin=vec2(-1.18,0.0);
        naAgent(col,p,origin,0.16,0.0,NA_VIOLET,q,time,energy);
        vec2 goals[5]=vec2[5](vec2(0.92,0.62),vec2(1.20,0.25),vec2(0.82,0.0),vec2(1.18,-0.31),vec2(0.88,-0.64));
        for(int i=0;i<5;i++){
            float fi=float(i);
            vec2 bend=vec2(-0.08,mix(0.55,-0.55,fi/4.0));
            vec3 hue=naScaleHue(fi/5.0);
            naArrow(col,p,origin,bend,hue,q,energy*0.70);
            naArrow(col,p,bend,goals[i],hue,q,energy*0.70);
            naNode(col,p,goals[i],0.052,hue,q,energy);
        }
        naLandscape(col,p,goals[2],0.44,q,time,energy,NA_GOLD);
    }else if(mode==6){
        naFiveSpace(col,p,-1,q,time,energy);
        vec2 center=vec2(0.0);
        for(int i=0;i<5;i++){
            float fi=float(i),a=TAU*fi/5.0;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.80,0.48);
            naArrow(col,p,c,center,naScaleHue(fi/5.0),q,energy);
        }
        naCompass(col,p,center,0.28,time*0.04,q,time,energy);
    }else if(mode==7){
        naAgent(col,p,vec2(-0.78,0.0),0.22,0.0,NA_CYAN,q,time,energy);
        for(int i=0;i<8;i++){
            float fi=float(i),r=0.16+fi*0.09;
            float echo=abs(length((p-vec2(-0.78,0.0))/vec2(1.0,0.66))-r);
            col+=NA_GOLD*(aaStroke(echo,0.006)*0.30+glow(echo,0.03)*0.04)*q*energy;
        }
        naLandscape(col,p,vec2(0.82,0.0),0.62,q,time,energy,NA_GREEN);
        naArrow(col,p,vec2(-0.50,0.0),vec2(0.40,0.0),NA_GOLD,q,energy);
    }else if(mode==8){
        naLandscape(col,p,vec2(0.92,0.0),0.64,q,time,energy,NA_GREEN);
        vec2 path[5]=vec2[5](vec2(-1.25,-0.52),vec2(-0.72,0.30),vec2(-0.20,-0.16),vec2(0.32,0.22),vec2(0.88,0.02));
        for(int i=0;i<4;i++){
            float improvement=float(i)/3.0;
            vec2 mid=mix(path[i],path[i+1],q);
            naArrow(col,p,path[i],path[i+1],mix(NA_RED,NA_GREEN,improvement),q,energy);
            naAgent(col,p,mid,0.075,atan(path[i+1].y-path[i].y,path[i+1].x-path[i].x),NA_CYAN,q,time,energy);
        }
    }else if(mode==9){
        vec2 origin=vec2(-1.22,0.0);
        naAgent(col,p,origin,0.18,0.0,NA_CYAN,q,time,energy);
        for(int i=0;i<9;i++){
            float fi=float(i),a=mix(-0.82,0.82,fi/8.0);
            vec2 bend=vec2(-0.10,0.62*sin(a*1.7));
            vec2 goal=vec2(1.18*cos(a*0.25),0.75*sin(a));
            naArrow(col,p,origin,bend,naScaleHue(fi/9.0),q,energy*0.58);
            naArrow(col,p,bend,goal,naScaleHue(fi/9.0),q,energy*0.58);
            naNode(col,p,goal,0.038,naScaleHue(fi/9.0),q,energy);
        }
    }else if(mode==10){
        naNested(col,p,vec2(0.0),q,time,energy);
        for(int i=0;i<6;i++){
            float fi=float(i),r=0.18+fi*0.15;
            naCompass(col,p,vec2(0.0),r*0.54,time*0.03+fi*0.5,q*(1.0-fi*0.08),time,energy);
        }
    }else if(mode==11){
        vec2 levels[4]=vec2[4](vec2(-1.10,-0.54),vec2(-0.38,-0.18),vec2(0.38,0.20),vec2(1.08,0.56));
        for(int i=0;i<4;i++){
            float fi=float(i);
            naBoundary(col,p,levels[i],vec2(0.24+0.04*fi,0.16+0.025*fi),naScaleHue(fi/4.0),q,energy);
            naCompass(col,p,levels[i],0.13,0.35+fi*0.45,q,time,energy);
            if(i<3) naArrow(col,p,levels[i],levels[i+1],NA_GOLD,q,energy);
        }
    }else if(mode==12){
        naSwarm(col,p,vec2(0.0),1.12,18,0.18,q,time,energy);
        vec2 radii=mix(vec2(0.34,0.22),vec2(1.34,0.74),q);
        naBoundary(col,p,vec2(0.0),radii,NA_GREEN,q,energy);
        naCompass(col,p,vec2(0.0),0.26,time*0.03,q,time,energy);
    }else if(mode==13){
        naSwarm(col,p,vec2(-0.72,0.0),0.62,10,0.0,q,time,energy);
        naSwarm(col,p,vec2(0.72,0.0),0.62,10,0.0,q,time+8.0,energy);
        vec2 joint=vec2(0.0);
        naLandscape(col,p,joint,0.44,q,time,energy,NA_GOLD);
        naArrow(col,p,vec2(-0.52,0.0),joint,NA_GREEN,q,energy);
        naArrow(col,p,vec2(0.52,0.0),joint,NA_GREEN,q,energy);
    }else if(mode==14){
        vec2 source=vec2(0.0,0.0);
        naNode(col,p,source,0.10,NA_GOLD,q,energy);
        for(int i=0;i<12;i++){
            float fi=float(i),a=TAU*fi/12.0;
            vec2 c=vec2(cos(a),sin(a))*vec2(1.18,0.66);
            naAgent(col,p,c,0.075,a+PI,fi<6.0?NA_RED:NA_BLUE,q,time,energy);
            naArrow(col,p,c,source,fi<6.0?NA_RED:NA_BLUE,q,energy*0.55);
        }
        naBoundary(col,p,source,vec2(0.38,0.26),NA_GREEN,q,energy);
    }else if(mode==15){
        naSwarm(col,p,vec2(0.0),1.14,22,0.78,q,time,energy);
        naLandscape(col,p,vec2(0.82,0.0),0.70,q,time,energy,NA_GREEN);
        naLightCone(col,p,vec2(-0.98,0.0),vec2(0.82,0.0),0.24,1.0,q,time,energy);
        naBoundary(col,p,vec2(0.0),vec2(1.36,0.74),NA_CYAN,q*0.50,energy);
    }else if(mode==16){
        naSwarm(col,p,vec2(0.0),1.20,22,0.0,q,time,energy);
        for(int i=0;i<14;i++){
            float fi=float(i);
            vec2 a=hash22(vec2(fi,7.0))*vec2(2.5,1.3)-vec2(1.25,0.65);
            vec2 b=hash22(vec2(fi,31.0))*vec2(2.5,1.3)-vec2(1.25,0.65);
            naArrow(col,p,a,b,i%2==0?NA_RED:NA_MAGENTA,q,energy*0.72);
        }
        naLandscape(col,p,vec2(0.94,0.0),0.55,q*0.32,time,energy,NA_GREEN);
    }else if(mode==17){
        naCompiler(col,p,q,time,energy);
    }else if(mode==18){
        vec2 c=vec2(0.0);
        for(int i=0;i<17;i++){
            float fi=float(i),a=TAU*fi/17.0;
            float r=0.44+0.20*sin(a*5.0+time*0.10)+0.09*sin(a*9.0);
            vec2 n=c+vec2(cos(a),sin(a))*vec2(r,r*0.70);
            naAgent(col,p,n,0.085,a+PI*0.5,naScaleHue(fi/17.0),q,time,energy);
            if(i>0){
                float pa=TAU*(fi-1.0)/17.0;
                float pr=0.44+0.20*sin(pa*5.0+time*0.10)+0.09*sin(pa*9.0);
                lightFilament(col,p,vec2(cos(pa),sin(pa))*vec2(pr,pr*0.70),n,NA_GOLD,q*energy*0.36);
            }
        }
        naCompass(col,p,c,0.30,time*0.05,q,time,energy);
    }else if(mode==19){
        vec2 left=vec2(-0.92,0.0),right=vec2(0.92,0.0);
        naSwarm(col,p,left,0.46,10,0.35,q,time,energy);
        naCompiler(col,p,q*0.45,time,energy*0.50);
        naSwarm(col,p,right,0.46,10,0.35,q,time+4.0,energy);
        naArrow(col,p,left,vec2(0.0),NA_CYAN,q,energy);
        naArrow(col,p,vec2(0.0),right,NA_GOLD,q,energy);
        naBoundary(col,p,vec2(0.0),vec2(1.45,0.76),NA_GREEN,q,energy);
    }else if(mode==20){
        vec2 c=vec2(0.0);
        for(int i=0;i<9;i++){
            float fi=float(i),r=0.16+fi*0.12;
            float frame=abs(sdRoundBox(p-c,vec2(r,r*0.62),0.035));
            col+=naScaleHue(fi/9.0)*(aaStroke(frame,0.006)*0.38+glow(frame,0.030)*0.043)*q*energy;
        }
        naAgent(col,p,c,0.10,0.0,NA_CYAN,q,time,energy);
        naBody(col,p,vec2(0.0),0.98,NA_PEARL,q*0.45,energy);
    }else if(mode==21){
        vec2 self=vec2(-1.12,0.0),goal=vec2(1.10,0.0);
        naAgent(col,p,self,0.16,0.0,NA_CYAN,q,time,energy);
        naLandscape(col,p,goal,0.48,q,time,energy,NA_GOLD);
        naLightCone(col,p,self,goal,mix(0.06,0.34,q),mix(0.28,1.0,q),q,time,energy);
        for(int i=0;i<8;i++){
            float fi=float(i),along=fi/8.0;
            vec2 c=mix(self,goal,along)+vec2(0.0,0.34*sin(fi*2.2));
            naNode(col,p,c,0.026,naScaleHue(fi/8.0),q,energy);
        }
    }else if(mode==22){
        naFailureCards(col,p,q,time,energy);
    }else if(mode==23){
        naSwarm(col,p,vec2(-0.62,0.0),0.62,15,0.70,q,time,energy);
        vec2 rogue=vec2(0.62,0.0);
        naSwarm(col,p,rogue,0.46,10,0.0,q,time+2.0,energy);
        naBoundary(col,p,rogue,vec2(0.54,0.38),NA_RED,q,energy);
        naArrow(col,p,vec2(-0.16,0.0),rogue,NA_RED,q,energy);
    }else if(mode==24){
        naSwarm(col,p,vec2(0.0),1.10,22,mix(0.05,0.82,q),q,time,energy);
        naBoundary(col,p,vec2(0.0),vec2(1.30,0.72),NA_GREEN,q,energy);
        naLandscape(col,p,vec2(0.70,0.0),0.58,q,time,energy,NA_GREEN);
    }else if(mode==25){
        naBody(col,p,vec2(-0.82,-0.10),0.72,NA_GREEN,q,energy);
        naBrain(col,p,vec2(0.78,0.05),0.70,q,time,energy);
        naArrow(col,p,vec2(-0.28,0.0),vec2(0.24,0.05),NA_GOLD,q,energy);
        for(int i=0;i<5;i++){
            float fi=float(i),y=mix(-0.42,0.42,fi/4.0);
            lightFilament(col,p,vec2(-0.70,y*0.5),vec2(0.40,y*0.65),naScaleHue(fi/5.0),q*energy);
        }
    }else if(mode==26){
        naBody(col,p,vec2(0.0),0.78,NA_PEARL,q,energy);
        naNested(col,p,vec2(0.0),q,time,energy);
        naSwarm(col,p,vec2(0.0),0.58,12,0.55,q,time,energy*0.58);
        naBoundary(col,p,vec2(0.0),vec2(1.22,0.76),NA_GOLD,q,energy);
    }else if(mode==27){
        float left=abs(sdEllipse(p-vec2(-0.38,0.0),vec2(0.68,0.58)));
        float right=abs(sdEllipse(p-vec2(0.38,0.0),vec2(0.68,0.58)));
        col+=NA_CYAN*(aaStroke(left,0.009)*0.45+glow(left,0.052)*0.075)*q*energy;
        col+=NA_GOLD*(aaStroke(right,0.009)*0.45+glow(right,0.052)*0.075)*q*energy;
        naCompass(col,p,vec2(0.0),0.28,time*0.04,q,time,energy);
        naNested(col,p,vec2(0.0),q*0.54,time,energy);
    }else if(mode==28){
        vec3 hues[4]=vec3[4](NA_GREEN,NA_RED,NA_GOLD,NA_CYAN);
        for(int i=0;i<4;i++){
            float fi=float(i),y=mix(0.52,-0.52,fi/3.0);
            float card=abs(sdRoundBox(p-vec2(0.0,y),vec2(1.06,0.11),0.03));
            col+=hues[i]*(aaStroke(card,0.007)*0.44+glow(card,0.034)*0.045)*q*energy;
            naCompass(col,p,vec2(0.82,y),0.07,float(i),q,time,energy);
        }
    }else{
        naNested(col,p,vec2(-0.18,0.0),q,time,energy*0.68);
        naCompass(col,p,vec2(-0.95,0.0),0.22,0.0,q,time,energy);
        naLandscape(col,p,vec2(0.98,0.0),0.60,q,time,energy,NA_GOLD);
        naLightCone(col,p,vec2(-0.95,0.0),vec2(0.98,0.0),0.30,1.0,q,time,energy);
        naBoundary(col,p,vec2(0.0),vec2(1.48,0.78),NA_GREEN,q*0.62,energy);
        naSwarm(col,p,vec2(0.10,0.0),0.98,16,0.78,q,time,energy*0.48);
    }
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

void main(){
    vec2 uv=gl_FragCoord.xy/iResolution;
    vec2 p=aspectUV(uv,iResolution);
    fragColor=vec4(renderNavigationAtlas(p,uv,NAV_MODE,u,t,u_audioVolume,u_audioBeat),1.0);
}

#endif
