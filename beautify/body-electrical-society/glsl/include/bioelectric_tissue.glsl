#ifndef QUEUE_BIOELECTRIC_TISSUE_GLSL
#define QUEUE_BIOELECTRIC_TISSUE_GLSL

const vec3 BE_INK=vec3(0.002,0.012,0.022);
const vec3 BE_DEEP=vec3(0.006,0.055,0.075);
const vec3 BE_CYAN=vec3(0.00,1.18,1.20);
const vec3 BE_BLUE=vec3(0.02,0.30,1.12);
const vec3 BE_PINK=vec3(1.14,0.04,0.45);
const vec3 BE_VIOLET=vec3(0.48,0.08,1.18);
const vec3 BE_GOLD=vec3(1.35,0.62,0.07);
const vec3 BE_GREEN=vec3(0.08,1.12,0.48);
const vec3 BE_PEARL=vec3(0.84,1.04,1.06);

vec3 beBackground(vec2 p,vec2 uv,float time,int mode){
    float tissue=fbmWarp(p*1.15+vec2(time*0.008,-time*0.011),time+31.0);
    float threads=ridgedFbm(p*3.2+vec2(-time*0.014,time*0.006));
    vec3 col=mix(BE_INK,BE_DEEP,0.30+0.52*tissue);
    col+=mix(BE_BLUE,BE_CYAN,tissue)*pow(max(threads-0.63,0.0),2.8)*0.065;
    float dust=pow(max(noise21(p*28.0+time*0.02)-0.76,0.0),3.0);
    col+=BE_PEARL*dust*0.32;
    if(mode==13||mode==14) col+=BE_PINK*pow(max(tissue-0.61,0.0),2.0)*0.06;
    return col*(0.68+0.32*vignette(uv));
}
vec3 bePotential(float v){
    vec3 cold=mix(BE_BLUE,BE_CYAN,saturate(v*2.0));
    vec3 hot=mix(BE_PINK,BE_GOLD,saturate((v-0.48)*2.0));
    return mix(cold,hot,smoothstep(0.38,0.62,v));
}
float beCellDistance(vec2 p,vec2 center,vec2 radius,float phase,float time){
    vec2 q=(p-center)/radius;
    float a=atan(q.y,q.x);
    float r=length(q);
    float ripple=0.045*sin(a*5.0+phase+time*0.18)+0.024*sin(a*9.0-phase*1.7-time*0.11);
    return (r-1.0-ripple)*min(radius.x,radius.y);
}
void beCell(inout vec3 col,vec2 p,vec2 center,vec2 radius,float voltage,float phase,float time,float energy){
    float d=beCellDistance(p,center,radius,phase,time);
    vec3 hue=bePotential(voltage);
    float inside=aaFill(d);
    col+=hue*(aaStroke(d,0.007)*0.42+glow(d,0.045)*0.078)*energy;
    col+=mix(BE_DEEP,hue,0.42)*inside*(0.045+0.045*voltage)*energy;
    vec2 nucleus=center+radius*vec2(0.16*sin(phase),0.12*cos(phase*1.3));
    float nd=sdEllipse(p-nucleus,radius*vec2(0.18,0.15));
    col+=mix(BE_VIOLET,hue,0.46)*(aaStroke(nd,0.004)*0.32+glow(nd,0.022)*0.055+aaFill(nd)*0.028)*energy;
}
void beJunction(inout vec3 col,vec2 p,vec2 a,vec2 b,float flow,vec3 hue,float time,float energy){
    vec2 axis=b-a;
    vec2 normal=normalize(vec2(-axis.y,axis.x));
    vec2 mid=mix(a,b,0.5);
    lightFilament(col,p,a,b,hue,energy*0.56);
    for(int i=0;i<5;i++){
        float fi=float(i);
        float travel=fract(flow+fi/5.0+time*0.055);
        vec2 c=mix(a,b,travel)+normal*0.012*sin(fi*2.7+time);
        radiantNode(col,p,c,0.018,hue,energy*(0.55+0.45*sin(PI*travel)));
    }
    float gate=abs(sdSegment(p,mid-normal*0.055,mid+normal*0.055));
    col+=BE_PEARL*(aaStroke(gate,0.004)*0.35+glow(gate,0.020)*0.045)*energy;
}
void bePotentialContours(inout vec3 col,vec2 p,vec2 a,vec2 b,float q,float time,float energy){
    float va=0.58/(0.12+dot(p-a,p-a));
    float vb=0.48/(0.12+dot(p-b,p-b));
    float field=va-vb+0.12*fbm(p*3.1+time*0.02);
    float bands=abs(fract(field*1.25-time*0.045)-0.5);
    vec3 hue=bePotential(saturate(field*0.25+0.5));
    col+=hue*(1.0-smoothstep(0.035,0.11,bands))*0.15*q*energy;
}
void beSheet(inout vec3 col,vec2 p,float voltageBias,float fracture,float q,float time,float energy){
    for(int y=-2;y<=2;y++) for(int x=-4;x<=4;x++){
        float fy=float(y),fx=float(x);
        vec2 c=vec2(fx*0.36+(mod(fy,2.0))*0.18,fy*0.31);
        c.x+=0.025*sin(time*0.08+fy*2.0);
        float anomaly=hash11(fx*11.0+fy*37.0);
        float v=saturate(0.26+voltageBias+0.28*sin(fx*0.85+fy*1.3+time*0.12));
        if(anomaly<fracture) v=0.98;
        vec2 r=vec2(0.205,0.185)*(0.93+0.08*anomaly);
        beCell(col,p,c,r,v,fx*1.3+fy*0.7,time,energy*(0.64+0.36*q));
        if(x<4 && anomaly>=fracture) beJunction(col,p,c+vec2(0.19,0.0),c+vec2(0.34,0.0),q,bePotential(v),time,energy*0.30);
    }
}
void beVoltageRibbon(inout vec3 col,vec2 p,float y,float amplitude,float frequency,float q,vec3 hue,float time,float energy){
    float wave=y+amplitude*sin(p.x*frequency-time*(0.35+frequency*0.04));
    float d=abs(p.y-wave);
    col+=hue*(aaStroke(d,0.006)*0.52+glow(d,0.043)*0.075)*q*energy;
}
void beEmbryo(inout vec3 col,vec2 p,float q,float time,float energy){
    vec2 lp=p*rot(0.10*sin(time*0.08));
    float outer=sdEllipse(lp,vec2(0.72,0.66));
    float left=sdCircle(lp-vec2(-0.22,0.05),0.34);
    float right=sdCircle(lp-vec2(0.22,0.05),0.34);
    float cleft=max(-sdEllipse(lp-vec2(0.0,0.25),vec2(0.12,0.36)),min(left,right));
    float body=min(outer,cleft);
    col+=BE_PEARL*(aaStroke(body,0.009)*0.58+glow(body,0.055)*0.10+aaFill(body)*0.025)*q*energy;
    bePotentialContours(col,lp,vec2(-0.28,0.12),vec2(0.28,-0.10),q,time,energy);
    for(int i=0;i<10;i++){
        float fi=float(i),a=TAU*fi/10.0;
        vec2 c=vec2(cos(a),sin(a))*vec2(0.50,0.44);
        beCell(col,lp,c,vec2(0.12),0.5+0.4*sin(a*2.0),fi,time,energy*0.42*q);
    }
}
void beEye(inout vec3 col,vec2 p,vec2 center,float size,float q,float time,float energy){
    vec2 lp=(p-center)/size;
    float lid=abs(sdVesica(lp,0.70,0.42));
    col+=BE_PEARL*(aaStroke(lid,0.018)*0.56+glow(lid,0.075)*0.10)*q*energy;
    float iris=sdCircle(lp,0.25);
    col+=BE_CYAN*(aaStroke(iris,0.020)*0.62+glow(iris,0.085)*0.13+aaFill(iris)*0.055)*q*energy;
    float pupil=sdCircle(lp,0.082+0.018*sin(time*0.6));
    col+=BE_INK*aaFill(pupil)*1.4;
    radiantNode(col,lp,vec2(0.0),0.065,BE_GOLD,q*energy);
}
void beGene(inout vec3 col,vec2 p,vec2 center,float scale,float q,float time,float energy){
    vec2 lp=(p-center)/scale;
    for(int i=0;i<20;i++){
        float fi=float(i),x=mix(-0.68,0.68,fi/19.0);
        float y=0.24*sin(x*9.0-time*0.55);
        vec2 a=center+scale*vec2(x,y);
        vec2 b=center+scale*vec2(x,-y);
        vec3 hue=mix(BE_CYAN,BE_PINK,fi/19.0);
        if(i<19){
            float nx=mix(-0.68,0.68,(fi+1.0)/19.0);
            lightFilament(col,p,a,center+scale*vec2(nx,0.24*sin(nx*9.0-time*0.55)),hue,q*energy*0.68);
            lightFilament(col,p,b,center+scale*vec2(nx,-0.24*sin(nx*9.0-time*0.55)),hue,q*energy*0.68);
        }
        if(i%2==0) lightFilament(col,p,a,b,BE_PEARL,q*energy*0.45);
    }
}
void beArrow(inout vec3 col,vec2 p,vec2 a,vec2 b,vec3 hue,float q,float energy){
    lightFilament(col,p,a,b,hue,q*energy);
    vec2 n=normalize(b-a),side=vec2(-n.y,n.x);
    lightFilament(col,p,b,b-n*0.12+side*0.065,hue,q*energy);
    lightFilament(col,p,b,b-n*0.12-side*0.065,hue,q*energy);
}
void beConcentricBody(inout vec3 col,vec2 p,float q,float time,float energy){
    for(int i=0;i<12;i++){
        float fi=float(i),r=0.12+fi*0.075;
        vec2 lp=p/vec2(1.0,0.70);
        float a=atan(lp.y,lp.x);
        float d=abs(length(lp)-r-0.018*sin(a*5.0+fi+time*0.12));
        vec3 hue=bePotential(fi/11.0);
        col+=hue*(aaStroke(d,0.006)*0.40+glow(d,0.034)*0.052)*q*energy*(1.0-fi*0.045);
    }
}

vec3 renderBioelectricTissue(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat){
    float q=easeInOut(progress),energy=audioEnergy(volume,beat);
    vec3 col=beBackground(p,uv,time,mode);

    if(mode==0){
        vec2 c=vec2(0.0);
        beCell(col,p,c,vec2(0.92,0.64),0.52,0.0,time,energy);
        bePotentialContours(col,p,vec2(-0.55,0.0),vec2(0.55,0.0),q,time,energy);
        for(int i=0;i<18;i++){
            float fi=float(i),a=TAU*fi/18.0;
            vec2 n=c+vec2(cos(a),sin(a))*vec2(0.92,0.64);
            radiantNode(col,p,n,0.025,i%2==0?BE_CYAN:BE_PINK,q*energy);
        }
    }else if(mode==1){
        beCell(col,p,vec2(0.0),vec2(1.18,0.70),0.45,0.0,time,energy*0.45);
        for(int i=0;i<7;i++){
            float fi=float(i),y=mix(-0.46,0.46,fi/6.0);
            beVoltageRibbon(col,p,y,0.065+0.02*fi,2.2+fi*0.38,q,bePotential(fi/6.0),time,energy);
        }
        float spikeX=mix(-1.35,1.35,q);
        col+=BE_PEARL*exp(-pow((p.x-spikeX)/0.035,2.0))*0.16*energy;
    }else if(mode==2){
        beCell(col,p,vec2(0.0),vec2(1.06,0.68),0.42,0.0,time,energy*0.62);
        for(int i=0;i<14;i++){
            float fi=float(i),a=TAU*fi/14.0;
            vec2 n=vec2(cos(a),sin(a))*vec2(1.06,0.68);
            float open=smoothstep(0.26,0.72,0.5+0.5*sin(fi*2.1+time*0.65));
            radiantNode(col,p,n,0.025+0.028*open,bePotential(fi/13.0),q*energy);
            vec2 inner=n*0.72;
            beArrow(col,p,n*1.10,inner,bePotential(fi/13.0),q*open,energy);
        }
    }else if(mode==3){
        vec2 centers[6]=vec2[6](vec2(-1.05,0.34),vec2(-0.36,0.40),vec2(0.38,0.32),vec2(1.05,0.38),vec2(-0.72,-0.36),vec2(0.43,-0.38));
        for(int i=0;i<6;i++) beCell(col,p,centers[i],vec2(0.34,0.28),0.2+0.13*float(i),float(i),time,energy*0.72);
        beJunction(col,p,centers[0]+vec2(0.32,0),centers[1]-vec2(0.32,0),q,BE_CYAN,time,energy);
        beJunction(col,p,centers[1]+vec2(0.32,0),centers[2]-vec2(0.32,0),q,BE_GOLD,time,energy);
        beJunction(col,p,centers[2]+vec2(0.32,0),centers[3]-vec2(0.32,0),q,BE_PINK,time,energy);
        beJunction(col,p,centers[1]-vec2(0.1,0.24),centers[4]+vec2(0.1,0.24),q,BE_GREEN,time,energy);
        beJunction(col,p,centers[2]-vec2(0.1,0.24),centers[5]+vec2(0.1,0.24),q,BE_VIOLET,time,energy);
    }else if(mode==4){
        beSheet(col,p,0.28,0.0,q,time,energy);
        float sync=0.5+0.5*sin(time*0.45);
        col+=BE_GOLD*exp(-pow((p.x-mix(-1.55,1.55,sync))/0.12,2.0))*0.08*q*energy;
    }else if(mode==5){
        bePotentialContours(col,p,vec2(-0.62,0.0),vec2(0.62,0.0),q,time,energy);
        for(int i=0;i<13;i++){
            float fi=float(i),r=0.11+fi*0.075;
            float d=abs(length(p/vec2(1.0,0.64))-r);
            col+=bePotential(fi/12.0)*(aaStroke(d,0.006)*0.36+glow(d,0.030)*0.045)*q*energy;
        }
        radiantNode(col,p,vec2(-0.62,0.0),0.09,BE_CYAN,q*energy);
        radiantNode(col,p,vec2(0.62,0.0),0.09,BE_PINK,q*energy);
    }else if(mode==6){
        beSheet(col,p,0.12,0.0,q,time,energy*0.64);
        float memory=abs(length((p-vec2(0.30,0.02))/vec2(0.84,0.48))-0.56);
        col+=BE_GOLD*(aaStroke(memory,0.015)*0.65+glow(memory,0.075)*0.13)*q*energy;
        for(int i=0;i<8;i++){
            float fi=float(i),a=TAU*fi/8.0;
            radiantNode(col,p,vec2(0.30,0.02)+vec2(cos(a),sin(a))*vec2(0.47,0.27),0.035,BE_GOLD,q*energy);
        }
    }else if(mode==7){
        beEmbryo(col,p,q,time,energy);
        float pre=abs(p.x+0.08*sin(p.y*7.0+time*0.18));
        col+=mix(BE_CYAN,BE_PINK,smoothstep(-0.5,0.5,p.y))*(1.0-smoothstep(0.018,0.07,pre))*q*0.25*energy;
    }else if(mode==8){
        beCell(col,p,vec2(-0.92,0.0),vec2(0.40,0.48),0.68,0.0,time,energy);
        beGene(col,p,vec2(0.78,0.0),0.86,q,time,energy);
        beArrow(col,p,vec2(-0.48,0.0),vec2(0.10,0.0),BE_GOLD,q,energy);
        bePotentialContours(col,p,vec2(-0.92,0.0),vec2(0.78,0.0),q,time,energy*0.60);
    }else if(mode==9){
        vec2 center=vec2(-1.18,0.0);
        beCell(col,p,center,vec2(0.32),0.55,0.0,time,energy);
        vec2 choices[4]=vec2[4](vec2(0.72,0.58),vec2(1.25,0.16),vec2(0.82,-0.54),vec2(0.20,-0.05));
        for(int i=0;i<4;i++){
            vec3 hue=i==0?BE_GREEN:(i==1?BE_GOLD:(i==2?BE_PINK:BE_CYAN));
            beArrow(col,p,center+vec2(0.30,0.0),choices[i],hue,q,energy);
            beCell(col,p,choices[i],vec2(0.18),float(i)/3.0,float(i),time,energy*0.64);
        }
    }else if(mode==10){
        beEmbryo(col,p-vec2(-0.62,0.0),q,time,energy*0.58);
        beEye(col,p,vec2(0.86,0.04),0.62,q,time,energy);
        beArrow(col,p,vec2(-0.10,0.0),vec2(0.42,0.04),BE_GOLD,q,energy);
    }else if(mode==11){
        vec2 poles[2]=vec2[2](vec2(-1.10,0.0),vec2(1.10,0.0));
        radiantNode(col,p,poles[0],0.11,BE_CYAN,q*energy);
        radiantNode(col,p,poles[1],0.11,BE_PINK,q*energy);
        bePotentialContours(col,p,poles[0],poles[1],q,time,energy);
        beConcentricBody(col,p,q,time,energy);
        beArrow(col,p,poles[0],poles[1],BE_GOLD,q,energy*0.72);
    }else if(mode==12){
        beSheet(col,p,0.30,0.0,q,time,energy*0.75);
        for(int i=0;i<5;i++){
            float fi=float(i),a=TAU*fi/5.0+time*0.06;
            float d=abs(sdEllipse(p,vec2(0.34+fi*0.23,0.20+fi*0.13)));
            col+=BE_GREEN*(aaStroke(d,0.007)*0.28+glow(d,0.035)*0.035)*q*energy;
        }
    }else if(mode==13){
        beSheet(col,p,0.0,0.30,q,time,energy);
        vec2 tear=vec2(0.18,-0.06);
        radiantNode(col,p,tear,0.15,BE_PINK,q*energy);
        for(int i=0;i<9;i++){
            float fi=float(i),a=TAU*fi/9.0;
            vec2 end=tear+vec2(cos(a),sin(a))*vec2(0.70,0.45);
            lightFilament(col,p,tear,end,BE_PINK,q*energy*0.72);
        }
    }else if(mode==14){
        beSheet(col,p,0.10,0.18,q,time,energy*0.72);
        float lesion=length((p-vec2(0.28,0.0))/vec2(1.0,0.68));
        float chaos=fbmWarp((p-vec2(0.28,0.0))*4.0,time);
        col+=mix(BE_PINK,BE_VIOLET,chaos)*(1.0-smoothstep(0.25,0.72,lesion))*pow(chaos,2.0)*0.55*q*energy;
        float boundary=abs(lesion-0.62);
        col+=BE_PINK*(aaStroke(boundary,0.012)*0.48+glow(boundary,0.080)*0.12)*q*energy;
    }else if(mode==15){
        beSheet(col,p,mix(0.0,0.36,q),mix(0.28,0.0,q),q,time,energy);
        float healing=abs(length((p-vec2(0.28,0.0))/vec2(1.0,0.68))-mix(0.74,0.18,q));
        col+=BE_GREEN*(aaStroke(healing,0.012)*0.62+glow(healing,0.075)*0.11)*q*energy;
    }else if(mode==16){
        vec2 upper=p-vec2(0.0,0.38),lower=p-vec2(0.0,-0.38);
        for(int i=0;i<8;i++){
            float fi=float(i),x=mix(-1.25,1.25,fi/7.0);
            vec2 a=vec2(x,0.56+0.08*sin(fi+time*0.1));
            vec2 b=vec2(x,-0.56+0.08*cos(fi+time*0.1));
            beCell(col,p,a,vec2(0.16),fi/7.0,fi,time,energy*0.52);
            beCell(col,p,b,vec2(0.16),1.0-fi/7.0,fi,time,energy*0.52);
            beJunction(col,p,a,b,q,mix(BE_CYAN,BE_GREEN,fi/7.0),time,energy*0.46);
        }
        beVoltageRibbon(col,p,0.0,0.08,3.4,q,BE_GOLD,time,energy);
    }else if(mode==17){
        vec2 left=vec2(-0.88,0.0),right=vec2(0.86,0.0);
        bePotentialContours(col,p,left,right,q,time,energy);
        float picture=abs(sdRoundBox(p-left,vec2(0.50,0.38),0.06));
        col+=BE_PEARL*(aaStroke(picture,0.008)*0.40+glow(picture,0.035)*0.04)*q;
        for(int i=0;i<9;i++){
            float fi=float(i),y=mix(-0.38,0.38,fi/8.0);
            beVoltageRibbon(col,p-vec2(right.x,0.0),y,0.05,2.4+fi*0.2,q,bePotential(fi/8.0),time,energy*0.78);
        }
        beArrow(col,p,vec2(-0.20,0.0),vec2(0.24,0.0),BE_GOLD,q,energy);
    }else if(mode==18){
        beGene(col,p,vec2(-1.10,0.0),0.58,q,time,energy);
        vec2 waist=vec2(0.0);
        radiantNode(col,p,waist,0.10,BE_GOLD,q*energy);
        vec2 outcomes[4]=vec2[4](vec2(0.86,0.60),vec2(1.20,0.20),vec2(1.10,-0.28),vec2(0.72,-0.62));
        beArrow(col,p,vec2(-0.56,0.0),waist,BE_CYAN,q,energy);
        for(int i=0;i<4;i++){
            vec3 hue=bePotential(float(i)/3.0);
            beArrow(col,p,waist,outcomes[i],hue,q,energy*0.80);
            radiantNode(col,p,outcomes[i],0.052,hue,q*energy);
        }
    }else if(mode==19){
        beConcentricBody(col,p,q,time,energy);
        for(int i=0;i<5;i++){
            float fi=float(i),a=TAU*fi/5.0+time*0.04;
            vec2 c=vec2(cos(a),sin(a))*vec2(1.22,0.66);
            beCell(col,p,c,vec2(0.20),fi/4.0,fi,time,energy*0.60);
            beJunction(col,p,c,c*0.32,q,bePotential(fi/4.0),time,energy*0.70);
        }
    }else if(mode==20){
        beCell(col,p,vec2(-0.92,0.0),vec2(0.48),0.20,0.0,time,energy);
        beCell(col,p,vec2(0.92,0.0),vec2(0.48),0.82,2.0,time,energy);
        for(int i=0;i<5;i++){
            float fi=float(i),y=mix(-0.34,0.34,fi/4.0);
            beArrow(col,p,vec2(-0.44,y*0.5),vec2(0.44,y*0.5),mix(BE_CYAN,BE_GREEN,fi/4.0),q,energy);
        }
        float dose=mix(-0.72,0.72,q);
        radiantNode(col,p,vec2(dose,0.62),0.075,BE_GOLD,q*energy*(1.0+beat));
    }else if(mode==21){
        bePotentialContours(col,p,vec2(-0.85,0.0),vec2(0.85,0.0),q,time,energy);
        for(int i=0;i<17;i++){
            float fi=float(i),x=mix(-1.22,1.22,fi/16.0);
            float y=0.48*sin(x*2.0+0.45*sin(time*0.12))+0.10*sin(x*7.0+time*0.16);
            vec2 c=vec2(x,y);
            beCell(col,p,c,vec2(0.16,0.13),saturate(0.5+y),fi,time,energy*0.54*q);
            if(i<16){
                float nx=mix(-1.22,1.22,(fi+1.0)/16.0);
                float ny=0.48*sin(nx*2.0+0.45*sin(time*0.12))+0.10*sin(nx*7.0+time*0.16);
                beJunction(col,p,c,vec2(nx,ny),q,BE_GREEN,time,energy*0.44);
            }
        }
    }else if(mode==22){
        vec3 verdicts[4]=vec3[4](BE_GREEN,BE_PINK,BE_GOLD,BE_CYAN);
        for(int i=0;i<4;i++){
            float fi=float(i),y=mix(0.54,-0.54,fi/3.0);
            float card=abs(sdRoundBox(p-vec2(0.0,y),vec2(1.12,0.12),0.035));
            col+=verdicts[i]*(aaStroke(card,0.007)*0.45+glow(card,0.032)*0.045)*q*energy;
            float marker=sdCircle(p-vec2(0.88,y),0.045);
            col+=verdicts[i]*(aaFill(marker)*0.44+glow(marker,0.035)*0.10)*q;
        }
    }else if(mode==23){
        float left=abs(sdEllipse(p-vec2(-0.40,0.0),vec2(0.72,0.60)));
        float right=abs(sdEllipse(p-vec2(0.40,0.0),vec2(0.72,0.60)));
        col+=BE_CYAN*(aaStroke(left,0.010)*0.46+glow(left,0.055)*0.08)*q*energy;
        col+=BE_GOLD*(aaStroke(right,0.010)*0.46+glow(right,0.055)*0.08)*q*energy;
        bePotentialContours(col,p,vec2(-0.40,0.0),vec2(0.40,0.0),q,time,energy);
        beCell(col,p,vec2(0.0),vec2(0.24),0.56,0.0,time,energy);
    }else{
        beSheet(col,p,0.24,0.0,q,time,energy*0.58);
        beConcentricBody(col,p,q,time,energy);
        bePotentialContours(col,p,vec2(-0.92,0.0),vec2(0.92,0.0),q,time,energy);
        beEye(col,p,vec2(0.0,0.0),0.42,q,time,energy*0.82);
        for(int i=0;i<8;i++){
            float fi=float(i),a=TAU*fi/8.0;
            vec2 c=vec2(cos(a),sin(a))*vec2(1.15,0.66);
            beJunction(col,p,c,c*0.34,q,bePotential(fi/7.0),time,energy*0.55);
        }
    }
    col+=BE_CYAN*lensFlare(p,vec2(-0.72,0.48))*0.003*q*energy;
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
