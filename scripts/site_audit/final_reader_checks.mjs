// Final-reader independent checks (read-only audit). Replicates widget arithmetic exactly (JS int32 semantics).
function v2(n){ if(n===0) return Infinity; let c=0; while((n&1)===0){n>>=1;c++} return c }
function dropDepth(m){ return v2(3*m+1) }
function bounceRows(n0){
  let m=Math.max(3,n0); if(m%2===0)m++;
  const rows=[]; let acc=0;
  for(let i=0;i<80&&m>1;i++){
    while(m>1&&m%4===3){ m=(3*m+1)/2 }
    if(m<=1)break;
    const depth=dropDepth(m); const vm1=v2(m-1);
    const isBounce=vm1===3&&m%16===9&&((m-9)/16)%8===2;
    acc+=isBounce?1.92:0.5;
    rows.push({m,depth,isBounce,acc});
    let next=3*m+1; while(next%2===0) next>>=1; m=next;
  }
  return rows;
}
function exactRows(n0){ // BigInt reference
  let m=BigInt(n0); if(m%2n===0n)m++;
  const rows=[];
  for(let i=0;i<80&&m>1n;i++){
    while(m>1n&&m%4n===3n){ m=(3n*m+1n)/2n }
    if(m<=1n)break;
    let t=3n*m+1n, d=0; while(t%2n===0n){t/=2n; d++}
    const isBounce=(m%128n===41n);
    rows.push({m:m.toString(),depth:d,isBounce});
    m=t;
  }
  return rows;
}
for(const n of [76827,1227079,27,2919]){
  const r=bounceRows(n), e=exactRows(n);
  const B=Math.ceil(Math.log2(n+1));
  const same = r.length===e.length && r.every((x,i)=>String(x.m)===e[i].m && x.depth===e[i].depth && x.isBounce===e[i].isBounce);
  console.log(`n=${n} B=${B} rows=${r.length} widget==exact:${same}`);
  console.log('  bounce rows:', r.map((x,i)=>x.isBounce?i:null).filter(x=>x!==null).join(','), ' first deep (depth>=3) row:', r.findIndex(x=>x.depth>=3), ' first strong(depth>=4):', r.findIndex(x=>x.depth>=4));
  console.log('  types:', r.map((x,i)=>i+':'+(x.isBounce?'B':x.depth>=4?'S':x.depth>=3?'m':'w')).join(' '));
  console.log('  tally at each bounce row:', r.filter(x=>x.isBounce).map(x=>x.acc.toFixed(2)).join(','));
  const maxv = Math.max(...e.map(x=>Number(x.m)));
  console.log('  max Set3 value (exact):', maxv, ' 3m+1 >= 2^31 anywhere:', e.some(x=>3*Number(x.m)+1>=2**31));
}
// countdown: for m = 3 mod 4 below 200000: after the countdown ends at m' = 1 mod 4 and the step down S(m'), is the result still above m?
{
  let tot=0, above=0, aboveOrEq=0;
  for(let m=3;m<200000;m+=4){
    let x=BigInt(m);
    while(x%4n===3n) x=(3n*x+1n)/2n;
    let t=3n*x+1n; while(t%2n===0n) t/=2n;
    tot++; if(t>BigInt(m)) above++;
  }
  console.log(`countdown: m=3 mod 4 below 200000: ${tot} cases; next odd value after the step down still above start: ${(100*above/tot).toFixed(2)}%`);
}
// hailstone: share of n in 2..1000 whose orbit exceeds n
{
  let c=0, tot=0;
  for(let n=2;n<=1000;n++){ let x=n, mx=n; while(x!==1){ x=(x%2)?3*x+1:x/2; if(x>mx)mx=x } tot++; if(mx>n)c++ }
  console.log(`hailstone: ${c}/${tot} = ${(100*c/tot).toFixed(1)}% of n in 2..1000 climb above their start`);
}
// first n whose orbit exceeds 2^31 (int32 >> failure)
{
  let first=null;
  for(let n=2;n<200000&&first===null;n++){ let x=n; while(x!==1){ x=(x%2)?3*x+1:x/2; if(x>=2**31){first=n;break} } }
  console.log('first n whose orbit reaches 2^31:', first);
}
// alpha position chart
function syr(m){ let v=3*m+1; while(v%2===0) v/=2; return v }
function alphaPos(limit){
  const sum={1:0,2:0,3:0,4:0}, cnt={1:0,2:0,3:0,4:0}; let s4nf=0,c4nf=0,finals=0;
  for(let n=3;n<limit;n+=2){
    const orb=[n]; let m=n; while(m!==1){ m=syr(m); orb.push(m) }
    const s=orb.length-1; if(s<5) continue;
    for(let i=0;i<s;i++){ let a=v2big(3*orb[i]+1); const key=a>=4?4:a; const rp=i/(s-1); sum[key]+=rp; cnt[key]++; if(key===4){ if(i===s-1) finals++; else { s4nf+=rp; c4nf++ } } }
  }
  return {means:[1,2,3,4].map(k=>(sum[k]/cnt[k]).toFixed(3)), noFinal:(s4nf/c4nf).toFixed(3), finalShare:(finals/cnt[4]).toFixed(3)};
}
function v2big(x){ let c=0; while(x%2===0){x/=2;c++} return c }
console.log('alpha positions, odd 3..5999:', JSON.stringify(alphaPos(6000)));
console.log('alpha positions, odd 3..99999:', JSON.stringify(alphaPos(100000)));
// zoo explorer
function zoo(n,y,c,lim=500){
  const step=x=> (x%y===0)?Math.floor(x/y):n*x+c;
  let conv=0,cyc=0,div=0,tmo=0; const cycles=new Set();
  for(let x=3;x<lim;x+=2){ if(x%y===0) continue;
    const seen=new Set([x]); let cur=x, status='timeout';
    for(let i=0;i<2000;i++){ const nx=step(cur); cur=nx; if(nx===1){status='converged';break} if(nx<=0||nx>1e15){status='diverged';break} if(seen.has(nx)){status='cycle';break} seen.add(nx) }
    if(status==='converged')conv++; else if(status==='cycle')cyc++; else if(status==='diverged')div++; else tmo++;
  }
  const t=conv+cyc+div+tmo; return {conv,cyc,div,tmo,t, pct:[conv,cyc,div,tmo].map(v=>(100*v/t).toFixed(1))};
}
for(const [n,y,c] of [[3,2,1],[5,2,1],[7,2,1],[9,2,1],[3,2,3],[3,2,5],[3,2,7],[3,2,9],[3,2,11],[3,2,13]]) console.log(`zoo ${n}x+${c}, x/${y}:`, JSON.stringify(zoo(n,y,c)));
function mu(n,y,c){ let tot=0,cnt=0; for(let x=1;x<500;x++){ if(x%y===0)continue; let val=n*x+c,d=0; while(val>0&&val%y===0){val=Math.floor(val/y);d++} tot+=d;cnt++ } const avg=tot/cnt; return n/Math.pow(y,avg) }
console.log('mu(2,3,1)=',mu(2,3,1).toFixed(4),' mu(3,2,1)=',mu(3,2,1).toFixed(4),' mu(5,2,1)=',mu(5,2,1).toFixed(4));
// full-cycle census for 3x+c (true eventual cycles), odd starts 3..499 and 3..999
function census(c,lim){
  const cycles=new Map(); let through1=0, tot=0, unresolved=0;
  for(let x0=3;x0<lim;x0+=2){ tot++;
    let x=BigInt(x0); const seen=new Map(); let hit1=false, i=0, found=false;
    while(i<100000){ if(x===1n) hit1=true; if(seen.has(x)){found=true;break} seen.set(x,i); x=(x%2n===0n)?x/2n:3n*x+BigInt(c); i++ }
    if(!found){unresolved++;continue}
    // cycle min
    let mn=x, y=(x%2n===0n)?x/2n:3n*x+BigInt(c); while(y!==x){ if(y<mn)mn=y; y=(y%2n===0n)?y/2n:3n*y+BigInt(c) }
    cycles.set(mn.toString(),(cycles.get(mn.toString())||0)+1); if(hit1) through1++;
  }
  return {c,lim,cycles:[...cycles.keys()].length, mins:[...cycles.keys()].join(','), through1:(100*through1/tot).toFixed(1)+'%', unresolved};
}
for(const c of [1,3,5,7,9,11,13]) console.log('census', JSON.stringify(census(c,500)));
for(const c of [1,3,5,7,9,11,13,15,17,19]) { const r=census(c,1000); console.log(`c=${c} starts 3..999: unresolved=${r.unresolved} cycles=${r.cycles}`) }
// rotation drift & epsilon
{
  let worst=0, at=0, worst6=0;
  for(let n=2;n<1000000;n++){ let x=n, w=0; while(x!==1){ if(x%2){ w+=Math.log2(1+1/(3*x)); x=3*x+1 } else x/=2 } if(w>worst){worst=w;at=n} if(n===99999) worst6=worst }
  console.log(`epsilon min over n<1e6: -${worst.toFixed(4)} at n=${at}; in log6 turns: ${(worst/Math.log2(6)).toFixed(4)}; residue=${Math.pow(2,worst).toFixed(4)}; max over n<1e5 (log2): ${worst6.toFixed(4)}`);
}
