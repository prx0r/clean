#ifndef QUEUE_ATTENTIONAL_APERTURE_GLSL
#define QUEUE_ATTENTIONAL_APERTURE_GLSL

const vec3 AF_VOID=vec3(0.002,0.004,0.012);
const vec3 AF_BLUE=vec3(0.015,0.32,0.86);
const vec3 AF_CYAN=vec3(0.01,0.94,1.22);
const vec3 AF_GOLD=vec3(1.38,0.66,0.08);
const vec3 AF_RED=vec3(1.14,0.025,0.105);
const vec3 AF_MAGENTA=vec3(1.02,0.04,0.68);
const vec3 AF_VIOLET=vec3(0.47,0.08,1.16);
const vec3 AF_GREEN=vec3(0.13,1.04,0.42);
const vec3 AF_PEARL=vec3(0.88,0.96,1.16);

vec3 afGround(vec2 p,vec2 uv,int mode,float time){
    float warp=fbmWarp(p*1.35+vec2(time*0.010,-time*0.006),time+22.0);
    float ridge=ridgedFbm(p*3.4+vec2(-time*0.008,time*0.005));
    vec3 col=mix(AF_VOID,vec3(0.025,0.018,0.080),0.20+0.48*warp);
    col+=mix(AF_BLUE,AF_VIOLET,warp)*pow(max(ridge-0.58,0.0),3.0)*0.11;
    float caustic=pow(0.5+0.5*cos((warp-ridge)*38.0),24.0);
    col+=spectral(warp*0.33)*caustic*0.018;
    if(mode==8||mode==10||mode==12||mode==14)col+=AF_RED*pow(max(warp-0.66,0.0),2.0)*0.055;
    return col*(0.69+0.31*vignette(uv));
}
void afNode(inout vec3 col,vec2 p,vec2 c,float r,vec3 hue,float energy){
    radiantNode(col,p,c,r,hue,energy);
    float ring=abs(length(p-c)-r*1.9);
    col+=hue*(aaStroke(ring,0.004)*0.22+glow(ring,0.025)*0.035)*energy;
}
void afField(inout vec3 col,vec2 p,float visibility,float time,float ae){
    for(int i=0;i<72;i++){
        float fi=float(i);
        vec2 c=hash22(vec2(fi*2.17,17.0))*vec2(2.65,1.42)-vec2(1.325,0.71);
        c+=0.025*vec2(sin(time*0.11+fi),cos(time*0.09+fi*1.7));
        vec3 hue=spectral(hash11(fi*4.3));
        afNode(col,p,c,0.010+0.013*hash11(fi+4.0),hue,visibility*ae*(0.42+0.48*hash11(fi)));
    }
}
void afRings(inout vec3 col,vec2 p,vec2 c,float extent,float q,vec3 hue,float ae,float time){
    vec2 lp=p-c;
    float angle=atan(lp.y,lp.x);
    for(int i=0;i<11;i++){
        float fi=float(i),r=extent*(0.12+fi*0.080);
        float d=abs(length(lp/vec2(1.0,0.62))-r-0.009*sin(angle*(6.0+fi)+time*0.12));
        col+=hue*(aaStroke(d,0.005)*0.28+glow(d,0.034)*0.052)*q*ae*(0.86-fi*0.065);
    }
}
void afBeam(inout vec3 col,vec2 p,vec2 origin,vec2 target,float width,float q,vec3 hue,float ae){
    vec2 axis=target-origin;
    float lengthAxis=length(axis);
    vec2 direction=axis/lengthAxis;
    vec2 rel=p-origin;
    float along=dot(rel,direction)/lengthAxis;
    float side=abs(dot(rel,vec2(-direction.y,direction.x)));
    float coneWidth=mix(width*0.08,width,saturate(along));
    float inside=(1.0-smoothstep(coneWidth,coneWidth+0.015,side))*smoothstep(-0.02,0.04,along)*(1.0-smoothstep(0.98,1.04,along));
    col+=hue*inside*(0.085+0.075*q)*ae;
    lightFilament(col,p,origin,target,hue,q*ae);
}
float afBody(vec2 p,vec2 c,float s){
    vec2 q=(p-c)/s;
    float head=sdCircle(q-vec2(0.0,0.34),0.13);
    float torso=sdRoundBox(q-vec2(0.0,-0.08),vec2(0.19,0.34),0.10);
    float shoulders=sdEllipse(q-vec2(0.0,0.08),vec2(0.36,0.18));
    return min(head,min(torso,shoulders))*s;
}
void afBodyPaint(inout vec3 col,vec2 p,vec2 c,float s,vec3 hue,float energy){
    float d=afBody(p,c,s);
    col+=hue*(aaStroke(d,0.008)*0.52+glow(d,0.055)*0.085+aaFill(d)*0.035)*energy;
}
void afTunnel(inout vec3 col,vec2 p,float q,float ae,float time,vec3 hue){
    vec2 lp=p*rot(time*0.012);
    for(int i=0;i<13;i++){
        float fi=float(i),z=fi/12.0;
        vec2 size=vec2(1.22,0.68)*(1.0-z*0.77);
        float d=abs(sdRoundBox(lp-vec2(0.0,0.025*sin(fi+time*0.15)),size,0.045));
        col+=mix(hue,AF_RED,z)*(aaStroke(d,0.006)*0.34+glow(d,0.032)*0.045)*q*ae*(0.92-z*0.48);
    }
}
void afWeb(inout vec3 col,vec2 p,vec2 c,float radius,float q,float ae,float time){
    for(int i=0;i<18;i++){
        float fi=float(i),a=TAU*fi/18.0+time*0.015;
        vec2 n=c+vec2(cos(a),sin(a)*0.62)*radius*(0.65+0.35*hash11(fi));
        vec3 hue=spectral(fi/18.0);
        lightFilament(col,p,c,n,hue,q*ae*0.40);
        afNode(col,p,n,0.022,hue,q*ae);
    }
    afNode(col,p,c,0.062,AF_GOLD,q*ae);
}
void afFracture(inout vec3 col,vec2 p,vec2 c,float q,float ae,float time){
    for(int i=0;i<22;i++){
        float fi=float(i),a=TAU*fi/22.0+0.18*sin(fi*4.0);
        float r=mix(0.08,0.96,q)*(0.72+0.28*hash11(fi));
        vec2 n=c+vec2(cos(a),sin(a)*0.62)*r;
        vec3 hue=i%3==0?AF_RED:(i%3==1?AF_CYAN:AF_MAGENTA);
        lightFilament(col,p,c,n,hue,q*ae);
        afNode(col,p,n,0.022,hue,q*ae*(0.7+0.3*sin(time+fi)));
    }
}
void afVesica(inout vec3 col,vec2 p,float q,float ae,float time){
    float left=abs(sdEllipse(p-vec2(-0.32,0.0),vec2(0.58,0.48)));
    float right=abs(sdEllipse(p-vec2(0.32,0.0),vec2(0.58,0.48)));
    col+=AF_GOLD*(aaStroke(left,0.008)*0.50+glow(left,0.045)*0.08)*q*ae;
    col+=AF_VIOLET*(aaStroke(right,0.008)*0.50+glow(right,0.045)*0.08)*q*ae;
    float middle=abs(sdVesica(p*vec2(1.0,1.2),0.60,0.31));
    col+=AF_CYAN*(aaStroke(middle,0.008)*0.55+glow(middle,0.050)*0.10)*q*ae;
}
vec3 renderAttentionalAperture(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat){
    float q=easeInOut(progress),ae=audioEnergy(volume,beat);
    vec3 col=afGround(p,uv,mode,time);

    if(mode==0){
        afField(col,p,0.90,time,ae);
        afRings(col,p,vec2(0.0),0.98,q,AF_GOLD,ae,time);
    }else if(mode==1){
        vec2 focus=vec2(0.38,-0.08);
        afField(col,p,0.65*(1.0-q)+0.18,time,ae);
        float privilege=exp(-dot(p-focus,p-focus)/(0.055+0.24*(1.0-q)));
        col=mix(col,AF_VOID,(1.0-privilege)*q*0.72);
        afRings(col,p,focus,0.68,q,AF_GOLD,ae,time);
        afNode(col,p,focus,0.075,AF_GOLD,q*ae);
    }else if(mode==2){
        vec2 origin=vec2(-1.05,0.0),target=vec2(0.92,0.0);
        afField(col,p,0.48*(1.0-q),time,ae);
        afBeam(col,p,origin,target,mix(0.64,0.11,q),q,AF_CYAN,ae);
        afNode(col,p,target,0.075,AF_GOLD,q*ae);
    }else if(mode==3){
        vec2 focus=vec2(0.32,0.04);
        afField(col,p,0.72,time,ae);
        float aperture=length((p-focus)/vec2(1.0,0.72))-mix(0.92,0.34,q);
        col=mix(col,AF_VOID,smoothstep(-0.02,0.035,aperture)*q*0.88);
        col+=AF_GOLD*(aaStroke(aperture,0.009)*0.62+glow(aperture,0.045)*0.08)*q*ae;
        afNode(col,p,focus,0.055,AF_GOLD,q*ae);
    }else if(mode==4){
        vec2 here=vec2(-0.12,-0.02);
        afRings(col,p,here,mix(0.98,0.42,q),q,AF_CYAN,ae,time);
        afNode(col,p,here,0.075,AF_GOLD,q*ae);
        vec2 farPoints[3]=vec2[3](vec2(-0.98,0.50),vec2(1.03,0.46),vec2(0.84,-0.52));
        for(int i=0;i<3;i++)afNode(col,p,farPoints[i],0.035,AF_VIOLET,(1.0-q*0.48)*ae);
    }else if(mode==5){
        vec2 self=vec2(-0.80,0.0);
        afBodyPaint(col,p,self,0.62,AF_PEARL,ae);
        vec2 nodes[4]=vec2[4](vec2(0.02,0.42),vec2(0.80,0.28),vec2(0.12,-0.46),vec2(0.91,-0.39));
        for(int i=0;i<4;i++){
            vec3 hue=i==0?AF_GREEN:(i==1?AF_RED:(i==2?AF_CYAN:AF_GOLD));
            afBeam(col,p,self,nodes[i],0.09,q,hue,ae);
            afNode(col,p,nodes[i],0.052,hue,q*ae);
        }
    }else if(mode==6){
        afField(col,p,0.52,time,ae);
        float border=length(p/vec2(1.0,0.62))-mix(0.20,0.72,q);
        col=mix(col,AF_VOID,smoothstep(-0.02,0.04,border)*0.56*q);
        col+=AF_GOLD*(aaStroke(border,0.010)*0.66+glow(border,0.050)*0.09)*q*ae;
        afNode(col,p,vec2(0.0),0.075,AF_GOLD,q*ae);
        for(int i=0;i<8;i++){
            float fi=float(i),a=TAU*fi/8.0;vec2 n=vec2(cos(a),sin(a)*0.62)*0.52;
            if(i%2==0)lightFilament(col,p,n,vec2(0.0),AF_GOLD,q*ae*0.72);
        }
    }else if(mode==7){
        afTunnel(col,p,q,ae,time,AF_CYAN);
        afBodyPaint(col,p,vec2(0.0,-0.12),0.70,AF_PEARL,q*ae);
        afNode(col,p,vec2(0.0,0.10),0.07,AF_GOLD,q*ae);
    }else if(mode==8){
        vec2 self=vec2(-0.82,-0.04);
        afBodyPaint(col,p,self,0.58,AF_PEARL,ae);
        vec2 threats[3]=vec2[3](vec2(0.05,0.45),vec2(0.94,0.03),vec2(0.18,-0.52));
        for(int i=0;i<3;i++){
            afBeam(col,p,self,threats[i],0.18,q,AF_RED,ae);
            afNode(col,p,threats[i],0.075,AF_RED,q*ae);
        }
        float alarm=pow(0.5+0.5*cos(atan(p.y,p.x)*11.0-time*0.7),24.0);
        col+=AF_RED*alarm*exp(-length(p)*1.4)*q*0.08;
    }else if(mode==9){
        vec2 lack=vec2(0.10,0.02);
        afNode(col,p,lack,0.055,AF_RED,q*ae);
        vec2 desires[4]=vec2[4](vec2(-1.05,0.48),vec2(1.05,0.48),vec2(-0.96,-0.52),vec2(0.98,-0.48));
        for(int i=0;i<4;i++){
            vec3 hue=spectral(float(i)*0.23);
            vec2 bend=desires[i]*0.48+vec2(0.0,0.16*sin(float(i)+time*0.14));
            lightFilament(col,p,lack,bend,hue,q*ae);
            lightFilament(col,p,bend,desires[i],hue,q*ae);
            afNode(col,p,desires[i],0.055,hue,q*ae);
        }
        afRings(col,p,lack,0.62,q,AF_RED,ae,time);
    }else if(mode==10){
        vec2 lp=kaleido(p,9.0,time*0.026);
        float vortex=abs(log(max(length(lp),0.025))*0.48+atan(lp.y,lp.x)*2.2-time*0.20);
        vortex=abs(fract(vortex)-0.5);
        col+=mix(AF_RED,AF_MAGENTA,fbm(p*3.0))*(1.0-smoothstep(0.035,0.16,vortex))*q*0.33*ae;
        afRings(col,p,vec2(0.0),0.72,q,AF_RED,ae,time);
        afNode(col,p,vec2(0.0),0.10,AF_RED,q*ae*(1.0+beat));
    }else if(mode==11){
        for(int y=0;y<4;y++)for(int x=0;x<7;x++){
            vec2 c=vec2(mix(-1.10,1.10,float(x)/6.0),mix(-0.52,0.52,float(y)/3.0));
            float d=abs(sdRoundBox(p-c,vec2(0.12,0.10),0.025));
            vec3 hue=spectral((float(x)+float(y)*2.0)/12.0);
            col+=hue*(aaStroke(d,0.005)*0.28+glow(d,0.025)*0.035)*ae;
        }
        float scan=mix(-1.20,1.20,fract(q+time*0.03));
        col+=AF_GOLD*exp(-pow((p.x-scan)/0.07,2.0))*0.22*ae;
        afBeam(col,p,vec2(scan,-0.68),vec2(scan,0.68),0.09,q,AF_GOLD,ae);
    }else if(mode==12){
        afBodyPaint(col,p,vec2(0.0),0.70,AF_PEARL,ae);
        afFracture(col,p,vec2(0.0),q,ae,time);
    }else if(mode==13){
        vec3 hues[5]=vec3[5](AF_CYAN,AF_MAGENTA,AF_GOLD,AF_RED,AF_GREEN);
        for(int i=0;i<5;i++){
            float fi=float(i),y=mix(0.52,-0.52,fi/4.0);
            vec2 a=vec2(-1.15,y),b=vec2(1.15,y+0.12*sin(fi*2.0+time*0.16));
            lightFilament(col,p,a,b,hues[i],q*ae);
            afNode(col,p,mix(a,b,fract(q+fi*0.17)),0.036,hues[i],q*ae);
        }
        float slice=mix(-0.95,0.95,fract(q*1.7));
        col+=AF_PEARL*exp(-pow((p.x-slice)/0.025,2.0))*0.18;
    }else if(mode==14){
        afBodyPaint(col,p,vec2(-0.36,-0.02),0.84,AF_PEARL,ae*0.72);
        vec2 pain=vec2(-0.10,-0.22);
        float radius=mix(0.84,0.10,q);
        float aperture=abs(length(p-pain)-radius);
        col=mix(col,AF_VOID,smoothstep(radius*0.25,radius*0.95,length(p-pain))*q*0.80);
        col+=AF_RED*(aaStroke(aperture,0.012)*0.72+glow(aperture,0.075)*0.13)*q*ae;
        afNode(col,p,pain,0.085,AF_RED,q*ae*(1.0+beat));
    }else if(mode==15){
        afField(col,p,0.52*q,time,ae);
        afWeb(col,p,vec2(0.0),mix(0.10,0.86,q),q,ae,time);
        float wash=fbmWarp(p*1.8,time);
        col+=spectral(wash+time*0.01)*pow(max(wash-0.48,0.0),2.2)*q*0.20;
    }else if(mode==16){
        afBodyPaint(col,p,vec2(0.0,-0.08),0.68,AF_PEARL,q*ae);
        afBeam(col,p,vec2(0.0,-0.58),vec2(0.0,0.60),0.08,q,AF_CYAN,ae);
        afField(col,p,0.62*q,time,ae);
        afRings(col,p,vec2(0.0),0.88,q,AF_GOLD,ae,time);
    }else if(mode==17){
        afField(col,p,0.88,time,ae);
        afRings(col,p,vec2(0.0),1.02,q,AF_GOLD,ae,time);
        afNode(col,p,vec2(0.0),0.060,AF_GOLD,q*ae);
    }else if(mode==18){
        afField(col,p,0.78,time,ae);
        vec2 origin=vec2(-1.02,0.0),target=vec2(0.52,0.0);
        afBeam(col,p,origin,target,0.42,q,AF_CYAN,ae);
        afNode(col,p,target,0.070,AF_GOLD,q*ae);
        afRings(col,p,target,0.58,q,AF_GOLD,ae,time);
    }else if(mode==19){
        afVesica(col,p,q,ae,time);
        afNode(col,p,vec2(-0.32,0.0),0.07,AF_GOLD,q*ae);
        afNode(col,p,vec2(0.32,0.0),0.07,AF_VIOLET,q*ae);
        afBeam(col,p,vec2(-0.32,0.0),vec2(0.32,0.0),0.12,q,AF_CYAN,ae);
    }else if(mode==20){
        afWeb(col,p,vec2(0.0),0.66,q,ae,time);
        float cross=abs(p.x*p.y);
        col+=AF_PEARL*exp(-cross*85.0)*exp(-length(p)*0.8)*q*0.07;
        afTunnel(col,p,q*0.36,ae,time,AF_GOLD);
    }else if(mode==21){
        for(int i=0;i<3;i++){
            float fi=float(i),a=TAU*fi/3.0+time*0.15;
            vec2 c=vec2(cos(a),sin(a)*0.62)*0.58;
            vec3 hue=i==0?AF_MAGENTA:(i==1?AF_CYAN:AF_GOLD);
            afNode(col,p,c,0.07,hue,q*ae);
            lightFilament(col,p,c,vec2(0.0),hue,q*ae);
        }
        afRings(col,p,vec2(0.0),0.88,q,AF_GOLD,ae,time*1.7);
        afNode(col,p,vec2(0.0),0.10,AF_PEARL,q*ae*(1.0+beat));
    }else if(mode==22){
        vec2 centers[4]=vec2[4](vec2(-0.78,0.40),vec2(0.76,0.43),vec2(-0.68,-0.45),vec2(0.72,-0.42));
        for(int i=0;i<4;i++){
            vec3 hue=spectral(float(i)*0.22);
            afNode(col,p,centers[i],0.070,hue,q*ae);
            for(int j=i+1;j<4;j++)lightFilament(col,p,centers[i],centers[j],mix(hue,spectral(float(j)*0.22),0.5),q*ae*0.52);
        }
        float care=abs(length(p/vec2(1.0,0.68))-0.98);
        col+=AF_GREEN*(aaStroke(care,0.009)*0.52+glow(care,0.05)*0.08)*q*ae;
    }else if(mode==23){
        vec2 lc=vec2(-0.62,0.0),rc=vec2(0.62,0.0);
        afWeb(col,p,lc,0.42,q,ae,time);
        afRings(col,p,rc,0.58,q,AF_GOLD,ae,time);
        afBeam(col,p,lc,rc,0.13,q,AF_VIOLET,ae);
        float divide=abs(p.x);
        col+=AF_PEARL*aaStroke(divide,0.006)*0.28*q;
    }else if(mode==24){
        vec3 hues[4]=vec3[4](AF_GREEN,AF_RED,AF_CYAN,AF_RED);
        for(int i=0;i<4;i++){
            float fi=float(i),y=mix(0.50,-0.50,fi/3.0);
            float card=abs(sdRoundBox(p-vec2(0.0,y),vec2(0.90,0.105),0.025));
            col+=hues[i]*(aaStroke(card,0.006)*0.46+glow(card,0.028)*0.04)*q*ae;
            float verdict=sdCircle(p-vec2(0.72,y),0.035);
            col+=hues[i]*(aaFill(verdict)*0.45+glow(verdict,0.025)*0.08)*q;
        }
    }else{
        afField(col,p,0.90,time,ae);
        afRings(col,p,vec2(0.0),1.02,q,AF_GOLD,ae,time);
        afBeam(col,p,vec2(-1.12,0.0),vec2(0.48,0.0),0.30,q,AF_CYAN,ae);
        afNode(col,p,vec2(0.48,0.0),0.072,AF_GOLD,q*ae);
        afWeb(col,p,vec2(0.48,0.0),0.50,q*0.62,ae,time);
    }
    col+=AF_GOLD*lensFlare(p,vec2(0.52,0.42))*0.005*q*ae;
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
