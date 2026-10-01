const pickupFrames=['neutral','surprise','pickup','hold-entry'],pickupEnds=[80,160,260,360];
function pickupAt(elapsed){return {index:Math.min(3,pickupEnds.findIndex(e=>elapsed<e)<0?3:pickupEnds.findIndex(e=>elapsed<e)),done:elapsed>=360};}
if(typeof module!=='undefined')module.exports={pickupAt,pickupEnds,pickupFrames};
