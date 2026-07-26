#ifndef BEAUTIFY_PRESSURE_OPERA_GLSL
#define BEAUTIFY_PRESSURE_OPERA_GLSL

const vec3 GP_VOID=vec3(.006,.004,.018);
const vec3 GP_WINE=vec3(.34,.012,.10);
const vec3 GP_VIOLET=vec3(.34,.07,.62);
const vec3 GP_FIRE=vec3(1.25,.25,.045);
const vec3 GP_GOLD=vec3(1.28,.72,.22);
const vec3 GP_MOON=vec3(.56,.82,1.14);

vec3 gpBackground(vec2 p,float time){
    float smoke=fbmWarp(p*1.1+vec2(0,-time*.012),time*.18);
    float curtain=pow(max(0.,sin(p.y*2.8+smoke*3.7)),5.);
    vec3 c=GP_VOID+GP_WINE*.045*smoke+GP_VIOLET*.045*curtain;
    c+=vec3(.10,.025,.08)*pow(max(0.,1.-length(p)*.45),6.);
    return c;
}

vec3 gpVolume(vec2 p,float time,float kind,float drive){
    vec3 sum=vec3(0);float trans=1.;
    for(int i=0;i<28;i++){
        float z=-1.18+float(i)*.087;
        vec3 q=vec3(p,z);
        q.xy*=rot(.25*z*sin(time*.07+kind));
        q.xz*=rot(.18*sin(time*.09+q.y*1.7));
        float shell=smoothstep(.12,-.08,length(q*vec3(1.,1.12,.88))-(.72+.06*sin(time*.3)));
        float g=abs(gyroidField(q+vec3(0,0,time*.035),5.2+kind*.65));
        float filaments=exp(-g*g*110.);
        float cloud=fbm3(q*2.2+vec3(kind*2.7,time*.035,-time*.02));
        float rho=shell*saturate((cloud-.36)*1.5+filaments*.75);
        vec3 hue=mix(GP_VIOLET,GP_FIRE,saturate(cloud+kind*.08));
        hue+=GP_MOON*pow(filaments,4.)*.48;
        sum+=trans*hue*rho*.075*drive;
        trans*=exp(-rho*.105);
    }
    return sum;
}

float gpMaskSdf(vec2 p,float time,float morph){
    vec2 q=p;q.x*=1.08+.08*sin(time*.23);
    float crown=sdRegularPolygon(q-vec2(0,.08),.47,7.,PI*.5);
    float jaw=sdVesica(q+vec2(0,.18),.47,.23);
    float face=smoothUnion(crown,jaw,.18);
    float split=abs(q.x+.07*sin(q.y*8.+time*.31))-.018;
    return max(face,-mix(9.,split,morph));
}

void gpMask(inout vec3 c,vec2 p,float time,float drive,float morph,vec3 hue){
    float face=gpMaskSdf(p,time,morph);
    vec2 eyeP=p-vec2(.19,.07),eyeN=p+vec2(.19,-.07);
    float eye1=sdVesica(eyeP,.125,.078),eye2=sdVesica(eyeN,.125,.078);
    float eyes=min(eye1,eye2);
    float sigil=abs(sdStar(p+vec2(0,.22),.105,5.,.74,time*.06))-.008;
    float outline=aaStroke(face,.011),inside=aaFill(face);
    c+=hue*(outline+glow(face,.055)*.28)*drive;
    c+=mix(GP_WINE,GP_VIOLET,.5)*inside*.18;
    c*=1.-aaFill(eyes)*.72;
    c+=GP_MOON*(aaStroke(eyes,.007)+glow(eyes,.027)*.28);
    c+=GP_GOLD*(aaStroke(sigil,.006)+glow(sigil,.027)*.36)*drive;
}

float gpPressureBands(vec2 p,float time,float amount){
    float warp=fbmWarp(p*1.8,time*.2)-.5;
    float bands=phaseContour(p.y+warp*.22,10.+amount*6.,.048);
    float clampField=smoothstep(.86,.15,abs(p.y))*(.5+.5*sin(p.x*3.+time*.2));
    return bands*clampField;
}

float gpMandala(vec2 p,float time,float complexity){
    vec2 q=kaleido(p,6.+floor(complexity*4.),time*.035);
    float r=length(q),a=atan(q.y,q.x);
    float petals=abs(q.y-(.11+.25*q.x*q.x+.02*sin(18.*q.x-time)))-.009;
    float rings=abs(sin(r*(16.+complexity*8.)-time*.32))-.92;
    float spiral=logarithmicSpiral(q,2.+complexity*2.,3.8,time*.2);
    return min(petals,min(abs(rings)*.10,spiral*.025));
}

void gpPressureNodes(inout vec3 c,vec2 p,float time,float drive,float capture){
    for(int i=0;i<8;i++){
        float fi=float(i),a=fi*TAU/8.+time*.04;
        float rr=mix(.72,.28,capture)+.04*sin(time*.6+fi);
        vec2 n=rr*vec2(cos(a),sin(a));
        radiantNode(c,p,n,.12,mix(GP_MOON,GP_FIRE,capture),.32*drive);
        lightFilament(c,p,n,vec2(0),mix(GP_VIOLET,GP_GOLD,capture),.42*drive);
    }
}

float gpAshLandscape(vec2 p,float time){
    float horizon=-.26+.08*fbm(vec2(p.x*1.3,time*.02));
    float dune1=horizon+.13*sin(p.x*2.1)+.06*fbm(vec2(p.x*3.,2.));
    float dune2=horizon-.16+.09*sin(p.x*3.7+1.4);
    return min(abs(p.y-dune1),abs(p.y-dune2));
}

float gpTunnel(vec2 p,float time,float reversal){
    vec2 q=logPolar(p+vec2(.0001));
    float radial=phaseContour(q.x-time*mix(.18,-.18,reversal),7.,.055);
    float ribs=phaseContour(q.y/TAU+.07*sin(q.x*7.-time),12.,.035);
    return max(radial,ribs);
}

float gpTimeSlices(vec2 p,float time,float dissolve){
    float bands=floor((p.x+1.5)*10.);
    vec2 q=p;
    q.y+=.15*sin(bands*.71+time*.35);
    q.x+=.10*sin(bands*1.93-time*.22);
    float figure=sdEllipse(q,vec2(.48,.72));
    float erase=fbmWarp(q*2.+bands,time*.35);
    return aaStroke(figure,.012)*(1.-smoothstep(.58,.78,erase)*dissolve);
}

float gpCymatic(vec2 p,float time,float order){
    float r=length(p),a=atan(p.y,p.x);
    float wave=sin(r*(26.+order*4.)-time*2.)+sin(a*(5.+order)+time*.7);
    wave+=sin((p.x+p.y)*18.-time*1.3)*.35;
    return exp(-abs(wave)*6.)*smoothstep(1.25,.12,r);
}

void gpBodyTemple(inout vec3 c,vec2 p,float time,float drive,float coherence){
    float axis=abs(p.x)-.007;
    float silhouette=sdRoundBox(p,vec2(.28,.72),.22);
    c+=GP_VIOLET*aaStroke(silhouette,.009)*.7;
    c+=GP_MOON*glow(axis,.025)*.25*coherence;
    for(int i=0;i<7;i++){
        float fi=float(i),y=-.58+fi*.19;
        float drift=.025*sin(time*.45+fi*1.8)*(1.-coherence);
        vec2 n=vec2(drift,y);
        radiantNode(c,p,n,.085,mix(GP_FIRE,GP_GOLD,coherence),.42*drive);
        if(i>0)lightFilament(c,p,n,vec2(0,y-.19),GP_MOON,.55*coherence*drive);
    }
}

vec3 renderPressureOpera(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    float drive=audioEnergy(volume,beat),enter=easeOut(min(1.,u*1.55));
    float reveal=smoothstep(.16,.86,u),breath=.5+.5*sin(time*.66);
    vec3 c=gpBackground(p,time);

    if(mode==0){
        c+=gpVolume(p,time,0.,drive);
        float bands=gpPressureBands(p,time,1.);
        c+=GP_FIRE*bands*.16+GP_GOLD*softBeam(p,vec2(0,1.),vec2(0,-1),.38,.52)*.13;
        c+=GP_MOON*softBeam(p,vec2(0,-1.),vec2(0,1),.38,.52)*.10;
    }else if(mode==1){
        c+=gpVolume(p,time,1.,drive)*.72;
        for(int i=0;i<9;i++){
            float fi=float(i),a=fi*TAU/9.;
            vec2 a0=.17*vec2(cos(a),sin(a)),b0=(.72+.05*sin(time+fi))*vec2(cos(a+.12*sin(fi)),sin(a+.12*sin(fi)));
            lightFilament(c,p,a0,b0,mix(GP_FIRE,GP_MOON,fi/8.),drive);
        }
    }else if(mode==2){
        vec2 source=vec2(-.62,.08),screen=vec2(.72,0);
        radiantNode(c,p,source,.21,GP_FIRE,.62*drive);
        c+=GP_GOLD*softBeam(p,source,vec2(1,-.06),.21,.35)*.34;
        float wall=abs(p.x-screen.x)-.006;
        c+=GP_MOON*aaStroke(wall,.006);
        gpMask(c,p-screen, time,drive*.72,reveal,GP_VIOLET);
    }else if(mode==3){
        c+=gpVolume(p,time,2.,drive)*.52;
        gpMask(c,p,time,drive,reveal,GP_GOLD);
        c+=GP_VIOLET*gpPressureBands(p,time,2.)*.12*(1.-reveal);
    }else if(mode==4){
        float capture=smoothstep(.18,.78,u);
        gpPressureNodes(c,p,time,drive,capture);
        gpMask(c,p/mix(1.35,.66,capture),time,drive,1.,GP_FIRE);
        c*=mix(1.,.64,capture*smoothstep(.95,.15,length(p)));
    }else if(mode==5){
        vec2 q=kaleido(p,5.,time*.09);
        float eruption=gpMandala(q,time,.36);
        float thermal=glow(eruption,.036)*.34+aaStroke(eruption,.006)*.52;
        c+=pressurePalette(1.-smoothstep(0.,.09,eruption))*thermal*drive;
        c+=GP_FIRE*causticField(p*.75,time)*.17;
    }else if(mode==6){
        vec2 q=kaleido(projectiveWarp(p,.45,time*.04),8.,0.);
        float threat=gpMandala(q,time,.82);
        c+=GP_VIOLET*glow(threat,.038)*.24+GP_MOON*aaStroke(threat,.005)*.48;
        for(int i=0;i<5;i++){float fi=float(i);float ring=abs(length(p)-(.18+fi*.15+.018*sin(time+fi)))-.005;c+=GP_FIRE*glow(ring,.022)*.12;}
    }else if(mode==7){
        float absent=length(p-vec2(.55,.08));
        for(int i=0;i<11;i++){
            float fi=float(i),y=-.75+fi*.15;
            vec2 a=vec2(-1.25,y),b=vec2(.55,.08),mid=mix(a,b,.5)+vec2(0,.22*sin(fi*1.7+time*.2));
            float d=min(sdSegment(p,a,mid),sdSegment(p,mid,b));
            c+=mix(GP_VIOLET,GP_FIRE,fi/10.)*(aaStroke(d,.004)+glow(d,.025)*.11);
        }
        c*=1.-.82*exp(-absent*absent/.055);
        c+=GP_GOLD*glow(absent-.22,.035)*.28;
    }else if(mode==8){
        float ash=gpAshLandscape(p,time);
        c+=vec3(.18,.12,.22)*smoothstep(.55,-.25,p.y)*(.35+.65*fbm(p*3.));
        c+=GP_MOON*glow(ash,.025)*.12;
        for(int i=0;i<18;i++){
            vec2 star=hash22(vec2(float(i),7.))*vec2(2.8,1.0)-vec2(1.4,.1);
            float fade=.15+.85*hash11(float(i)*2.3);
            radiantNode(c,p,star,.035,mix(vec3(.18),GP_GOLD,fade),.10*fade);
        }
        c+=vec3(.3,.17,.18)*fbmWarp(p*2.+vec2(0,-time*.02),time)*.14;
    }else if(mode==9){
        float tunnel=gpTunnel(p,time,0.);
        vec2 q=projectiveWarp(p,.72,time*.03);
        c+=GP_FIRE*tunnel*.28+GP_GOLD*pow(tunnel,3.)*.55;
        c+=GP_MOON*softBeam(q,vec2(0),vec2(cos(time*.2),sin(time*.2)),.5,.6)*.13;
        c*=.52+.48*smoothstep(.04,.5,length(p));
    }else if(mode==10){
        float tunnel=gpTunnel(p,time,reveal);
        c+=mix(GP_FIRE,GP_MOON,reveal)*(tunnel*.28+pow(tunnel,4.)*.44);
        radiantNode(c,p,vec2(0),mix(.08,.34,reveal),mix(GP_GOLD,GP_MOON,reveal),drive);
        c+=gpVolume(p*.8,time,3.,drive)*.32*reveal;
    }else if(mode==11){
        float slices=gpTimeSlices(p,time,reveal);
        c+=GP_MOON*slices*.5;
        float dissolve=fbmWarp(p*2.+vec2(time*.04,0),time);
        c+=mix(GP_FIRE,GP_GOLD,dissolve)*phaseContour(dissolve-time*.05,12.,.025)*reveal*.09;
        c+=GP_VIOLET*softBeam(p,vec2(1.2,.5),vec2(-1,-.2),.22,.4)*.16;
    }else if(mode==12){
        float sound=gpCymatic(p,time,2.+floor(beat*2.));
        c+=GP_GOLD*sound*(.42+.9*drive)+GP_MOON*pow(sound,3.)*.55;
        c+=gpVolume(p,time,4.,drive)*.24*(1.-sound);
        float ring=abs(length(p)-(.2+.55*fract(time*.24)))-.007;
        c+=GP_FIRE*glow(ring,.035)*.34;
    }else if(mode==13){
        c+=gpVolume(p*.82,time,5.,drive)*.26;
        gpBodyTemple(c,p,time,drive,reveal);
        float aura=abs(sdVesica(p,.9,.46))-.008;
        c+=GP_GOLD*glow(aura,.05)*.28;
    }else if(mode==14){
        for(int i=0;i<8;i++){
            float fi=float(i),r=.18+fi*.095+reveal*fi*.045;
            vec2 q=p*rot(reveal*(fi-3.5)*.17);
            float shell=abs(sdRegularPolygon(q,r,4.+mod(fi,5.),fi*.2))- .006;
            c+=mix(GP_FIRE,GP_MOON,reveal)*(aaStroke(shell,.006)+glow(shell,.025)*.16)*(1.-fi*.08);
        }
        radiantNode(c,p,vec2(0),.25,GP_GOLD,.72*drive);
    }else if(mode==15){
        vec2 q=projectiveWarp(p,.7*(1.-reveal),time*.05);
        gpMask(c,q,time,drive,1.-reveal,GP_FIRE);
        c+=gpVolume(p,time,6.,drive)*.38*reveal;
        float inner=gpMandala(p,time,.42);
        c+=GP_GOLD*(aaStroke(inner,.005)*.54+glow(inner,.025)*.14)*reveal;
    }else if(mode==16){
        c+=gpVolume(p,time,7.,drive)*.48;
        gpPressureNodes(c,p,time,drive*.72,0.);
        float boundary=abs(length(p)-(.62+.035*sin(time*.4)))-.007;
        c+=GP_GOLD*aaStroke(boundary,.007)+GP_MOON*glow(boundary,.04)*.22;
    }else if(mode==17){
        c+=gpVolume(p,time,8.,drive)*.30;
        for(int i=0;i<9;i++){
            float fi=float(i),a=fi*TAU/9.+time*.025;
            vec2 n=.67*vec2(cos(a),sin(a));
            float emblem=abs(sdRegularPolygon(p-n,.10+mod(fi,3.)*.025,3.+mod(fi,6.),a))-.006;
            c+=interferencePalette(fi/9.,.08)*(aaStroke(emblem,.006)+glow(emblem,.03)*.21)*drive;
            lightFilament(c,p,n,vec2(0),GP_GOLD,.28*drive);
        }
        radiantNode(c,p,vec2(0),.22,GP_MOON,.58*drive);
    }else if(mode==18){
        for(int i=0;i<4;i++){
            float fi=float(i),a=fi*TAU/4.+PI*.25;
            vec2 n=.58*vec2(cos(a),sin(a)),q=p-n;
            float lens=abs(length(q)-.24)-.007;
            c+=mix(GP_MOON,GP_GOLD,fi/3.)*(aaStroke(lens,.006)+glow(lens,.025)*.16);
            float mark=abs(sdRegularPolygon(q,.10,3.+fi,fi*.3))-.005;
            c+=GP_VIOLET*aaStroke(mark,.005);
        }
        float crosshair=abs(length(p)-.16)-.006;
        c+=GP_FIRE*glow(crosshair,.03)*.24;
    }else{
        float pressure=gpPressureBands(p,time,2.)*(1.-reveal);
        c+=GP_FIRE*pressure*.18+gpVolume(p,time,9.,drive)*(.34+.30*reveal);
        for(int i=0;i<5;i++){
            float fi=float(i),a=fi*TAU/5.+time*.035;
            vec2 n=mix(.28,.66,reveal)*vec2(cos(a),sin(a));
            float mask=abs(sdRegularPolygon(p-n,.13,5.+mod(fi,3.),a))-.006;
            c+=mix(GP_FIRE,GP_MOON,reveal)*(aaStroke(mask,.006)+glow(mask,.03)*.18);
            lightFilament(c,p,n,vec2(0),GP_GOLD,.30*drive);
        }
        radiantNode(c,p,vec2(0),mix(.12,.28,reveal),GP_GOLD,.68*drive);
    }
    c*=enter;
    return cinemaFinish(c,uv,gl_FragCoord.xy,time,.24+.14*drive);
}

#endif
