#ifndef QUEUE_IMAGINAL_ANSWER_GLSL
#define QUEUE_IMAGINAL_ANSWER_GLSL

const vec3 IA_INK=vec3(0.018,0.022,0.045);
const vec3 IA_NIGHT=vec3(0.025,0.035,0.095);
const vec3 IA_IVORY=vec3(0.94,0.915,0.84);
const vec3 IA_SILVER=vec3(0.52,0.61,0.72);
const vec3 IA_GOLD=vec3(1.34,0.66,0.12);
const vec3 IA_CYAN=vec3(0.02,0.78,1.12);
const vec3 IA_VIOLET=vec3(0.55,0.12,1.10);
const vec3 IA_GREEN=vec3(0.06,0.80,0.42);
const vec3 IA_RED=vec3(1.02,0.05,0.16);
const vec3 IA_PEARL=vec3(0.92,0.96,1.08);

vec3 iaGround(vec2 p,vec2 uv,int mode,float q,float time){
    float depthMode=(mode==5||mode==6||mode==7||mode==8||mode==11||mode==12||mode==17)?1.0:0.0;
    float plaster=fbmWarp(p*1.55+vec2(time*0.006,-time*0.004),time+9.0);
    float grainField=fbm(p*8.0+vec2(time*0.008,0.0));
    vec3 paper=mix(vec3(0.74,0.67,0.56),IA_IVORY,0.52+0.34*plaster);
    paper+=vec3(0.16,0.10,0.035)*(grainField-0.5)*0.10;
    vec3 night=mix(IA_INK,IA_NIGHT,0.42+0.48*plaster);
    night+=mix(IA_VIOLET,IA_CYAN,plaster)*pow(max(plaster-0.57,0.0),3.0)*0.12;
    vec3 col=mix(paper,night,depthMode);
    if(mode==5) col=mix(paper,night,smoothstep(-0.22,0.22,p.x));
    if(mode==13) col=mix(paper,night,smoothstep(-0.06,0.06,p.x));
    if(mode==16) col=mix(paper,vec3(0.07,0.10,0.12),smoothstep(-0.55,0.55,p.y)*0.36);
    return col*(0.74+0.26*vignette(uv));
}
float iaDoorSDF(vec2 p,vec2 c,vec2 size,float open){
    vec2 lp=p-c;
    float outer=sdRoundBox(lp,size,0.045);
    float inner=sdRoundBox(lp,vec2(size.x*0.72,size.y*0.79),0.025);
    float frame=max(outer,-inner);
    float panel=sdRoundBox(lp-vec2(size.x*0.24*open,0.0),
                           vec2(size.x*0.67*(1.0-open*0.70),size.y*0.76),0.018);
    return min(frame,panel);
}
void iaDoor(inout vec3 col,vec2 p,vec2 c,vec2 size,float q,float open,float ae){
    vec2 lp=p-c;
    float outer=sdRoundBox(lp,size,0.045);
    float inner=sdRoundBox(lp,vec2(size.x*0.72,size.y*0.79),0.025);
    float frame=max(outer,-inner);
    float depth=aaFill(inner)*open;
    vec2 ray=lp/max(size,vec2(0.001));
    float tunnel=pow(0.5+0.5*cos(length(ray)*38.0-log(max(length(ray),0.04))*5.0),18.0);
    col=mix(col,mix(IA_NIGHT,IA_VIOLET*0.26,tunnel),depth*0.88);
    col+=IA_GOLD*(aaFill(frame)*0.42+aaStroke(frame,0.009)*0.78+glow(frame,0.045)*0.10)*q*ae;
    for(int i=0;i<5;i++){
        float fi=float(i),s=1.0-fi*0.13;
        float d=abs(sdRoundBox(lp,vec2(size.x*s,size.y*s),0.035));
        col+=mix(IA_SILVER,IA_GOLD,fi/4.0)*glow(d,0.018)*0.055*q*ae;
    }
}
float iaEye(vec2 p,vec2 c,float scale,float phase){
    vec2 q=(p-c)/scale;
    float lid=abs(sdVesica(q,0.72,0.35))-0.025;
    float iris=abs(length(q)-0.19-0.015*sin(atan(q.y,q.x)*8.0+phase));
    return min(lid,iris)*scale;
}
void iaGaze(inout vec3 col,vec2 p,vec2 c,float scale,vec3 hue,float energy,float time){
    float d=iaEye(p,c,scale,time*0.12);
    col+=hue*(aaStroke(d,0.007)*0.75+glow(d,0.050)*0.12)*energy;
    radiantNode(col,p,c,scale*0.13,IA_PEARL,energy*0.78);
}
void iaThread(inout vec3 col,vec2 p,vec2 a,vec2 b,vec3 hue,float energy,float time){
    vec2 mid=(a+b)*0.5+vec2(0.0,0.10*sin(time*0.17+dot(a,b)*7.0));
    lightFilament(col,p,a,mid,hue,energy);
    lightFilament(col,p,mid,b,hue,energy);
}
void iaContours(inout vec3 col,vec2 p,vec2 c,float q,vec3 hue,float energy,float time){
    vec2 lp=p-c;
    float angle=atan(lp.y,lp.x);
    for(int i=0;i<9;i++){
        float fi=float(i);
        float radius=0.09+fi*0.065+0.012*sin(angle*(5.0+fi)+time*0.11);
        float d=abs(length(lp/vec2(1.0,0.66))-radius);
        col+=hue*(aaStroke(d,0.005)*0.30+glow(d,0.030)*0.050)*q*energy*(0.80-fi*0.065);
    }
}
void iaCity(inout vec3 col,vec2 p,float q,float ae,float time){
    float horizon=-0.34;
    for(int i=0;i<21;i++){
        float fi=float(i),x=mix(-1.45,1.45,fi/20.0);
        float height=(0.10+0.48*hash11(fi*2.71))*q;
        float width=0.035+0.042*hash11(fi+8.0);
        float d=sdRoundBox(p-vec2(x,horizon+height*0.5),vec2(width,height*0.5),0.009);
        vec3 hue=mix(IA_VIOLET,IA_GOLD,hash11(fi*5.0));
        col+=hue*(aaFill(d)*0.12+glow(d,0.025)*0.065)*ae;
        float window=step(0.82,noise21(floor((p-vec2(x,horizon))*vec2(72.0,56.0))+fi));
        col+=IA_PEARL*aaFill(d)*window*0.22*q;
    }
    float floorLines=pow(0.5+0.5*cos((p.x/max(-p.y-horizon+0.09,0.08))*13.0),34.0);
    col+=IA_GOLD*floorLines*smoothstep(horizon-0.42,horizon,p.y)*0.055*q;
}
void iaRoots(inout vec3 col,vec2 p,float q,float ae,float time){
    for(int i=0;i<13;i++){
        float fi=float(i),x=mix(-0.82,0.82,fi/12.0);
        vec2 root=vec2(x,-0.68);
        vec2 crown=vec2(x*0.66,0.68);
        iaThread(col,p,vec2(0.0,-0.02),root,mix(IA_VIOLET,IA_CYAN,fi/12.0),q*ae,time+fi);
        iaThread(col,p,vec2(0.0,0.02),crown,mix(IA_GOLD,IA_GREEN,fi/12.0),q*ae,time-fi);
    }
}
void iaTriptych(inout vec3 col,vec2 p,float q,float ae,float time){
    for(int i=0;i<3;i++){
        float fi=float(i);
        vec2 c=vec2(mix(-0.72,0.72,fi/2.0),0.0);
        vec2 lp=p-c;
        float shell=abs(sdRoundBox(lp,vec2(0.28,0.52),0.05));
        vec3 hue=i==0?IA_VIOLET:(i==1?IA_RED:IA_GOLD);
        col+=hue*(aaStroke(shell,0.008)*0.58+glow(shell,0.050)*0.10)*q*ae;
        float crack=abs(lp.y+0.62*lp.x+0.08*sin(lp.x*21.0+time*0.2+fi));
        col+=IA_RED*glow(crack,0.022)*smoothstep(0.36,0.92,q)*ae*0.20;
        if(i==0) iaContours(col,p,c,q,hue,ae*0.45,time);
        if(i==1) {
            float core=abs(length(lp)-0.13);
            col+=IA_PEARL*(aaStroke(core,0.006)*0.55+glow(core,0.035)*0.08)*q;
        }
        if(i==2) radiantNode(col,p,c,0.10,IA_GOLD,q*ae*(0.8+0.3*sin(time)));
    }
}
void iaPredictionGrid(inout vec3 col,vec2 p,float energy){
    vec2 g=abs(fract((p+2.0)*vec2(9.0,7.0))-0.5);
    float grid=1.0-smoothstep(0.465,0.495,min(g.x,g.y));
    col+=IA_CYAN*grid*0.055*energy;
}
vec3 renderImaginalAnswer(vec2 p,vec2 uv,int mode,float progress,float time,float volume,float beat){
    float q=easeInOut(progress),ae=audioEnergy(volume,beat);
    vec3 col=iaGround(p,uv,mode,q,time);

    if(mode==0){
        iaGaze(col,p,vec2(-0.72,0.02),0.34,IA_CYAN,ae,time);
        iaDoor(col,p,vec2(0.46,0.0),vec2(0.43,0.70),q,0.0,ae);
        iaThread(col,p,vec2(-0.48,0.08),vec2(0.06,0.26),IA_CYAN,q*ae,time);
        iaThread(col,p,vec2(-0.48,0.00),vec2(0.06,0.00),IA_CYAN,q*ae,time+1.0);
        iaThread(col,p,vec2(-0.48,-0.08),vec2(0.06,-0.26),IA_CYAN,q*ae,time+2.0);
    }else if(mode==1){
        iaGaze(col,p,vec2(-0.74,0.02),0.34,IA_CYAN,ae,time);
        iaDoor(col,p,vec2(0.42,0.0),vec2(0.48,0.73),q,q,ae);
        iaThread(col,p,vec2(-0.47,-0.10),vec2(0.02,-0.10),IA_CYAN,q*ae,time);
        iaThread(col,p,vec2(0.02,0.16),vec2(-0.47,0.16),IA_GOLD,smoothstep(0.30,0.88,q)*ae,time);
        col+=mix(IA_VIOLET,IA_GOLD,fbmWarp(p*2.0,time))*aaFill(sdRoundBox(p-vec2(0.42),vec2(0.34,0.57),0.02))*q*0.12;
    }else if(mode==2){
        iaPredictionGrid(col,p,q);
        iaGaze(col,p,vec2(-0.88,0.0),0.30,IA_CYAN,ae,time);
        iaDoor(col,p,vec2(0.83,0.0),vec2(0.32,0.60),q,0.22,ae);
        float model=sdRoundBox(p,vec2(0.25,0.27),0.08);
        col+=IA_CYAN*(aaFill(model)*0.12+aaStroke(model,0.010)*0.55)*q;
        iaThread(col,p,vec2(-0.64,0.0),vec2(0.0,0.0),IA_CYAN,q*ae,time);
        iaThread(col,p,vec2(0.0,0.0),vec2(0.51,0.0),IA_CYAN,q*ae,time);
        iaThread(col,p,vec2(0.51,-0.22),vec2(0.0,-0.40),IA_GOLD,q*ae,time);
        iaThread(col,p,vec2(0.0,-0.40),vec2(-0.64,-0.16),IA_GOLD,q*ae,time);
    }else if(mode==3){
        iaPredictionGrid(col,p,0.65);
        float river=abs(p.y-0.16*sin(p.x*4.2+time*0.13)-0.05*sin(p.x*11.0-time*0.08));
        col+=IA_GOLD*(aaStroke(river,0.010)*0.84+glow(river,0.080)*0.14)*q*ae;
        float tear=smoothstep(0.0,0.38,q)*exp(-river*river/0.018);
        col=mix(col,mix(IA_NIGHT,IA_VIOLET,fbmWarp(p*2.6,time))*1.15,tear*0.38);
        iaDoor(col,p,vec2(0.82,0.08),vec2(0.27,0.48),q,q,ae);
    }else if(mode==4){
        iaRoots(col,p,q,ae,time);
        iaDoor(col,p,vec2(0.0,0.0),vec2(0.27,0.48),q,q*0.72,ae);
        iaContours(col,p,vec2(0.0),q,IA_GOLD,ae,time);
    }else if(mode==5){
        float membrane=abs(p.x+0.05*sin(p.y*7.0+time*0.12));
        col+=IA_GOLD*(aaStroke(membrane,0.012)*0.72+glow(membrane,0.070)*0.12)*q*ae;
        for(int i=0;i<9;i++){
            float fi=float(i),y=mix(-0.62,0.62,fi/8.0);
            iaThread(col,p,vec2(-0.92,y),vec2(0.92,-y*0.55),mix(IA_CYAN,IA_VIOLET,fi/8.0),q*ae*0.54,time+fi);
        }
        iaDoor(col,p,vec2(0.0),vec2(0.25,0.68),q,q,ae);
    }else if(mode==6){
        iaCity(col,p,q,ae,time);
        iaDoor(col,p,vec2(0.0,0.10),vec2(0.25,0.46),q,q,ae);
        float moon=length(p-vec2(-0.72,0.48))-0.12;
        col+=IA_PEARL*(aaFill(moon)*0.42+glow(moon,0.07)*0.11)*q;
    }else if(mode==7){
        float panel=sdRoundBox(p-vec2(0.22,0.0),vec2(0.62,0.74),0.08);
        col+=IA_GOLD*(aaFill(panel)*0.10+aaStroke(panel,0.012)*0.75+glow(panel,0.06)*0.10)*q;
        iaGaze(col,p,vec2(0.08,0.08),0.74,IA_GOLD,q*ae,time);
        iaGaze(col,p,vec2(-0.92,-0.10),0.25,IA_CYAN,ae,time);
        iaThread(col,p,vec2(-0.72,-0.05),vec2(-0.14,-0.05),IA_CYAN,q*ae,time);
        iaThread(col,p,vec2(-0.14,0.16),vec2(-0.72,0.16),IA_GOLD,smoothstep(0.30,0.90,q)*ae,time);
    }else if(mode==8){
        float axis=abs(p.x+0.045*sin(p.y*7.0+time*0.12));
        col+=IA_GOLD*(aaStroke(axis,0.010)*0.68+glow(axis,0.065)*0.13)*q*ae;
        radiantNode(col,p,vec2(0.0,0.62),0.09,IA_GOLD,q*ae);
        iaDoor(col,p,vec2(0.0,0.02),vec2(0.30,0.42),q,q,ae);
        iaGaze(col,p,vec2(0.0,-0.60),0.28,IA_CYAN,q*ae,time);
        for(int i=0;i<7;i++){
            float fi=float(i);vec2 c=vec2(mix(-0.65,0.65,fi/6.0),-0.30+0.08*sin(fi));
            iaThread(col,p,vec2(0.0,0.02),c,mix(IA_VIOLET,IA_GOLD,fi/6.0),q*ae*0.45,time+fi);
        }
    }else if(mode==9){
        vec2 lc=vec2(-0.67,0.0),rc=vec2(0.63,0.0);
        iaGaze(col,p,lc,0.32,IA_RED,q*ae,time);
        iaContours(col,p,lc,q,IA_RED,ae,time);
        iaDoor(col,p,rc,vec2(0.37,0.62),q,q,ae);
        iaThread(col,p,rc,vec2(0.06,-0.58),IA_GREEN,q*ae,time);
        radiantNode(col,p,vec2(0.06,-0.58),0.06,IA_GREEN,q*ae);
    }else if(mode==10){
        iaTriptych(col,p,q,ae,time);
    }else if(mode==11){
        for(int i=0;i<34;i++){
            float fi=float(i),a=TAU*hash11(fi*2.7)+time*0.018;
            float r=(0.12+0.76*hash11(fi+14.0))*q;
            vec2 c=vec2(cos(a),sin(a)*0.65)*r;
            radiantNode(col,p,c,0.017+0.010*beat,spectral(fi/34.0),q*ae);
            iaThread(col,p,vec2(0.0),c,mix(IA_GOLD,spectral(fi/34.0),0.7),q*ae*0.17,time+fi);
        }
        iaContours(col,p,vec2(0.0),q,IA_GOLD,ae,time);
        radiantNode(col,p,vec2(0.0),0.10,IA_PEARL,q*ae);
    }else if(mode==12){
        for(int i=0;i<24;i++){
            float fi=float(i),a=TAU*fi/24.0+time*0.025;
            float r=mix(0.04,0.92,q)*(0.55+0.45*hash11(fi));
            vec2 c=vec2(cos(a),sin(a)*0.64)*r;
            vec3 hue=mix(IA_GOLD,IA_CYAN,hash11(fi*3.0));
            iaThread(col,p,vec2(0.0),c,hue,q*ae*0.48,time+fi);
            radiantNode(col,p,c,0.026,hue,q*ae);
        }
        radiantNode(col,p,vec2(0.0),0.12,IA_GOLD,q*ae);
    }else if(mode==13){
        radiantNode(col,p,vec2(-0.68,0.0),0.30,IA_GOLD,q*ae);
        iaDoor(col,p,vec2(0.58,0.0),vec2(0.42,0.66),q,q,ae);
        iaContours(col,p,vec2(0.58,0.0),q,IA_VIOLET,ae,time);
        float divide=abs(p.x);
        col+=IA_RED*aaStroke(divide,0.008)*q*0.7;
    }else if(mode==14){
        vec2 a=vec2(0.0,0.62),b=vec2(-0.66,-0.48),c=vec2(0.66,-0.48);
        iaThread(col,p,a,b,IA_GOLD,q*ae,time);
        iaThread(col,p,b,c,IA_CYAN,q*ae,time);
        iaThread(col,p,c,a,IA_VIOLET,q*ae,time);
        iaDoor(col,p,vec2(0.0,-0.05),vec2(0.25,0.40),q,q,ae);
        for(int i=0;i<12;i++){
            float fi=float(i),ang=TAU*fi/12.0;
            vec2 n=vec2(cos(ang),sin(ang))*vec2(0.90,0.62);
            radiantNode(col,p,n,0.032,spectral(fi/12.0),q*ae);
            iaThread(col,p,n,vec2(0.0),spectral(fi/12.0),q*ae*0.36,time+fi);
        }
    }else if(mode==15){
        iaDoor(col,p,vec2(-0.62,0.0),vec2(0.34,0.62),q,q,ae);
        vec2 roots[4]=vec2[4](vec2(0.02,0.40),vec2(0.35,0.16),vec2(0.16,-0.34),vec2(0.72,-0.24));
        for(int i=0;i<4;i++){
            vec3 hue=i==0?IA_CYAN:(i==1?IA_GOLD:(i==2?IA_VIOLET:IA_GREEN));
            iaThread(col,p,vec2(-0.28,0.0),roots[i],hue,q*ae,time+float(i));
            radiantNode(col,p,roots[i],0.075,hue,q*ae);
        }
        float canopy=fbmWarp((p-vec2(0.35))*2.3,time);
        col+=IA_GREEN*pow(max(canopy-0.58,0.0),2.0)*q*0.32;
    }else if(mode==16){
        float horizon=-0.34;
        for(int i=0;i<11;i++){
            float fi=float(i),x=mix(-1.30,1.30,fi/10.0);
            float h=0.13+0.32*hash11(fi*3.4);
            float d=sdRoundBox(p-vec2(x,horizon+h*0.5),vec2(0.055,h*0.5),0.008);
            col+=IA_SILVER*(aaFill(d)*0.16+aaStroke(d,0.006)*0.28);
        }
        iaDoor(col,p,vec2(-0.82,-0.05),vec2(0.28,0.52),q,q,ae);
        vec2 prev=vec2(-0.58,-0.18);
        for(int i=1;i<72;i++){
            float s=float(i)/71.0;
            vec2 now=vec2(mix(-0.58,1.26,s),-0.24+0.12*sin(s*8.0+time*0.10)*s);
            lightFilament(col,p,prev,now,IA_GREEN,(1.0-smoothstep(q,q+0.025,s))*ae);
            prev=now;
        }
    }else{
        iaGaze(col,p,vec2(-0.86,0.0),0.30,IA_CYAN,ae,time);
        iaDoor(col,p,vec2(0.32,0.0),vec2(0.51,0.72),q,q,ae);
        iaCity(col,p-vec2(0.32,0.0),q,ae*0.72,time);
        iaThread(col,p,vec2(-0.63,-0.10),vec2(-0.08,-0.10),IA_CYAN,q*ae,time);
        iaThread(col,p,vec2(-0.08,0.16),vec2(-0.63,0.16),IA_GOLD,q*ae,time);
        iaContours(col,p,vec2(0.32,0.0),q,IA_GOLD,ae,time);
        float dawn=smoothstep(-0.70,0.70,p.x)*q;
        col+=IA_GREEN*dawn*fbmWarp(p*2.0,time)*0.08;
    }
    col+=IA_GOLD*lensFlare(p,vec2(0.56,0.44))*0.007*q*ae;
    return visionaryFinish(col,uv,gl_FragCoord.xy,time);
}

#endif
