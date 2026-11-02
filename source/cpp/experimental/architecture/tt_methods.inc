 // Original four-slot table: same entry count/byte budget, distinct history contexts.
 bool historyUsable(const Entry&e,uint64_t ctx,int half,bool unique)const{
  if(e.context==ctx)return true;
  bool clock=e.ruleHalf==half||(e.span>=0&&e.span<120&&e.ruleHalf+e.span<100&&half+e.span<100);
  return unique&&clock&&e.span>=0&&(CLASH_TT_REUSE==1?e.span<5:CLASH_TT_REUSE==2&&half<70&&e.ruleHalf<70&&abs(e.score)<20000);
 }
 Entry probeTT(uint64_t key,uint64_t ctx,int half,bool unique){
#if CLASH_CLUSTER_TT
  ttProbes++;size_t base=(key&((tt.size()/4)-1))*4;Entry best;int priority=-100000;
  for(size_t i=base;i<base+4;i++){auto&e=tt[i];if(e.depth<0||e.key!=key)continue;
   int rank=(historyUsable(e,ctx,half,unique)?10000:0)+e.depth*16+(e.context==ctx?4:0)+(e.flag==0?2:0);
   if(rank>priority){priority=rank;best=e;}
  }
  if(best.depth>=0)ttHits++;return best;
#else
  return tt[key&(tt.size()-1)];
#endif
 }
 void storeTT(uint64_t key,uint64_t ctx,Move move,int depth,int score,int flag,int half,int span){
#if CLASH_CLUSTER_TT
#ifdef CLASH_VERIFY_TT
  if(half<0||half>=100||span< -1||span>120)throw runtime_error("TT rule metadata out of range");
#endif
  size_t base=(key&((tt.size()/4)-1))*4,target=base;int lowest=100000;
  for(size_t i=base;i<base+4;i++){auto&e=tt[i];
   if(e.depth<0){target=i;break;}
   unsigned age=uint16_t(generation-e.age);
   if(e.key==key&&e.context==ctx){
    if(e.flag==0&&e.depth>depth+2&&age<=1){e.age=generation;return;}
    target=i;break;
   }
   int retention=e.depth*8+(e.flag==0?4:0)-int(min(32u,age))*16;
   if(retention<lowest){lowest=retention;target=i;}
  }
  auto&e=tt[target];if(e.depth>=0&&(e.key!=key||e.context!=ctx))ttReplacements++;
  e.key=key;e.context=ctx;e.move=move;e.depth=depth;e.score=score;e.flag=int8_t(flag);e.ruleHalf=int16_t(half);e.span=int16_t(span);e.age=generation;
#else
  tt[key&(tt.size()-1)]={key,ctx,move,depth,score,flag,half,span};
#endif
 }
