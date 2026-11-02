// Semantic evaluation groups. Features and scores come only from our own evaluator.
int unsafeMobility(const Board& b,int from,uint64_t enemyPawnAttacks){
 int p=abs(b.b[from]),c=sign(b.b[from]),x=file(from),y=rankof(from),count=0;
 auto countSquare=[&](int square){if(enemyPawnAttacks&(uint64_t(1)<<square))count++;};
 if(p==2){constexpr int offsets[8][2]={{1,2},{2,1},{2,-1},{1,-2},{-1,-2},{-2,-1},{-2,1},{-1,2}};for(auto&d:offsets){int f=x+d[0],r=y+d[1];if(f>=0&&f<8&&r>=0&&r<8&&sign(b.b[r*8+f])!=c)countSquare(r*8+f);}return count;}
 if(p<3||p>5)return 0;
 for(int d=0;d<8;d++){if(p==3&&d<4)continue;if(p==4&&d>=4)continue;int f=x+dirs[d][0],r=y+dirs[d][1];while(f>=0&&f<8&&r>=0&&r<8){int piece=b.b[r*8+f];if(sign(piece)==c)break;countSquare(r*8+f);if(piece)break;f+=dirs[d][0];r+=dirs[d][1];}}
 return count;
}
template<bool Collect>
int evaluateGroups(const Board& b,array<double,MODEL_FEATURES>*dump){
 int phase=0,mg=0,eg=0;int pawns[2][8]={},bishops[2]={},kings[2]={};PawnSquares pawnSquares[2];
 int groupMG[MODEL_GROUPS]={},groupEG[MODEL_GROUPS]={};
 auto add=[&](int group,int m,int e,int sg=1){if constexpr(Collect){groupMG[group]+=sg*m;groupEG[group]+=sg*e;}};
 for(int s=0;s<64;s++)if(b.b[s]){int p=abs(b.b[s]),c=b.b[s]>0?1:0;if(p==1){pawns[c][file(s)]++;pawnSquares[c].push_back(s);}if(p==6)kings[c]=s;if(p==3)bishops[c]++;phase+=p==2||p==3?1:p==4?2:p==5?4:0;}
 phase=min(24,phase);
 for(int s=0;s<64;s++)if(b.b[s]){int p=abs(b.b[s]),c=b.b[s]>0?1:0,sg=c?1:-1,sq=c?s:s^56,f=file(s),r=c?rankof(s):7-rankof(s);int m=PIECE_VALUES_MG[p]+PST_MG[p][sq],e=PIECE_VALUES_EG[p]+PST_EG[p][sq];
  add(0,PIECE_VALUES_MG[p],PIECE_VALUES_EG[p],sg);add(p==1?1:p<=3?2:p<=5?3:4,PST_MG[p][sq],PST_EG[p][sq],sg);
  int beforeM=m,beforeE=e;
  if(p==1){bool passed=true;for(int t:pawnSquares[1-c])if(abs(file(t)-f)<=1&&(c?rankof(t)>rankof(s):rankof(t)<rankof(s)))passed=false;if(passed&&r>=2){int idx=min(5,r-1);m+=PASSED_BONUS_MG[idx];e+=PASSED_BONUS_EG[idx];if(phase<=16){auto dist=[](int a,int z){return max(abs(file(a)-file(z)),abs(rankof(a)-rankof(z)));};e+=(7-dist(kings[c],s))*EVAL_COEFFICIENT_12-(7-dist(kings[1-c],s))*EVAL_COEFFICIENT_16;}}}
  add(5,m-beforeM,e-beforeE,sg);beforeM=m;beforeE=e;
  if(p==4){if(!pawns[0][f]&&!pawns[1][f]){m+=EVAL_COEFFICIENT_25;e+=EVAL_COEFFICIENT_15;}else if(!pawns[c][f]){m+=EVAL_COEFFICIENT_15;e+=EVAL_COEFFICIENT_10;}if(r==6){m+=EVAL_COEFFICIENT_30;e+=EVAL_COEFFICIENT_35;}}
  add(6,m-beforeM,e-beforeE,sg);mg+=sg*m;eg+=sg*e;
 }
 for(int c=0;c<2;c++){int sg=c?1:-1,m=0,e=0;
  if(bishops[c]>=2){m+=EVAL_COEFFICIENT_35;e+=EVAL_COEFFICIENT_50;add(7,EVAL_COEFFICIENT_35,EVAL_COEFFICIENT_50,sg);}
  for(int f=0;f<8;f++){if(pawns[c][f]>1){m-=EVAL_COEFFICIENT_15;e-=EVAL_COEFFICIENT_20;add(8,-EVAL_COEFFICIENT_15,-EVAL_COEFFICIENT_20,sg);}if(pawns[c][f]&&!(f>0&&pawns[c][f-1])&&!(f<7&&pawns[c][f+1])){m-=EVAL_COEFFICIENT_15;e-=EVAL_COEFFICIENT_18;add(9,-EVAL_COEFFICIENT_15,-EVAL_COEFFICIENT_18,sg);}}
  int k=kings[c],f=file(k),r=c?rankof(k):7-rankof(k);int beforeM=m,beforeE=e;
  if(phase>=20){for(int s:{1,2,5,6}){int sq=c?s:s^56;if(b.b[sq]==sg*2||b.b[sq]==sg*3)m-=EVAL_COEFFICIENT_32;}}
  add(10,m-beforeM,e-beforeE,sg);
  if(phase>8){beforeM=m;beforeE=e;bool sheltered=(f>=6||f<=2)&&r==0;
   if(sheltered){int shield=0;int lo=f>=6?5:0;for(int t=0;t<64;t++)if(b.b[t]==sg&&file(t)>=lo&&file(t)<=lo+2){int rr=c?rankof(t):7-rankof(t);if(rr==1||rr==2)shield++;}if(shield<3)m-=(3-shield)*(f>=6?EVAL_COEFFICIENT_25:EVAL_COEFFICIENT_20);m+=f>=6?EVAL_COEFFICIENT_35:EVAL_COEFFICIENT_30;
    if(f>=6){int open[]={EVAL_COEFFICIENT_45,EVAL_COEFFICIENT_65,EVAL_COEFFICIENT_55},semi[]={EVAL_COEFFICIENT_25,EVAL_COEFFICIENT_40,EVAL_COEFFICIENT_30};for(int j=0;j<3;j++){int ff=5+j;if(!pawns[0][ff]&&!pawns[1][ff])m-=open[j];else if(!pawns[c][ff])m-=semi[j];}}
    else{for(int ff:{1,2}){if(!pawns[0][ff]&&!pawns[1][ff])m-=ff==1?EVAL_COEFFICIENT_60:EVAL_COEFFICIENT_45;else if(!pawns[c][ff])m-=ff==1?EVAL_COEFFICIENT_35:EVAL_COEFFICIENT_25;}}
   }else{m-=CLASH_EVAL_STYLE==3?72:EVAL_COEFFICIENT_110;if(!pawns[0][f]&&!pawns[1][f])m-=EVAL_COEFFICIENT_50;else if(!pawns[c][f])m-=EVAL_COEFFICIENT_30;if(!(b.castle&(c?3:12)))m-=CLASH_EVAL_STYLE==3?40:EVAL_COEFFICIENT_60;}
   add(sheltered?11:12,m-beforeM,e-beforeE,sg);
   int ring[8],ringSize=0;for(auto&delta:dirs){int xx=f+delta[0],yy=rankof(k)+delta[1];if(xx>=0&&xx<8&&yy>=0&&yy<8)ring[ringSize++]=yy*8+xx;}
   int attack=0;for(int s=0;s<64;s++)if(sign(b.b[s])==-sg&&abs(b.b[s])>1&&abs(b.b[s])<6){bool hits=false;for(int i=0;i<ringSize;i++)if(b.attacks(s,ring[i])){hits=true;break;}if(hits)attack+=abs(b.b[s])==5?50:abs(b.b[s])==4?35:25;}
   beforeM=m;m-=CLASH_EVAL_STYLE==3?attack*(attack>=80?5:attack>=50?3:2)/2:attack*(attack>=80?3:attack>=50?2:1);add(13,m-beforeM,0,sg);
   int enemyKing=kings[1-c];beforeM=m;
   for(int t=0;t<64;t++)if(b.b[t]==sg*5){int queenBefore=m;int d=max(abs(file(t)-file(enemyKing)),abs(rankof(t)-rankof(enemyKing)));if(d<=3)m+=(4-d)*EVAL_COEFFICIENT_35;int ownDist=max(abs(file(t)-f),abs(rankof(t)-rankof(k)));if(attack>=50){if(ownDist<=2)m+=EVAL_COEFFICIENT_45;else if(ownDist>=4)m-=EVAL_COEFFICIENT_75;}else{if(ownDist<=2)m+=EVAL_COEFFICIENT_25;else if(ownDist>=4)m-=EVAL_COEFFICIENT_35;}if(CLASH_EVAL_STYLE==3)m=queenBefore+(m-queenBefore)/2;}
   add(14,m-beforeM,0,sg);beforeM=m;
   bool thorn=false;for(int t:pawnSquares[1-c])if(abs(file(t)-f)<=1){int rr=c?rankof(t):7-rankof(t);if(rr==1||rr==2)thorn=true;}if(thorn)m-=CLASH_EVAL_STYLE==3?47:EVAL_COEFFICIENT_70;
   add(15,m-beforeM,0,sg);beforeM=m;
   for(int ff=max(0,f-1);ff<=min(7,f+1);ff++)if(!pawns[c][ff]){bool rook=false,queen=false;for(int t=ff;t<64;t+=8){if(b.b[t]==-sg*4)rook=true;if(b.b[t]==-sg*5)queen=true;}if(rook)m-=CLASH_EVAL_STYLE==3?27:EVAL_COEFFICIENT_40;if(queen)m-=CLASH_EVAL_STYLE==3?35:EVAL_COEFFICIENT_50;}
   add(16,m-beforeM,0,sg);
  }
  beforeE=e;
  if(phase<=16&&(r==0||f==0||f==7)){int other=kings[1-c];bool major=false;for(int s=0;s<64;s++)if(sign(b.b[s])==-sg&&(abs(b.b[s])==4||abs(b.b[s])==5))major=true;if(major&&max(abs(file(k)-file(other)),abs(rankof(k)-rankof(other)))<=2)e-=EVAL_COEFFICIENT_160;}
  add(17,0,e-beforeE,sg);mg+=sg*m;eg+=sg*e;
 }
 if constexpr ((EVAL_MOBILITY_MG | EVAL_MOBILITY_EG | CLASH_EVAL_STYLE)!=0){int mobility=0;for(int from=0;from<64;from++)if(abs(b.b[from])>1&&abs(b.b[from])<6)mobility+=sign(b.b[from])*b.mobility(from);int m=mobility*(EVAL_MOBILITY_MG+(CLASH_EVAL_STYLE==3?2:CLASH_EVAL_STYLE==4?3:0)),e=mobility*(EVAL_MOBILITY_EG+(CLASH_EVAL_STYLE==3?1:CLASH_EVAL_STYLE==4?2:0));mg+=m;eg+=e;add(18,m,e);}
 int base=((mg*phase+eg*(24-phase))/24)*b.side+EVAL_TEMPO;
 if constexpr(Collect){
  if(dump){int m=0,e=0;for(int i=0;i<19;i++){m+=groupMG[i];e+=groupEG[i];}if(m!=mg||e!=eg)throw runtime_error("evaluation feature accounting mismatch");}
  groupMG[19]=groupEG[19]=EVAL_TEMPO*b.side;
  if(dump||(MODEL_DELTAS[40]!=0.0||MODEL_DELTAS[41]!=0.0)){uint64_t attacks[2]={};for(int c=0;c<2;c++)for(int square:pawnSquares[c])for(int dx:{-1,1}){int f=file(square)+dx,r=rankof(square)+(c?1:-1);if(f>=0&&f<8&&r>=0&&r<8)attacks[c]|=uint64_t(1)<<(r*8+f);}int unsafe=0;for(int from=0;from<64;from++)if(abs(b.b[from])>1&&abs(b.b[from])<6)unsafe+=sign(b.b[from])*unsafeMobility(b,from,attacks[b.b[from]>0?0:1]);groupMG[20]=unsafe*2;groupEG[20]=unsafe;}
  array<double,MODEL_FEATURES>features{};double correction=0;
  for(int i=0;i<MODEL_GROUPS;i++){features[2*i]=double(groupMG[i])*phase/24.0;features[2*i+1]=double(groupEG[i])*(24-phase)/24.0;correction+=features[2*i]*MODEL_DELTAS[2*i]+features[2*i+1]*MODEL_DELTAS[2*i+1];}
  if(dump){*dump=features;return base;}
  return max(-24000,min(24000,base+b.side*int(llround(correction))));
 }
 return base;
}
int evaluate(const Board& b){return evaluateGroups<MODEL_ACTIVE>(b,nullptr);}
