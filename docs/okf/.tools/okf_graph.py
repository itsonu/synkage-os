#!/usr/bin/env python3
"""Build the OKF knowledge graph from frontmatter + markdown links.

Emits graph.json (nodes + edges). With --html, also writes a single
self-contained HTML file (vanilla-JS canvas force layout, no CDN, no data
leaves the file) — a minimal offline visualizer.

Usage:
  python okf_graph.py --bundle docs/okf --out docs/okf/graph.json --html
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okf_common as ok


def build_graph(bundle):
    nodes, edges, seen = [], [], set()
    concept_rels = set()
    for ap_, rel, fm, body in ok.iter_concepts(bundle):
        concept_rels.add(rel)
        nodes.append({
            "id": rel,
            "title": fm.get("title") or os.path.basename(rel),
            "type": fm.get("type") or ("nav" if os.path.basename(rel) in ok.RESERVED else "Unknown"),
            "tags": fm.get("tags", []) or [],
        })
    node_ids = {n["id"] for n in nodes}
    for ap_, rel, fm, body in ok.iter_concepts(bundle):
        for t in ok.extract_links(body, bundle, ap_):
            key = (rel, t)
            if t in node_ids and key not in seen:
                seen.add(key)
                edges.append({"source": rel, "target": t})
    return {"nodes": nodes, "edges": edges}


HTML_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>OKF Graph</title>
<style>
  html,body{margin:0;height:100%;background:#0f1020;color:#e8e6f0;font:14px system-ui,sans-serif}
  #c{display:block;width:100%;height:100%}
  #info{position:fixed;top:10px;left:10px;max-width:320px;background:#1b1c34;
        border:1px solid #34365e;border-radius:8px;padding:10px 12px;opacity:.96}
  #info h3{margin:0 0 4px;font-size:14px}
  #info .t{color:#a9a6d6;font-size:12px}
  #info a{color:#f0a; text-decoration:none}
</style></head><body>
<div id="info"><h3>OKF Graph</h3><div class="t">__COUNT__ concepts · hover a node</div></div>
<canvas id="c"></canvas>
<script>
const DATA = __DATA__;
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
let W,H;function fit(){W=cv.width=innerWidth;H=cv.height=innerHeight;}fit();addEventListener('resize',fit);
const types=[...new Set(DATA.nodes.map(n=>n.type))];
const pal=['#f0a','#5cf','#7f9','#fd6','#c9f','#f96','#6fd','#f66','#9cf','#ff9'];
const color=t=>pal[types.indexOf(t)%pal.length];
const N=DATA.nodes.map((n,i)=>({...n,x:W/2+Math.cos(i)*200+Math.random()*40,y:H/2+Math.sin(i)*200+Math.random()*40,vx:0,vy:0}));
const idx=Object.fromEntries(N.map((n,i)=>[n.id,i]));
const E=DATA.edges.filter(e=>e.source in idx&&e.target in idx).map(e=>({s:idx[e.source],t:idx[e.target]}));
let hover=null;
cv.addEventListener('mousemove',ev=>{hover=null;for(const n of N){const dx=n.x-ev.clientX,dy=n.y-ev.clientY;if(dx*dx+dy*dy<100){hover=n;break;}}
  if(hover){document.getElementById('info').innerHTML='<h3>'+hover.title+'</h3><div class="t">'+hover.type+(hover.tags.length?' · '+hover.tags.join(', '):'')+'</div><div class="t">'+hover.id+'</div>';}});
function step(){
  for(const a of N){a.vx*=0.85;a.vy*=0.85;}
  for(let i=0;i<N.length;i++)for(let j=i+1;j<N.length;j++){
    const a=N[i],b=N[j];let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy||0.01,d=Math.sqrt(d2);
    const f=1400/d2;a.vx+=dx/d*f;a.vy+=dy/d*f;b.vx-=dx/d*f;b.vy-=dy/d*f;}
  for(const e of E){const a=N[e.s],b=N[e.t];let dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)||0.01;
    const f=(d-90)*0.01;a.vx+=dx/d*f;a.vy+=dy/d*f;b.vx-=dx/d*f;b.vy-=dy/d*f;}
  for(const a of N){a.vx+=(W/2-a.x)*0.0008;a.vy+=(H/2-a.y)*0.0008;a.x+=a.vx;a.y+=a.vy;}
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle='rgba(140,140,200,0.25)';ctx.lineWidth=1;
  for(const e of E){const a=N[e.s],b=N[e.t];ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
  for(const n of N){ctx.beginPath();ctx.fillStyle=color(n.type);ctx.arc(n.x,n.y,n===hover?9:6,0,7);ctx.fill();
    if(n===hover){ctx.fillStyle='#fff';ctx.fillText(n.title,n.x+10,n.y+4);}}
  requestAnimationFrame(step);
}step();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default="docs/okf")
    ap.add_argument("--out", default=None, help="graph.json output path")
    ap.add_argument("--html", action="store_true")
    args = ap.parse_args()

    bundle = os.path.abspath(args.bundle)
    if not os.path.isdir(bundle):
        print(f"ERROR: bundle not found: {bundle}")
        return 2

    graph = build_graph(bundle)
    out = args.out or os.path.join(bundle, "graph.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Wrote {out}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

    if args.html:
        html_path = os.path.splitext(out)[0] + ".html"
        html = HTML_TEMPLATE.replace("__DATA__", json.dumps(graph)).replace(
            "__COUNT__", str(len(graph["nodes"])))
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote {html_path} (open in any browser, fully offline)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
