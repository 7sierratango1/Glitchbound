from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text()

# Add Mythic as the top loot tier. Existing rarity indexes remain unchanged.
old="const RARITIES=[['COMMON','#d6d6d6',1],['UNCOMMON','#63c76a',1.25],['RARE','#5f9cff',1.6],['EPIC','#bd6cff',2.15],['LEGENDARY','#ffb43b',3]];"
new="const RARITIES=[['COMMON','#d6d6d6',1],['UNCOMMON','#63c76a',1.25],['RARE','#5f9cff',1.6],['EPIC','#bd6cff',2.15],['LEGENDARY','#ffb43b',3],['MYTHIC','#ff4fd8',4.6]];"
if old not in s: raise SystemExit('missing rarity table')
s=s.replace(old,new,1)

# Extend rarity roll so Mythic is genuinely rare, with bosses/world bosses and later worlds improving odds.
old="function rarityFor(e){let q=Math.random(),boost=(e.kind==='worldboss'?.28:e.kind==='boss'?.18:e.kind==='tank'?.06:0)+Math.min(.18,Math.max(0,(e.size||1)-1))*.25+Math.min(.12,save.world*.012);q-=boost;if(q<.025)return 4;if(q<.09)return 3;if(q<.24)return 2;if(q<.52)return 1;return 0}"
new="function rarityFor(e){let q=Math.random(),boost=(e.kind==='worldboss'?.28:e.kind==='boss'?.18:e.kind==='tank'?.06:0)+Math.min(.18,Math.max(0,(e.size||1)-1))*.25+Math.min(.12,save.world*.012);q-=boost;if(q<.008)return 5;if(q<.035)return 4;if(q<.10)return 3;if(q<.25)return 2;if(q<.53)return 1;return 0}"
if old not in s: raise SystemExit('missing rarity roller')
s=s.replace(old,new,1)

# Selling is based on both item power (item level) and rarity. Higher tiers rise sharply in value.
marker="function statText(it){"
if marker not in s: raise SystemExit('missing statText marker')
helper="""const SELL_RARITY_MULT=[1,1.45,2.25,3.6,6.5,11];\nfunction sellValue(it){let r=Math.max(0,Math.min(SELL_RARITY_MULT.length-1,it.rarity||0)),level=Math.max(1,it.power||1);return Math.max(1,Math.round((4+Math.pow(level,0.82)*1.65)*SELL_RARITY_MULT[r]))}\nfunction sellItem(id){let inv=save.loot.inventory,idx=inv.findIndex(x=>x.id===id);if(idx<0)return;let it=inv[idx],value=sellValue(it);inv.splice(idx,1);save.coins+=value;persist();renderGear()}\n"""
s=s.replace(marker,helper+marker,1)

# Every inventory card gets a SELL button with the exact coin payout shown before tapping it.
old="d.innerHTML=`<strong style=\"color:${it.color}\">${it.name}</strong><div>Power ${it.power}</div><div style=\"font-size:10px;margin:5px 0\">${statText(it)}</div><button>EQUIP</button>`;d.querySelector('button').onclick=()=>equipItem(it.id);el.appendChild(d)"
new="d.innerHTML=`<strong style=\"color:${it.color}\">${it.name}</strong><div>Power ${it.power}</div><div style=\"font-size:10px;margin:5px 0\">${statText(it)}</div><div style=\"display:flex;gap:6px;justify-content:center;flex-wrap:wrap\"><button class=\"equipBtn\">EQUIP</button><button class=\"sellBtn\">SELL • ${sellValue(it)} COIN</button></div>`;d.querySelector('.equipBtn').onclick=()=>equipItem(it.id);d.querySelector('.sellBtn').onclick=()=>sellItem(it.id);el.appendChild(d)"
if old not in s: raise SystemExit('missing inventory card renderer')
s=s.replace(old,new,1)

p.write_text(s)
