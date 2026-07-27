#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("word_timings")
    parser.add_argument("output")
    parser.add_argument("--fps",type=float,default=20.0)
    args=parser.parse_args()
    data=json.loads(Path(args.word_timings).read_text(encoding="utf-8"))
    words=data["words"]
    duration=max((float(w["end"]) for w in words),default=0.0)
    frames=[]
    count=int(duration*args.fps)+1
    for index in range(count):
        time=index/args.fps
        active=[w for w in words if float(w["start"])<=time<float(w["end"])]
        nearby=[w for w in words if time-1.5<=float(w["start"])<=time+1.5]
        speech_active=1 if active else 0
        density=min(1.0,len(nearby)/10.0)
        emphasis=max([float(w.get("emphasis",0.0)) for w in active],default=0.0)
        semantic_event=next((w.get("semanticEvent") for w in active if w.get("semanticEvent")),None)
        frames.append({
            "time":round(time,6),
            "speechActive":speech_active,
            "speechDensity":round(density,6),
            "emphasis":round(emphasis,6),
            "semanticEvent":semantic_event,
            "attentionRequest":round(min(1.0,density*0.75+emphasis*0.4),6)
        })
    output={"version":"1.0","duration":duration,"frames":frames}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,separators=(",",":")),encoding="utf-8")

if __name__=="__main__":
    main()
