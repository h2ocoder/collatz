// Which widgets silently go wrong above the 32-bit limit? Replicates their loops exactly.
function v2(n){ if(n===0) return Infinity; let c=0; while((n&1)===0){n>>=1;c++} return c }
function bounceRowsWidget(n0){ let m=Math.max(3,n0); if(m%2===0)m++; const rows=[];
  for(let i=0;i<80&&m>1;i++){ while(m>1&&m%4===3){m=(3*m+1)/2} if(m<=1)break; rows.push(m); let next=3*m+1; while(next%2===0) next>>=1; m=next } return rows }
function bounceRowsExact(n0){ let m=BigInt(n0); if(m%2n===0n)m++; const rows=[];
  for(let i=0;i<80&&m>1n;i++){ while(m>1n&&m%4n===3n){m=(3n*m+1n)/2n} if(m<=1n)break; rows.push(Number(m)); let t=3n*m+1n; while(t%2n===0n)t/=2n; m=t } return rows }
function countdownWidget(n0){ let m=Math.max(3,n0); if(m%2===0)m++; const out=[]; for(let i=0;i<60&&m>1;i++){ out.push(m); let next=3*m+1; while(next%2===0) next>>=1; m=next } return out }
function countdownExact(n0){ let m=BigInt(n0); if(m%2n===0n)m++; const out=[]; for(let i=0;i<60&&m>1n;i++){ out.push(Number(m)); let t=3n*m+1n; while(t%2n===0n)t/=2n; m=t } return out }
function firstBad(w,e,lim){ for(let n=3;n<lim;n+=2){ const a=w(n), b=e(n); if(a.length!==b.length||a.some((x,i)=>x!==b[i])) return {n, widget:a.slice(-3), exactLen:b.length, widgetLen:a.length} } return null }
console.log('BounceSimulator first odd start with wrong rows:', JSON.stringify(firstBad(bounceRowsWidget,bounceRowsExact,400000)));
console.log('CountdownVisualizer first odd start with wrong rows:', JSON.stringify(firstBad(countdownWidget,countdownExact,400000)));
