#ifndef BEAUTIFY_PERCEPTUAL_CRYSTAL_GLSL
#define BEAUTIFY_PERCEPTUAL_CRYSTAL_GLSL

const vec3 RP_BLACK=vec3(.008,.008,.016);
const vec3 RP_BLUE=vec3(.07,.28,1.12);
const vec3 RP_CYAN=vec3(.02,.95,1.04);
const vec3 RP_RED=vec3(1.18,.06,.18);
const vec3 RP_GOLD=vec3(1.34,.54,.07);
const vec3 RP_WHITE=vec3(.92,.94,1.02);

vec3 rpBackground(vec2 p,float time){
    float n=fbmWarp(p*.8+vec2(0,time*.01),time*.1);
    vec3 c=RP_BLACK+vec3(.018,.018,.05)*n;
    c+=vec3(.025,.012,.04)*waveInterference(p*.55,time*.15);
    return c;
}

float rpRigidGrid(vec2 p,float time,float bend){
    vec2 q=projectiveWarp(p,bend,.12+time*.02);
    q+=.06*bend*vec2(sin(q.y*5.+time*.1),sin(q.x*4.-time*.08));
    vec2 d=abs(fract(q*4.)-.5);
    return 1.-smoothstep(.025,.045,min(d.x,d.y));
}

float rpMoire(vec2 p,float time,float alignment){
    vec2 a=vec2(.28+.12*alignment,.08*sin(time*.08));
    float w1=sin(length(p-a)*(35.+alignment*12.)-time*.6);
    float w2=sin(length(p+a)*(34.-alignment*8.)+time*.52);
    return .5+.5*w1*w2;
}

float rpGlyph(vec2 p,float time,float open){
    vec2 q=p*rot(.12*sin(time*.08));
    float ring=abs(length(q)-(.31+.025*sin(4.*atan(q.y,q.x)+time*.22)))-.008;
    float v1=abs(sdVesica(q*rot(PI*.25),.36,.19))-.007;
    float v2=abs(sdVesica(q*rot(-PI*.25),.36,.19))-.007;
    float core=abs(sdRegularPolygon(q,.105,4.,PI*.25+time*.015))-.006;
    float aperture=1.-smoothstep(.16,.72,open);
    return min(core,min(ring,min(v1,v2)+aperture*.035));
}

void rpDrawGlyph(inout vec3 c,vec2 p,float time,float reveal,float drive){
    float d=rpGlyph(p,time,reveal);
    float interference=rpMoire(p,time,reveal);
    c+=mix(RP_BLUE,RP_GOLD,reveal)*(aaStroke(d,.006)+glow(d,.035)*(.12+.22*reveal))*drive;
    c+=RP_CYAN*interference*(1.-smoothstep(.18,.38,length(p)))*.08*reveal;
    radiantNode(c,p,vec2(0),.11,mix(RP_RED,RP_WHITE,reveal),.22*drive*reveal);
}

float rpGestaltMask(vec2 p,float morph){
    vec2 q=p;q.x*=1.1;
    float shell=sdRegularPolygon(q,.59,7.,.18);
    float knot=rpGlyph(q*.78,0.,1.);
    return mix(shell,knot,morph);
}

void rpParticles(inout vec3 c,vec2 p,float time,float reveal,float drive,float maskMode){
    for(int y=-6;y<=6;y++)for(int x=-10;x<=10;x++){
        vec2 id=vec2(float(x),float(y)),j=hash22(id+23.)-.5;
        vec2 n=(id+j*.9)*vec2(.14,.14);
        n+=.035*vec2(sin(time*.3+hash21(id)*TAU),cos(time*.27+hash21(id+2.)*TAU));
        float mask=rpGestaltMask(n,reveal);
        float inside=1.-smoothstep(-.04,.08,mask);
        float select=mix(.20+.80*hash21(id),inside,maskMode);
        float d=length(p-n),size=.006+.012*select;
        vec3 hue=interferencePalette(hash21(id)+reveal*.16,.08);
        c+=hue*exp(-d*d/(size*size))*select*(.18+.26*drive);
    }
}

float rpRibbon(vec2 p,float time,float ambiguity){
    float d=9.;vec2 prev=vec2(-1.25,-.22);
    for(int i=1;i<58;i++){
        float fi=float(i)/57.,x=-1.25+fi*2.5;
        float y=.26*sin(fi*TAU*(1.4+ambiguity)+time*.12)+.12*sin(fi*17.-time*.18)*ambiguity;
        vec2 next=vec2(x,y);
        d=min(d,sdSegment(p,prev,next));prev=next;
    }
    return d;
}

void rpFeatureFace(inout vec3 c,vec2 p,float time,float drive,float coherence){
    vec2 q=p;
    float boundary=abs(sdEllipse(q,vec2(.44,.58)))-.007;
    float eye1=sdVesica(q-vec2(-.17,.12),.12,.075);
    float eye2=sdVesica(q-vec2(.17,.12),.12,.075);
    float bridge=sdSegment(q,vec2(0,.08),vec2(-.04,-.12));
    float lower=abs(sdRegularPolygon(q+vec2(0,.22),.15,3.,PI*.5))-.006;
    vec2 scatter=(1.-coherence)*.15*vec2(sin(time*.4),cos(time*.31));
    c+=RP_BLUE*aaStroke(boundary,.007)*coherence;
    c+=RP_CYAN*(aaStroke(eye1+scatter.x,.006)+aaStroke(eye2-scatter.x,.006));
    c+=RP_GOLD*(aaStroke(bridge+scatter.y,.005)+aaStroke(lower,.006));
    c+=RP_RED*glow(min(eye1,eye2),.028)*.16*drive;
}

void rpFeaturePanels(inout vec3 c,vec2 p,float time,float drive,float meaning){
    for(int i=0;i<6;i++){
        float fi=float(i),a=fi*TAU/6.+time*.02;
        vec2 n=.57*vec2(cos(a),sin(a));
        float panel=abs(sdRoundBox(p-n,vec2(.16,.12),.035))-.005;
        float mark=abs(sdRegularPolygon(p-n,.065,3.+mod(fi,4.),a))-.004;
        c+=mix(RP_BLUE,RP_GOLD,meaning)*(aaStroke(panel,.005)+aaStroke(mark,.004))*drive;
        if(meaning>0.)lightFilament(c,p,n,vec2(0),RP_CYAN,.22*meaning*drive);
    }
}

void rpPrediction(inout vec3 c,vec2 p,float time,float drive,float correction){
    float predicted=rpRibbon(p+vec2(.10,-.10),time,0.);
    float sensed=rpRibbon(p,time,.35*correction);
    c+=RP_BLUE*(aaStroke(predicted,.005)+phaseContour(p.x-time*.1,9.,.04)*glow(predicted,.025)*.12);
    c+=mix(RP_RED,RP_CYAN,correction)*(aaStroke(sensed,.006)+glow(sensed,.028)*.18)*drive;
    for(int i=0;i<7;i++){
        float fi=float(i)/6.,x=-.95+fi*1.9;
        vec2 a=vec2(x,.26*sin((x+1.25)/2.5*TAU*1.4+time*.12));
        vec2 b=a+vec2(.10,-.10)*(1.-correction);
        lightFilament(c,p,a,b,RP_GOLD,.18*drive);
    }
}

void rpCategories(inout vec3 c,vec2 p,float time,float drive,float rigidity){
    for(int cluster=0;cluster<4;cluster++){
        float cl=float(cluster),a=cl*TAU/4.+PI*.25;
        vec2 center=.55*vec2(cos(a),sin(a));
        vec3 hue=interferencePalette(cl/4.,.07);
        for(int i=0;i<9;i++){
            float fi=float(i),ang=fi*2.399+time*.018*(1.-rigidity);
            vec2 n=center+(.05+.025*fi)*vec2(cos(ang),sin(ang));
            radiantNode(c,p,n,.045,hue,.11*drive);
        }
        float boundary=abs(length(p-center)-(.22-.06*rigidity))- .005;
        c+=hue*(aaStroke(boundary,.005)+glow(boundary,.022)*.09)*rigidity;
    }
}

void rpRasa(inout vec3 c,vec2 p,float time,float drive,float openness){
    for(int i=0;i<7;i++){
        float fi=float(i),a=fi*TAU/7.+time*.025,r=.22+.055*fi;
        float wave=abs(length(p)-r-.035*sin(atan(p.y,p.x)*(3.+fi)+time*.35+fi))- .005;
        vec3 hue=interferencePalette(fi/7.,.10);
        c+=hue*(aaStroke(wave,.005)+glow(wave,.026)*.12)*drive;
    }
    float bowl=abs(sdArcBand(p+vec2(0,.08),.67,-2.75,-.39))-.006;
    c+=RP_WHITE*aaStroke(bowl,.006)*openness+RP_GOLD*glow(bowl,.04)*.18;
}

void rpInvariant(inout vec3 c,vec2 p,float time,float drive,float recognition){
    for(int i=0;i<5;i++){
        float fi=float(i),x=-.92+fi*.46;
        vec2 q=(p-vec2(x,0))*rot(fi*.47+time*.015);
        float d=rpGlyph(q/(.32+.025*fi),time+fi,recognition)*(.32+.025*fi);
        c+=mix(RP_BLUE,RP_GOLD,recognition)*(aaStroke(d,.005)+glow(d,.022)*.10)*drive;
        if(i<4)lightFilament(c,p,vec2(x+.12,0),vec2(x+.34,0),RP_CYAN,.18*recognition);
    }
}

vec3 renderPerceptualCrystal(vec2 p,vec2 uv,int mode,float u,float time,float volume,float beat){
    float drive=audioEnergy(volume,beat),enter=easeOut(min(1.,u*1.55));
    float reveal=smoothstep(.16,.84,u),align=smoothstep(.28,.78,u);
    vec3 c=rpBackground(p,time);

    if(mode==0){
        float n=noise21(gl_FragCoord.xy*.72+floor(time*8.));
        c+=interferencePalette(n,.04)*(.05+.25*n)*drive;
        c+=RP_WHITE*phaseContour(n+time*.02,14.,.018)*.06;
    }else if(mode==1){
        rpParticles(c,p,time,reveal,drive,align);
        float boundary=rpGestaltMask(p,reveal);
        c+=RP_CYAN*aaStroke(boundary,.006)*reveal;
    }else if(mode==2){
        rpParticles(c,p,time,.42,drive,.4);
        float here=abs(length(p-vec2(.18,-.07))-(.12+.04*beat))- .006;
        c+=RP_GOLD*(aaStroke(here,.006)+glow(here,.04)*.26)*drive;
        c+=RP_BLUE*rpMoire(p,time,.3)*.05;
    }else if(mode==3){
        rpParticles(c,p,time,.58,drive,.72);
        float familiar=rpGlyph(p,time,reveal);
        c+=mix(RP_BLUE,RP_GOLD,reveal)*(glow(familiar,.05)*.24+aaStroke(familiar,.006)*reveal);
    }else if(mode==4){
        rpParticles(c,p,time,reveal,drive,align);
        float object=abs(sdRegularPolygon(projectiveWarp(p,.32*(1.-reveal),time*.02),.54,7.,time*.015))- .007;
        c+=RP_WHITE*aaStroke(object,.007)*reveal+RP_GOLD*glow(object,.04)*.18;
    }else if(mode==5){
        float fluid=rpRibbon(p,time,.72*(1.-reveal));
        c+=RP_CYAN*(aaStroke(fluid,.005)+glow(fluid,.028)*.16)*(1.-reveal);
        for(int i=0;i<7;i++){
            float fi=float(i),x=-.9+fi*.30;
            float mark=abs(sdRegularPolygon(p-vec2(x,0),.075,3.+mod(fi,4.),fi*.2))- .005;
            c+=RP_GOLD*(aaStroke(mark,.005)+glow(mark,.02)*.10)*reveal;
        }
    }else if(mode==6){
        rpCategories(c,p,time,drive,reveal);
        c+=RP_WHITE*rpMoire(p,time,reveal)*.04*reveal;
    }else if(mode==7){
        rpDrawGlyph(c,p,time,reveal,drive);
        float loop=abs(length(p)-(.68-.22*reveal))- .006;
        c+=RP_RED*(aaStroke(loop,.006)+glow(loop,.035)*.14);
        lightFilament(c,p,.68*vec2(cos(time*.2),sin(time*.2)),vec2(0),RP_WHITE,.26*drive);
    }else if(mode==8){
        rpDrawGlyph(c,p,time,reveal,drive);
        float mirror=rpGlyph(p*vec2(-1,1),-time,reveal);
        c+=RP_CYAN*glow(mirror,.04)*.13;
        float feedback=abs(length(p)-(.46+.04*sin(time*.5)))-.005;
        c+=RP_RED*aaStroke(feedback,.005)*.55;
    }else if(mode==9){
        float outline=abs(sdRegularPolygon(p,.58,9.,time*.02))- .007;
        c+=RP_WHITE*(aaStroke(outline,.007)+glow(outline,.035)*.13);
        c+=interferencePalette(fbmWarp(p*1.6,time),.03)*phaseContour(fbmWarp(p*1.8,time),12.,.025)*aaFill(outline)*.12;
        rpDrawGlyph(c,p*.62,time,reveal*.35,drive*.45);
    }else if(mode==10){
        float ribbonA=rpRibbon(p,time,mix(.1,.8,reveal));
        float ribbonB=rpRibbon(p*vec2(1,-1),time+2.,mix(.8,.1,reveal));
        c+=RP_CYAN*(aaStroke(ribbonA,.006)+glow(ribbonA,.03)*.16);
        c+=RP_RED*(aaStroke(ribbonB,.006)+glow(ribbonB,.03)*.16);
        float switching=abs(length(p)-(.18+.25*reveal))- .006;
        c+=RP_GOLD*aaStroke(switching,.006);
    }else if(mode==11){
        rpFeatureFace(c,p,time,drive,reveal);
        rpParticles(c,p,time,.2,drive*.3,1.-reveal);
    }else if(mode==12){
        rpFeaturePanels(c,p,time,drive,reveal*.15);
        float whole=abs(sdRegularPolygon(p,.68,6.,PI/6.))- .006;
        c+=RP_RED*glow(whole,.04)*.12*(1.-reveal);
    }else if(mode==13){
        for(int i=0;i<24;i++){
            float fi=float(i),a=fi*2.399;
            vec2 scattered=.74*sqrt(fi/23.)*vec2(cos(a),sin(a));
            vec2 reconstructed=.52*vec2(cos(fi*TAU/24.),sin(fi*TAU/24.))+.08*vec2(sin(fi*3.1),cos(fi*2.2));
            vec2 n=mix(scattered,reconstructed,reveal);
            radiantNode(c,p,n,.055,mix(RP_BLUE,RP_GOLD,reveal),.14*drive);
        }
        float contour=abs(sdRegularPolygon(p,.52,11.,0.))- .006;
        c+=RP_WHITE*aaStroke(contour,.006)*reveal;
    }else if(mode==14){
        rpPrediction(c,p,time,drive,reveal);
    }else if(mode==15){
        rpParticles(c,p,time,.46,drive,.3);
        vec2 target=vec2(.32*sin(time*.13),.24*cos(time*.17));
        radiantNode(c,p,target,mix(.08,.31,reveal),RP_GOLD,.62*drive);
        for(int i=0;i<9;i++){
            float fi=float(i),a=fi*TAU/9.;
            lightFilament(c,p,target+.52*vec2(cos(a),sin(a)),target,RP_CYAN,.14*reveal*drive);
        }
    }else if(mode==16){
        c+=RP_BLUE*rpRigidGrid(p,time,.32)*.13;
        for(int y=-2;y<=2;y++)for(int x=-4;x<=4;x++){
            vec2 n=vec2(float(x)*.28,float(y)*.28);
            float rune=abs(sdRegularPolygon(p-n,.075,3.+mod(float(x+y+8),5.),float(x)*.3))- .005;
            c+=RP_RED*(aaStroke(rune,.005)+glow(rune,.02)*.08);
        }
        rpDrawGlyph(c,p*.72,time,reveal*.35,drive*.35);
    }else if(mode==17){
        rpRasa(c,p,time,drive,reveal);
        c+=RP_CYAN*causticField(p*.52,time)*.13;
    }else if(mode==18){
        rpFeatureFace(c,p*.72,time,drive,1.);
        float shell=abs(length(p)-mix(.52,1.18,reveal))- .008;
        c+=RP_RED*(aaStroke(shell,.008)+glow(shell,.05)*.22)*drive;
        c*=1.-RP_RED.x*reveal*.12*smoothstep(.2,.9,length(p));
    }else if(mode==19){
        vec2 q=projectiveWarp(p,.72*(1.-reveal),time*.03);
        rpDrawGlyph(c,q,time,reveal,drive);
        rpParticles(c,p,time,reveal,drive*.72,reveal);
        float field=abs(length(p)-(.83+.04*sin(time*.2)))- .006;
        c+=RP_WHITE*glow(field,.04)*.16*reveal;
    }else if(mode==20){
        rpInvariant(c,p,time,drive,reveal);
        float retrieval=abs(p.y-.58)-.006;
        c+=RP_RED*aaStroke(retrieval,.006)*(1.-reveal);
    }else if(mode==21){
        vec2 left=p+vec2(.68,0),right=p-vec2(.68,0);
        rpFeaturePanels(c,left,time,drive*.55,reveal);
        rpDrawGlyph(c,right,time,reveal,drive*.58);
        float seam=abs(p.x)-.006;c+=RP_GOLD*(aaStroke(seam,.006)+glow(seam,.032)*.16);
    }else if(mode==22){
        for(int i=0;i<4;i++){
            float fi=float(i);vec2 n=vec2((mod(fi,2.)-.5)*1.10,(floor(fi/2.)-.5)*.86);
            float lens=abs(length(p-n)-.22)-.006;
            c+=interferencePalette(fi/4.,.08)*(aaStroke(lens,.006)+glow(lens,.025)*.11);
            float mark=abs(sdRegularPolygon(p-n,.08,3.+fi,fi*.4))-.004;
            c+=RP_WHITE*aaStroke(mark,.004);
        }
    }else{
        rpParticles(c,p,time,reveal,drive,reveal);
        vec2 q=projectiveWarp(p,.34*(1.-reveal),time*.025);
        rpDrawGlyph(c,q,time,reveal,drive);
        float wave=rpMoire(q,time,reveal);
        c+=interferencePalette(wave+reveal*.2,.04)*phaseContour(wave,9.,.025)*.08*reveal;
        float outer=abs(length(q)-(.68+.05*beat))- .006;
        c+=RP_WHITE*(aaStroke(outer,.006)+glow(outer,.035)*.14)*reveal;
    }
    c*=enter;
    return cinemaFinish(c,uv,gl_FragCoord.xy,time,.16+.14*drive);
}

#endif
