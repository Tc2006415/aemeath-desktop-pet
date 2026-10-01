function hemAt(t,dragging=false,enabled=true){if(dragging||!enabled)return 'base';const p=t%1400;return p<400?'base':p<550?'light':p<1200?'upper':p<1350?'light':'base';}
function nextHemBoundary(t){const base=Math.floor(t/1400)*1400;return [400,550,1200,1350,1400].map(d=>base+d).find(v=>v>t+.001);}
if(typeof module!=='undefined')module.exports={hemAt,nextHemBoundary};
