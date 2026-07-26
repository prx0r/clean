#ifndef QUEUE_MORPHOGENETIC_PORCELAIN_GLSL
#define QUEUE_MORPHOGENETIC_PORCELAIN_GLSL

const vec3 MP_PORCELAIN=vec3(0.94,0.89,0.78);
const vec3 MP_CREAM=vec3(0.62,0.54,0.42);
const vec3 MP_INK=vec3(0.012,0.020,0.045);
const vec3 MP_BLUE=vec3(0.015,0.22,0.80);
const vec3 MP_CYAN=vec3(0.01,0.86,0.95);
const vec3 MP_GOLD=vec3(1.20,0.50,0.045);
const vec3 MP_RED=vec3(0.98,0.035,0.12);
const vec3 MP_GREEN=vec3(0.04,0.74,0.34);
const vec3 MP_VIOLET=vec3(0.34,0.06,0.80);

vec3 mpBackground(vec2 p,vec2 uv,float time,int mode){
    float wash=fbmWarp(p*0.86+vec2(time*0.006,-time*0.004),time+71.0);
    float grainField=fbm(p*4.0+vec2(-time*0.008,time*0.005));
    vec3 col=mix(MP_INK,vec3(0.035,0.12,0.18),0.48+0.34*wash);
    col+=mix(MP_BLUE,MP_VIOLET,grainField)*pow(max(grainField-0.64,0.0),2.2)*0.10;
    float veins=pow(max(ridgedFbm(p*2.4)-0.70,0.0),2.0);
    col+=mix(MP_CYAN,MP_GOLD,wash)*veins*0.12;
    if(mode==14) col=mix(col,vec3(0.16,0.025,0.055),0.32);
    return col*(0.78+0.22*vignette(uv));
}
float mpPlanarianD(vec2 p,vec2 center,float scale,float angle,float splitHead){
    vec2 q=rot(-angle)*(p-center)/scale;
    float body=sdEllipse(q+vec2(0.08,0.0),vec2(0.78,0.22));
    float headA=sdCircle(q-vec2(0.58,0.10*splitHead),0.29);
    float headB=sdCircle(q-vec2(0.58,-0.10*splitHead),0.29);
    float tail=sdEllipse(q+vec2(0.70,0.0),vec2(0.30,0.13));
    return min(body,min(tail,min(headA,headB)))*scale;
}
void mpPlanarian(inout vec3 col,vec2 p,vec2 center,float scale,float angle,float splitHead,vec3 glaze,float q,float time,float energy){
    vec2 lp=rot(-angle)*(p-center)/scale;
    float d=mpPlanarianD(p,center,scale,angle,splitHead);
    float inside=aaFill(d);
    float marbling=fbmWarp(lp*2.5,time+17.0);
    col+=mix(MP_PORCELAIN,glaze,0.30+0.34*marbling)*inside*(0.48+0.12*marbling)*q;
    col+=glaze*(aaStroke(d,0.010)*0.62+glow(d,0.055)*0.11)*q*energy;
    float seam=abs(lp.y-0.035*sin(lp.x*7.0+time*0.12));
    col+=MP_GOLD*(1.0-smoothstep(0.010,0.028,seam))*inside*q*0.32*energy;
    vec2 eye1=center+rot(angle)*(scale*vec2(0.68,0.095+0.08*splitHead));
    vec2 eye2=center+rot(angle)*(scale*vec2(0.68,-0.095-0.08*splitHead));
    radiantNode(col,p,eye1,0.026*scale,MP_INK,q*2.0);
    radiantNode(col,p,eye2,0.026*scale,MP_INK,q*2.0);
    radiantNode(col,p,eye1,0.010*scale,MP_GOLD,q*energy);
    radiantNode(col,p,eye2,0.010*scale,MP_GOLD,q*energy);
}
void mpArrow(inout vec3 col,vec2 p,vec2 a,vec2 b,vec3 hue,float q,float energy){
    lightFilament(col,p,a,b,hue,q*energy);
    vec2 n=normalize(b-a),side=vec2(-n.y,n.x);
    lightFilament(col,p,b,b-n*0.12+side*0.06,hue,q*energy);
    lightFilament(col,p,b,b-n*0.12-side*0.06,hue,q*energy);
}
void mpTarget(inout vec3 col,vec2 p,vec2 center,float scale,float q,vec3 hue,float time,float energy){
    for(int i=0;i<11;i++){
        float fi=float(i),r=scale*(0.10+fi*0.082);
        vec2 lp=(p-center)/vec2(1.0,0.62);
        float a=atan(lp.y,lp.x);
        float d=abs(length(lp)-r-0.012*sin(a*6.0+fi+time*0.10));
        col+=hue*(aaStroke(d,0.006)*0.38+glow(d,0.034)*0.055)*q*energy*(1.0-fi*0.055);
    }
    radiantNode(col,p,center,0.065*scale,hue,q*energy);
}
void mpContours(inout vec3 col,vec2 p,vec2 center,float scale,float depth,float q,float time,float energy){
    float terrain=length((p-center)/vec2(1.0,0.65))/scale;
    terrain+=0.16*fbmWarp((p-center)*3.2,time)-0.08;
    float bands=abs(fract(terrain*10.0-time*0.025)-0.5);
    vec3 hue=mix(MP_BLUE,MP_GOLD,saturate(terrain*0.65));
    col+=hue*(1.0-smoothstep(0.035,0.095,bands))*0.17*q*energy;
    col-=MP_INK*(1.0-smoothstep(0.0,1.2,terrain))*depth*0.18*q;
}
void mpCell(inout vec3 col,vec2 p,vec2 c,float r,float phase,vec3 hue,float q,float time,float energy){
    vec2 lp=(p-c)/r;
    float a=atan(lp.y,lp.x);
    float d=(length(lp)-1.0-0.06*sin(a*6.0+phase+time*0.1))*r;
    col+=mix(MP_PORCELAIN,hue,0.34)*aaFill(d)*q*0.30;
    col+=hue*(aaStroke(d,0.006)*0.47+glow(d,0.030)*0.055)*q*energy;
    radiantNode(col,p,c,r*0.13,MP_GOLD,q*energy*0.55);
}
void mpCollective(inout vec3 col,vec2 p,vec2 center,float radius,float q,float time,float energy,bool connected){
    vec2 points[12];
    for(int i=0;i<12;i++){
        float fi=float(i),a=TAU*fi/12.0+0.08*sin(time*0.08+fi);
        points[i]=center+vec2(cos(a),sin(a))*vec2(radius,radius*0.62)*(0.55+0.30*hash11(fi+9.0));
        vec3 hue=mix(MP_BLUE,MP_GREEN,fi/11.0);
        mpCell(col,p,points[i],0.095,fi,hue,q,time,energy);
    }
    if(connected) for(int i=0;i<12;i++){
        lightFilament(col,p,points[i],points[(i+1)%12],MP_CYAN,q*energy*0.36);
        if(i%3==0) lightFilament(col,p,points[i],center,MP_GOLD,q*energy*0.32);
    }
    mpCell(col,p,center,0.15,0.0,MP_GOLD,q,time,energy);
}
void mpBreakLine(inout vec3 col,vec2 p,float x,float q,float time,float energy){
    float y=0.58*sin((p.x-x)*8.0+time*0.18)*exp(-abs(p.x-x)*2.0);
    float d=abs(p.y-y);
    col+=MP_RED*(aaStroke(d,0.009)*0.55+glow(d,0.060)*0.10)*q*energy;
}
void mpMorphedForm(inout vec3 col,vec2 p,vec2 center,float scale,float seed,vec3 hue,float q,float time,float energy){
    vec2 lp=(p-center)/scale;
    float a=atan(lp.y,lp.x);
    float radial=0.52+0.14*sin(a*(3.0+mod(seed,4.0))+seed)+0.07*sin(a*7.0-time*0.12);
    float d=(length(lp)-radial)*scale;
    col+=mix(MP_PORCELAIN,hue,0.42)*aaFill(d)*q*0.32;
    col+=hue*(aaStroke(d,0.008)*0.56+glow(d,0.048)*0.085)*q*energy;
    radiantNode(col,p,center,scale*0.06,MP_GOLD,q*energy);
}

vec3 renderMorphogeneticPorcelain(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat){
    float q=easeInOut(progress),energy=audioEnergy(volume,beat);
    vec3 col=mpBackground(p,uv,time,mode);

    if(mode==0){
        mpPlanarian(col,p,vec2(-0.75,0.0),0.72,0.0,0.0,MP_BLUE,q,time,energy);
        float cut=abs(p.x+0.16);
        col+=MP_RED*(aaStroke(cut,0.012)*0.62+glow(cut,0.055)*0.10)*q*energy*(1.0-smoothstep(0.001,0.38,abs(p.y)));
        vec2 question=vec2(0.90,0.0);
        mpTarget(col,p,question,0.46,q,MP_GOLD,time,energy);
        mpArrow(col,p,vec2(-0.05,0.0),vec2(0.48,0.0),MP_GOLD,q,energy);
    }else if(mode==1){
        vec2 origins[3]=vec2[3](vec2(-1.10,0.52),vec2(-1.08,0.0),vec2(-1.10,-0.52));
        vec2 ends[3]=vec2[3](vec2(0.70,0.52),vec2(0.70,0.0),vec2(0.70,-0.52));
        for(int i=0;i<3;i++){
            float grow=saturate(q*1.35-float(i)*0.10);
            mpMorphedForm(col,p,origins[i],0.28,float(i),MP_RED,grow,time,energy);
            mpArrow(col,p,origins[i]+vec2(0.28,0),ends[i]-vec2(0.48,0),MP_GREEN,grow,energy);
            mpPlanarian(col,p,ends[i],0.48,0.0,0.0,MP_BLUE,grow,time,energy);
        }
    }else if(mode==2){
        float blueprint=abs(sdRoundBox(p-vec2(-0.88,0.0),vec2(0.55,0.48),0.05));
        col+=MP_INK*aaFill(blueprint)*0.22;
        for(int i=0;i<6;i++){
            float fi=float(i),x=-1.22+mod(fi,3.0)*0.34,y=0.25-floor(fi/3.0)*0.48;
            float d=abs(sdRoundBox(p-vec2(x,y),vec2(0.12,0.10),0.015));
            col+=MP_BLUE*aaStroke(d,0.006)*0.60*q;
        }
        mpContours(col,p,vec2(0.80,0.0),0.74,1.0,q,time,energy);
        mpTarget(col,p,vec2(0.80,0.0),0.56,q,MP_GOLD,time,energy);
        mpArrow(col,p,vec2(-0.22,0.0),vec2(0.25,0.0),MP_GREEN,q,energy);
    }else if(mode==3){
        mpCollective(col,p,vec2(0.0),0.92,q,time,energy,true);
        float boundary=abs(length(p/vec2(1.0,0.65))-1.18);
        col+=MP_GOLD*(aaStroke(boundary,0.010)*0.43+glow(boundary,0.055)*0.08)*q*energy;
    }else if(mode==4){
        mpCollective(col,p,vec2(0.0),0.92,q,time,energy,false);
        for(int i=0;i<9;i++){
            float fi=float(i),a=TAU*fi/9.0;
            vec2 a0=vec2(cos(a),sin(a))*vec2(0.42,0.27);
            vec2 b0=vec2(cos(a+0.44),sin(a+0.44))*vec2(0.92,0.57);
            lightFilament(col,p,a0,b0,MP_CYAN,q*energy);
            radiantNode(col,p,mix(a0,b0,fract(time*0.08+fi/9.0)),0.025,MP_GOLD,q*energy);
        }
    }else if(mode==5){
        mpPlanarian(col,p,vec2(0.0),0.94,0.0,0.0,MP_BLUE,q,time,energy*0.75);
        mpContours(col,p,vec2(-0.30,0.0),0.84,0.5,q,time,energy);
        radiantNode(col,p,vec2(-0.70,0.0),0.07,MP_CYAN,q*energy);
        radiantNode(col,p,vec2(0.68,0.0),0.07,MP_GOLD,q*energy);
    }else if(mode==6){
        mpPlanarian(col,p,vec2(-0.78,0.0),0.58,0.0,0.0,MP_BLUE,q,time,energy);
        mpPlanarian(col,p,vec2(0.84,0.0),0.58,0.0,0.0,MP_GREEN,q,time,energy);
        mpContours(col,p,vec2(-0.78,0.0),0.52,0.4,q,time,energy);
        mpContours(col,p,vec2(0.84,0.0),0.52,0.4,q,time,energy);
        mpArrow(col,p,vec2(-0.17,0.0),vec2(0.22,0.0),MP_GOLD,q,energy);
        float wand=sdSegment(p,vec2(0.0,-0.60),vec2(0.0,0.60));
        col+=MP_VIOLET*(aaStroke(wand,0.012)*0.58+glow(wand,0.055)*0.09)*q*energy;
    }else if(mode==7){
        mpPlanarian(col,p,vec2(0.0),0.95,0.0,mix(0.0,1.0,q),MP_RED,q,time,energy);
        vec2 crown=vec2(0.58,0.0);
        mpTarget(col,p,crown,0.42,q,MP_RED,time,energy);
    }else if(mode==8){
        mpPlanarian(col,p,vec2(-0.82,0.0),0.62,0.0,1.0,MP_RED,q,time,energy);
        mpTarget(col,p,vec2(0.78,0.0),0.60,q,MP_GOLD,time,energy);
        mpArrow(col,p,vec2(-0.12,0.0),vec2(0.24,0.0),MP_VIOLET,q,energy);
        for(int i=0;i<5;i++){
            float fi=float(i),a=TAU*fi/5.0;
            radiantNode(col,p,vec2(0.78,0.0)+vec2(cos(a),sin(a))*vec2(0.40,0.24),0.032,MP_RED,q*energy);
        }
    }else if(mode==9){
        mpPlanarian(col,p,vec2(0.0),0.92,0.0,mix(1.0,0.0,q),mix(MP_RED,MP_BLUE,q),q,time,energy);
        mpContours(col,p,vec2(0.0),0.82,0.4,q,time,energy);
        float reset=abs(length(p/vec2(1.0,0.62))-mix(1.24,0.30,q));
        col+=MP_GREEN*(aaStroke(reset,0.012)*0.60+glow(reset,0.070)*0.11)*q*energy;
    }else if(mode==10){
        mpContours(col,p,vec2(0.80,0.0),0.72,0.6,q,time,energy);
        mpTarget(col,p,vec2(0.80,0.0),0.58,q,MP_GOLD,time,energy);
        mpMorphedForm(col,p,vec2(-1.02,-0.44),0.28,3.0,MP_RED,q,time,energy);
        vec2 steps[4]=vec2[4](vec2(-0.55,-0.22),vec2(-0.08,0.12),vec2(0.36,0.28),vec2(0.74,0.04));
        vec2 last=vec2(-0.78,-0.34);
        for(int i=0;i<4;i++){
            mpArrow(col,p,last,steps[i],mix(MP_RED,MP_GREEN,float(i)/3.0),q,energy);
            mpCell(col,p,steps[i],0.10,float(i),mix(MP_RED,MP_GREEN,float(i)/3.0),q,time,energy);
            last=steps[i];
        }
    }else if(mode==11){
        mpPlanarian(col,p,vec2(0.0),0.98,0.0,0.0,MP_GREEN,q,time,energy);
        mpTarget(col,p,vec2(0.0),0.76,q,MP_GOLD,time,energy);
        float stop=abs(length((p-vec2(0.62,0.0))/vec2(1.0,0.72))-0.20);
        col+=MP_RED*(aaStroke(stop,0.014)*0.62+glow(stop,0.065)*0.11)*q*energy;
        float bar=abs(p.x-0.62);
        col+=MP_RED*aaStroke(bar,0.010)*q;
    }else if(mode==12){
        for(int i=0;i<4;i++){
            float fi=float(i),r=0.20+fi*0.23;
            float ring=abs(length(p/vec2(1.0,0.64))-r);
            vec3 hue=mix(MP_BLUE,MP_GOLD,fi/3.0);
            col+=hue*(aaStroke(ring,0.009)*0.48+glow(ring,0.055)*0.075)*q*energy;
            for(int j=0;j<5;j++){
                float fj=float(j),a=TAU*fj/5.0+fi*0.9;
                mpCell(col,p,vec2(cos(a),sin(a))*vec2(r,r*0.64),0.055+fi*0.012,fj,hue,q,time,energy*0.58);
            }
        }
    }else if(mode==13){
        mpCollective(col,p,vec2(-0.62,0.0),0.62,q,time,energy,true);
        mpBreakLine(col,p,-0.12,q,time,energy);
        for(int i=0;i<8;i++){
            float fi=float(i),a=TAU*fi/8.0;
            vec2 c=vec2(0.68,0.0)+vec2(cos(a),sin(a))*vec2(0.52,0.34);
            mpCell(col,p,c,0.09,fi,MP_RED,q,time,energy);
            mpArrow(col,p,vec2(-0.08,0.0),c,MP_RED,q,energy*0.38);
        }
    }else if(mode==14){
        mpCollective(col,p,vec2(-0.58,0.0),0.68,q,time,energy,true);
        vec2 rogue=vec2(0.74,0.04);
        for(int i=0;i<11;i++){
            float fi=float(i),a=TAU*fi/11.0;
            vec2 c=rogue+vec2(cos(a),sin(a))*vec2(0.42,0.30)*(0.42+0.35*hash11(fi));
            mpCell(col,p,c,0.105,fi,MP_RED,q,time,energy);
        }
        float exile=abs(length((p-rogue)/vec2(1.0,0.72))-0.60);
        col+=MP_RED*(aaStroke(exile,0.012)*0.55+glow(exile,0.07)*0.10)*q*energy;
    }else if(mode==15){
        vec2 rogue=vec2(-0.76,0.0);
        mpCollective(col,p,rogue,0.54,q,time,energy,false);
        mpArrow(col,p,vec2(-0.18,0.0),vec2(0.28,0.0),MP_GREEN,q,energy);
        mpCollective(col,p,vec2(0.78,0.0),0.58,q,time,energy,true);
        float embrace=abs(length((p-vec2(0.78,0.0))/vec2(1.0,0.65))-0.78);
        col+=MP_GREEN*(aaStroke(embrace,0.010)*0.48+glow(embrace,0.06)*0.09)*q*energy;
    }else if(mode==16){
        mpContours(col,p,vec2(-0.56,-0.06),1.06,0.75,q,time,energy);
        mpContours(col,p,vec2(0.86,0.12),0.62,0.55,q,time,energy);
        vec2 pathA=vec2(-1.28,0.58),pathB=vec2(0.82,0.04);
        mpArrow(col,p,pathA,pathB,MP_GOLD,q,energy);
        radiantNode(col,p,pathA,0.065,MP_RED,q*energy);
        radiantNode(col,p,pathB,0.085,MP_GREEN,q*energy);
    }else if(mode==17){
        for(int i=0;i<9;i++){
            float fi=float(i),a=TAU*fi/9.0+time*0.035;
            vec2 c=vec2(cos(a),sin(a))*vec2(0.95,0.55);
            mpMorphedForm(col,p,c,0.20,fi,mix(MP_BLUE,MP_GREEN,fi/8.0),q,time,energy);
            if(i>0){
                float pa=TAU*(fi-1.0)/9.0+time*0.035;
                lightFilament(col,p,vec2(cos(pa),sin(pa))*vec2(0.95,0.55),c,MP_GOLD,q*energy*0.36);
            }
        }
        mpTarget(col,p,vec2(0.0),0.42,q,MP_CYAN,time,energy);
    }else if(mode==18){
        mpContours(col,p,vec2(0.56,0.0),0.86,0.55,q,time,energy);
        vec2 starts[4]=vec2[4](vec2(-1.28,0.60),vec2(-1.34,0.18),vec2(-1.22,-0.24),vec2(-0.96,-0.62));
        for(int i=0;i<4;i++){
            vec2 target=vec2(0.56,0.0)+vec2(0.12*cos(float(i)),0.08*sin(float(i)));
            mpArrow(col,p,starts[i],target,mix(MP_RED,MP_GREEN,float(i)/3.0),q,energy);
            mpMorphedForm(col,p,starts[i],0.16,float(i),MP_VIOLET,q,time,energy);
        }
        mpTarget(col,p,vec2(0.56,0.0),0.48,q,MP_GOLD,time,energy);
    }else if(mode==19){
        mpCollective(col,p,vec2(0.0),0.84,q,time,energy,true);
        for(int i=0;i<5;i++){
            float fi=float(i),r=0.32+fi*0.20;
            float b=abs(length(p/vec2(1.0,0.64))-r);
            col+=mix(MP_BLUE,MP_GOLD,fi/4.0)*(aaStroke(b,0.007)*0.32+glow(b,0.035)*0.042)*q*energy;
        }
    }else if(mode==20){
        vec3 verdicts[4]=vec3[4](MP_GREEN,MP_RED,MP_GOLD,MP_BLUE);
        for(int i=0;i<4;i++){
            float fi=float(i),x=mix(-1.15,1.15,fi/3.0);
            float vessel=abs(sdRoundBox(p-vec2(x,0.0),vec2(0.22,0.54),0.06));
            col+=verdicts[i]*(aaStroke(vessel,0.009)*0.50+glow(vessel,0.05)*0.07)*q*energy;
            mpMorphedForm(col,p,vec2(x,0.0),0.17,fi,verdicts[i],q,time,energy);
        }
    }else if(mode==21){
        float left=abs(sdEllipse(p-vec2(-0.38,0.0),vec2(0.68,0.58)));
        float right=abs(sdEllipse(p-vec2(0.38,0.0),vec2(0.68,0.58)));
        col+=MP_BLUE*(aaStroke(left,0.010)*0.48+glow(left,0.055)*0.08)*q*energy;
        col+=MP_GOLD*(aaStroke(right,0.010)*0.48+glow(right,0.055)*0.08)*q*energy;
        mpPlanarian(col,p,vec2(0.0),0.56,0.0,0.0,MP_GREEN,q,time,energy);
        mpTarget(col,p,vec2(0.0),0.50,q,MP_CYAN,time,energy);
    }else{
        mpContours(col,p,vec2(0.56,0.0),0.98,0.68,q,time,energy);
        mpTarget(col,p,vec2(0.56,0.0),0.62,q,MP_GOLD,time,energy);
        mpPlanarian(col,p,vec2(-0.92,-0.34),0.42,0.18,0.0,MP_BLUE,q,time,energy);
        vec2 route[3]=vec2[3](vec2(-0.36,-0.12),vec2(0.05,0.30),vec2(0.48,0.05));
        vec2 last=vec2(-0.56,-0.28);
        for(int i=0;i<3;i++){
            mpArrow(col,p,last,route[i],mix(MP_BLUE,MP_GREEN,float(i)/2.0),q,energy);
            mpCell(col,p,route[i],0.09,float(i),MP_GREEN,q,time,energy);
            last=route[i];
        }
        float horizon=abs(p.y+0.70-0.06*sin(p.x*3.0+time*0.08));
        col+=MP_CYAN*(aaStroke(horizon,0.008)*0.40+glow(horizon,0.050)*0.06)*q*energy;
    }
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
