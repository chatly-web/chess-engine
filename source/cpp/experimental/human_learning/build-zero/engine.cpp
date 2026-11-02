// Original native chess implementation. No external engine source or weights.
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include "tables.h"
#include "learned_scale.h"
#include <iomanip>
#ifndef CLASH_TT_REUSE
#define CLASH_TT_REUSE 2
#endif
#ifndef CLASH_EVAL_STYLE
#define CLASH_EVAL_STYLE 0
#endif
#ifndef CLASH_SEARCH_V3
#define CLASH_SEARCH_V3 0
#endif
#ifndef CLASH_SEARCH_V2
#define CLASH_SEARCH_V2 0
#endif
#ifndef CLASH_TACTICAL_GEN
#define CLASH_TACTICAL_GEN 0
#endif
using namespace std;
using Clock=chrono::steady_clock;
mutex outputMutex;void emit(const string&s){lock_guard<mutex> lock(outputMutex);cout<<s<<endl;}
int sign(int x){return (x>0)-(x<0);} int file(int s){return s&7;} int rankof(int s){return s>>3;}
struct Move {int from=-1,to=-1,promo=0; bool operator==(const Move&o)const{return from==o.from&&to==o.to&&promo==o.promo;} };
string sqname(int s){return string(1,'a'+file(s))+char('1'+rankof(s));}
string uci(Move m){return m.from<0?"0000":sqname(m.from)+sqname(m.to)+(m.promo?string(1,"  nbrqk"[m.promo]):"");}
const int dirs[8][2]={{1,0},{-1,0},{0,1},{0,-1},{1,1},{1,-1},{-1,1},{-1,-1}};
uint64_t zob[12][64],castlekeys[16],epkeys[8],turnkey;
uint64_t random64(uint64_t& x){x+=0x9e3779b97f4a7c15ULL;uint64_t z=x;z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
struct Board{
 array<int,64>b{};int side=1,castle=0,ep=-1,half=0,full=1;uint64_t pieceHash=0;int kingSquares[2]={-1,-1};
 void setPiece(int square,int piece){int old=b[square];if(abs(old)==6)kingSquares[old>0]=-1;if(abs(piece)==6)kingSquares[piece>0]=square;if(old)pieceHash^=zob[(old>0?0:6)+abs(old)-1][square];b[square]=piece;if(piece)pieceHash^=zob[(piece>0?0:6)+abs(piece)-1][square];}
 uint64_t hash()const{uint64_t h=castlekeys[castle]^(side<0?turnkey:0);if(ep>=0){for(int dx:{-1,1}){int from=ep-side*8+dx;if(from>=0&&from<64&&abs(file(from)-file(ep))==1&&b[from]==side&&b[ep-side*8]==-side&&!moved({from,ep,0}).check(side)){h^=epkeys[file(ep)];break;}}}return h^pieceHash;}
 int king(int c)const{return kingSquares[c>0];}
 bool attacks(int from,int to)const{
  int p=abs(b[from]),dx=file(to)-file(from),dy=rankof(to)-rankof(from);if(!p)return false;
  if(p==1)return abs(dx)==1&&dy==sign(b[from]);
  if(p==2)return (abs(dx)==1&&abs(dy)==2)||(abs(dx)==2&&abs(dy)==1);
  if(p==6)return max(abs(dx),abs(dy))==1;
  if(!((p==3&&abs(dx)==abs(dy))||(p==4&&(!dx||!dy))||(p==5&&(!dx||!dy||abs(dx)==abs(dy)))))return false;
  if(!dx&&!dy)return false;
  int step=sign(dx)+8*sign(dy);for(int s=from+step;s!=to;s+=step)if(b[s])return false;return true;
 }
 int mobility(int from)const{
  int p=abs(b[from]),c=sign(b[from]),x=file(from),y=rankof(from),count=0;
  if(p==2){constexpr int offsets[8][2]={{1,2},{2,1},{2,-1},{1,-2},{-1,-2},{-2,-1},{-2,1},{-1,2}};for(auto&d:offsets){int f=x+d[0],r=y+d[1];if(f>=0&&f<8&&r>=0&&r<8&&sign(b[r*8+f])!=c)count++;}return count;}
  if(p<3||p>5)return 0;
  for(int d=0;d<8;d++){if(p==3&&d<4)continue;if(p==4&&d>=4)continue;int f=x+dirs[d][0],r=y+dirs[d][1];while(f>=0&&f<8&&r>=0&&r<8){int piece=b[r*8+f];if(sign(piece)==c)break;count++;if(piece)break;f+=dirs[d][0];r+=dirs[d][1];}}
  return count;
 }
 bool attacked(int sq,int c)const{
  int x=file(sq),y=rankof(sq);
  for(int dx:{-1,1}){int f=x+dx,r=y-c;if(f>=0&&f<8&&r>=0&&r<8&&b[r*8+f]==c)return true;}
  constexpr int knight[8][2]={{1,2},{2,1},{2,-1},{1,-2},{-1,-2},{-2,-1},{-2,1},{-1,2}};
  for(auto&d:knight){int f=x+d[0],r=y+d[1];if(f>=0&&f<8&&r>=0&&r<8&&b[r*8+f]==2*c)return true;}
  for(int d=0;d<8;d++){int f=x+dirs[d][0],r=y+dirs[d][1],distance=1;while(f>=0&&f<8&&r>=0&&r<8){int p=b[r*8+f];if(p){if(sign(p)==c){int type=abs(p);if(type==5||(d<4&&type==4)||(d>=4&&type==3)||(distance==1&&type==6))return true;}break;}f+=dirs[d][0];r+=dirs[d][1];distance++;}}
  return false;
 }
 bool check(int c)const{int k=king(c);return k<0||attacked(k,-c);}
 Board moved(Move m)const{
  Board n=*this;int p=b[m.from],capt=b[m.to];n.half=(abs(p)==1||capt)?0:half+1;n.ep=-1;
  n.setPiece(m.from,0);n.setPiece(m.to,m.promo?side*m.promo:p);
  if(abs(p)==1){if(m.to==ep&&!capt){n.setPiece(m.to-side*8,0);n.half=0;}if(abs(m.to-m.from)==16)n.ep=(m.from+m.to)/2;}
  if(abs(p)==6){n.castle&=side>0?12:3;if(abs(m.to-m.from)==2){int rf=m.to>m.from?m.from+3:m.from-4;int rt=m.to>m.from?m.from+1:m.from-1;n.setPiece(rt,n.b[rf]);n.setPiece(rf,0);}}
  for(int s:{m.from,m.to}){if(s==0)n.castle&=~2;if(s==7)n.castle&=~1;if(s==56)n.castle&=~8;if(s==63)n.castle&=~4;}
  n.side=-side;if(side<0)n.full++;
#ifdef CLASH_VERIFY_HASH
  uint64_t verified=0;for(int sq=0;sq<64;sq++)if(n.b[sq])verified^=zob[(n.b[sq]>0?0:6)+abs(n.b[sq])-1][sq];if(verified!=n.pieceHash)throw runtime_error("piece hash mismatch");int verifiedKings[2]={-1,-1};for(int sq=0;sq<64;sq++)if(abs(n.b[sq])==6)verifiedKings[n.b[sq]>0]=sq;for(int c=0;c<2;c++)if(verifiedKings[c]!=n.kingSquares[c])throw runtime_error("king square mismatch");
#endif
  return n;
 }
 void legalInto(vector<Move>&ps,vector<Move>&result,bool tactical=false,bool firstOnly=false)const{
  ps.clear();result.clear();if(!firstOnly)ps.reserve(64);bool found=false;
  auto addOne=[&](Move m){if(firstOnly){if(!moved(m).check(side)){result.push_back(m);found=true;}}else ps.push_back(m);};
  auto add=[&](int f,int t){if(found)return;if(tactical&&!b[t]&&!(abs(b[f])==1&&(t==ep||rankof(t)==0||rankof(t)==7)))return;if(abs(b[f])==1&&(rankof(t)==0||rankof(t)==7)){for(int p:{5,4,3,2}){addOne({f,t,p});if(found)break;}}else addOne({f,t,0});};
  for(int s=0;s<64&&!found;s++)if(sign(b[s])==side){int p=abs(b[s]),x=file(s),y=rankof(s);
   if(p==1){int t=s+side*8;if(t>=0&&t<64&&!b[t]){add(s,t);int t2=s+side*16;if(y==(side>0?1:6)&&!b[t2])add(s,t2);}for(int dx:{-1,1}){int tx=x+dx,ty=y+side;if(tx>=0&&tx<8&&ty>=0&&ty<8){int t=ty*8+tx;if((sign(b[t])==-side&&abs(b[t])!=6)||(t==ep&&!b[t]&&b[t-side*8]==-side))add(s,t);}}}
   else if(p==2){for(int dx:{-2,-1,1,2})for(int dy:{-2,-1,1,2})if(abs(dx)+abs(dy)==3){int tx=x+dx,ty=y+dy;if(tx>=0&&tx<8&&ty>=0&&ty<8){int t=8*ty+tx;if(sign(b[t])!=side&&abs(b[t])!=6)add(s,t);}}}
   else {for(int d=0;d<8&&!found;d++){if(p==3&&d<4)continue;if(p==4&&d>=4)continue;int tx=x+dirs[d][0],ty=y+dirs[d][1];while(tx>=0&&tx<8&&ty>=0&&ty<8&&!found){int t=ty*8+tx;if(sign(b[t])==side)break;if(abs(b[t])!=6)add(s,t);if(b[t]||p==6)break;tx+=dirs[d][0];ty+=dirs[d][1];}}
    if(!found&&!tactical&&p==6&&s==(side>0?4:60)&&!check(side)){int bit=side>0?1:4;if((castle&bit)&&b[s+3]==side*4&&!b[s+1]&&!b[s+2]&&!attacked(s+1,-side)&&!attacked(s+2,-side))add(s,s+2);if((castle&(bit*2))&&b[s-4]==side*4&&!b[s-1]&&!b[s-2]&&!b[s-3]&&!attacked(s-1,-side)&&!attacked(s-2,-side))add(s,s-2);}
   }
  }
  if(firstOnly)return;result.reserve(ps.size());for(auto m:ps)if(!moved(m).check(side)){result.push_back(m);if(firstOnly)break;}
 }
 vector<Move> legal(bool tactical=false,bool firstOnly=false)const{vector<Move>ps,result;legalInto(ps,result,tactical,firstOnly);return result;}
 bool insufficient()const{int minors=0;bool knight=false;int bishopcolor=-1;for(int s=0;s<64;s++)if(b[s]&&abs(b[s])!=6){int p=abs(b[s]);if(p!=2&&p!=3)return false;minors++;if(p==2)knight=true;else{int col=(file(s)+rankof(s))&1;if(bishopcolor<0)bishopcolor=col;else if(col!=bishopcolor)return false;}}return minors<=1||(!knight&&minors>0);}
};
Board fen(string text){Board b;istringstream in(text);string pos,side,cs,ep; if(!(in>>pos>>side>>cs>>ep>>b.half>>b.full))throw runtime_error("incomplete FEN");int s=56;string names=" pnbrqk";for(char c:pos){if(c=='/')s-=16;else if(c>='1'&&c<='8')s+=c-'0';else{auto p=names.find(tolower(c));if(p==string::npos||s<0||s>=64)throw runtime_error("invalid FEN");b.b[s++]=(isupper(c)?1:-1)*int(p);}}b.side=side=="w"?1:-1;for(char c:cs){if(c=='K')b.castle|=1;if(c=='Q')b.castle|=2;if(c=='k')b.castle|=4;if(c=='q')b.castle|=8;}if(ep!="-"&&(ep.size()!=2||ep[0]<'a'||ep[0]>'h'||(ep[1]!='3'&&ep[1]!='6')))throw runtime_error("invalid EP");if(ep!="-")b.ep=(ep[1]-'1')*8+ep[0]-'a';int wk=0,bk=0;for(int i=0;i<64;i++){if(b.b[i]==6){wk++;b.kingSquares[1]=i;}if(b.b[i]==-6){bk++;b.kingSquares[0]=i;}if(abs(b.b[i])==1&&(rankof(i)==0||rankof(i)==7))throw runtime_error("pawn on back rank");}if(s!=8||wk!=1||bk!=1||(side!="w"&&side!="b")||b.half<0||b.full<1||b.ep>=64||b.check(-b.side))throw runtime_error("invalid FEN state");for(int sq=0;sq<64;sq++)if(b.b[sq])b.pieceHash^=zob[(b.b[sq]>0?0:6)+abs(b.b[sq])-1][sq];return b;}
const string START="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
struct PawnSquares {
 int data[64];int count=0;
 void push_back(int square){data[count++]=square;}
 const int*begin()const{return data;}
 const int*end()const{return data+count;}
};
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

struct Halt{};
struct Entry{uint64_t key=0,context=0;Move move;int depth=-1,score=0,flag=0,ruleHalf=0,span=5;};
struct ScoredMove {int score,ordinal;Move move;};
struct SearchBuffers {vector<Move>pseudo,legal;vector<ScoredMove>scored;};
struct StaticEvalEntry{uint64_t key=0;int score=0;bool valid=false;};
struct Engine{
 array<SearchBuffers,128>buffers;
 vector<Entry>tt;vector<StaticEvalEntry>staticCache;uint64_t evalHits=0,evalMisses=0;atomic<bool>stop{false};Clock::time_point deadline;uint64_t nodes=0,nodeLimit=~0ULL;Move killers[128][2];int history[2][64][64]={};vector<uint64_t> path;Move rootbest;int completed=0;int quietSpan[128]={};uint64_t safeCutoffs=0;
 Engine():tt(1<<18),staticCache(1<<17){for(auto&buffer:buffers){buffer.pseudo.reserve(256);buffer.legal.reserve(256);buffer.scored.reserve(256);}}
 int cachedEval(const Board&b,uint64_t key){auto&e=staticCache[key&(staticCache.size()-1)];if(e.valid&&e.key==key){evalHits++;return e.score;}evalMisses++;int score=evaluate(b);e={key,score,true};return score;}
 void tick(){nodes++;if(stop||(nodes&127)==0){if(stop||Clock::now()>=deadline||nodes>=nodeLimit)throw Halt{};}if(nodes>=nodeLimit)throw Halt{};}
 bool draw(const Board& b,uint64_t h)const{if(b.half>=100||b.insufficient())return true;int count=0;int start=max(0,int(path.size())-b.half-1);for(int i=start;i<int(path.size());i++)if(path[i]==h)count++;return count>=3;}
 int exchange(const Board& b,Move m)const{
  if(m.promo)return PIECE_VALUES_MG[m.promo];
  int victim=abs(b.b[m.to]);if(!victim&&abs(b.b[m.from])==1&&m.to==b.ep)victim=1;
  int gains[32]={PIECE_VALUES_MG[victim]},depth=0;Board pos=b.moved(m);int onSquare=abs(pos.b[m.to]);
  while(depth<30){Move attacker;int least=100000;
   for(int sq=0;sq<64;sq++)if(sign(pos.b[sq])==pos.side&&pos.attacks(sq,m.to)){
    Move next{sq,m.to,abs(pos.b[sq])==1&&(rankof(m.to)==0||rankof(m.to)==7)?5:0};
    int value=abs(pos.b[sq])==6?20000:PIECE_VALUES_MG[abs(pos.b[sq])];
    if(value<least&&!pos.moved(next).check(pos.side)){least=value;attacker=next;}
   }
   if(attacker.from<0)break;
   depth++;gains[depth]=PIECE_VALUES_MG[onSquare]-gains[depth-1];
   pos=pos.moved(attacker);onSquare=abs(pos.b[m.to]);
  }
  while(depth>0){gains[depth-1]=-max(-gains[depth-1],gains[depth]);depth--;}
  return gains[0];
 }
 int ordering(const Board&b,Move m,Move preferred,int ply){if(m==preferred)return 2000000;int victim=abs(b.b[m.to]);if(abs(b.b[m.from])==1&&m.to==b.ep)victim=1;if(victim){int base=1000000+10*PIECE_VALUES_MG[victim]-PIECE_VALUES_MG[abs(b.b[m.from])];if(CLASH_SEARCH_V2>=2&&PIECE_VALUES_MG[victim]<PIECE_VALUES_MG[abs(b.b[m.from])]&&exchange(b,m)<0)base-=950000;return base;}if(m.promo)return 900000+PIECE_VALUES_MG[m.promo];if(abs(b.b[m.from])==6&&abs(m.to-m.from)==2)return 880000;if(m==killers[ply][0])return 850000;if(m==killers[ply][1])return 800000;return history[b.side>0][m.from][m.to];}
 int search(const Board&b,int depth,int alpha,int beta,int ply=0,int qdepth=0,bool allowNull=true,bool priorUnique=true){
  tick();quietSpan[ply]=0;bool check=b.check(b.side);bool tactical=CLASH_TACTICAL_GEN&&depth<=0&&!check;auto&buf=buffers[ply];int cachedStand=0;bool haveStand=false;
  if(depth<=0&&!check){cachedStand=cachedEval(b,path.back());haveStand=true;int boundedAlpha=alpha,boundedBeta=beta;if(CLASH_SEARCH_V3&&ply){boundedAlpha=max(alpha,-30000+ply);boundedBeta=min(beta,30000-ply-1);}if(cachedStand>=boundedBeta&&boundedAlpha<boundedBeta){b.legalInto(buf.pseudo,buf.legal,false,true);if(buf.legal.empty()||draw(b,path.back()))return 0;return cachedStand;}}
  b.legalInto(buf.pseudo,buf.legal,tactical);auto&moves=buf.legal;if(moves.empty()){if(check)return -30000+ply;if(!tactical)return 0;b.legalInto(buf.pseudo,buf.legal,false,true);bool anyLegal=!moves.empty();moves.clear();if(!anyLegal)return 0;}uint64_t key=path.back();int occurrences=0;int historyStart=max(0,int(path.size())-b.half-1);
  for(int i=historyStart;i<int(path.size());i++)if(path[i]==key)occurrences++;
  if(b.half>=100||b.insufficient()||occurrences>=3)return 0;
  bool nodeUnique=b.half==0||(priorUnique&&occurrences<=1);if(ply>=120)return cachedEval(b,path.back());
  bool q=depth<=0;
  if(CLASH_SEARCH_V3&&ply){alpha=max(alpha,-30000+ply);beta=min(beta,30000-ply-1);if(alpha>=beta)return alpha;}
  int original=alpha;uint64_t ctx=uint64_t(b.half);for(int i=max(0,int(path.size())-b.half-1);i<int(path.size());i++)ctx^=path[i]+0x9e3779b97f4a7c15ULL+(ctx<<6)+(ctx>>2);
  Entry entry=tt[key&(tt.size()-1)];Move preferred=entry.key==key?entry.move:Move{};
  bool exactHistory=entry.context==ctx;bool sameRuleClock=entry.ruleHalf==b.half||(entry.span>=0&&entry.span<120&&entry.ruleHalf+entry.span<100&&b.half+entry.span<100);bool safeHistory=nodeUnique&&sameRuleClock&&entry.span>=0&&(CLASH_TT_REUSE==1?entry.span<5:CLASH_TT_REUSE==2&&b.half<70&&entry.ruleHalf<70&&abs(entry.score)<20000);
  if(!q&&ply&&entry.key==key&&(exactHistory||safeHistory)&&entry.depth>=depth){int v=entry.score;if(v>28000)v-=ply;if(v< -28000)v+=ply;if(entry.flag==0||(entry.flag==1&&v>=beta)||(entry.flag==-1&&v<=alpha)){quietSpan[ply]=entry.span>=0?entry.span:120;if(!exactHistory)safeCutoffs++;return v;}}
  int staticValue=0;
  if((CLASH_SEARCH_V3&1)&&!q&&ply&&!check&&depth<=3&&beta-alpha==1&&abs(beta)<20000){
   staticValue=cachedEval(b,path.back());if(staticValue-depth*125>=beta)return staticValue;
  }
  if(q&&!check){int stand=haveStand?cachedStand:cachedEval(b,path.back());staticValue=stand;if(stand>=beta)return stand;alpha=max(alpha,stand);if(qdepth>=16)return alpha;moves.erase(remove_if(moves.begin(),moves.end(),[&](Move m){return !b.b[m.to]&&!m.promo&&!(abs(b.b[m.from])==1&&m.to==b.ep);}),moves.end());}
  if(!q&&depth>=3&&ply&&!check&&allowNull&&beta-alpha==1){bool pieces=false;for(int p:b.b)if(sign(p)==b.side&&abs(p)>1&&abs(p)<6)pieces=true;if(pieces){Board n=b;n.side=-n.side;n.ep=-1;path.push_back(n.hash());int v;try{v=-search(n,depth-3,-beta,-beta+1,ply+1,0,false,false);}catch(...){path.pop_back();throw;}path.pop_back();if(v>=beta&&abs(v)<28000){quietSpan[ply]=120;return v;}}}
  auto&scored=buf.scored;scored.clear();scored.reserve(moves.size());for(auto move:moves)scored.push_back({ordering(b,move,preferred,ply),int(scored.size()),move});sort(scored.begin(),scored.end(),[](const auto&a,const auto&z){return a.score>z.score||(a.score==z.score&&a.ordinal<z.ordinal);});for(size_t i=0;i<moves.size();i++)moves[i]=scored[i].move;int best=-32000;Move bm;
  for(int i=0;i<int(moves.size());i++){Move m=moves[i];Board n=b.moved(m);bool quiet=!b.b[m.to]&&!m.promo&&!(abs(b.b[m.from])==1&&m.to==b.ep);if((CLASH_SEARCH_V3&2)&&q&&!check&&!m.promo&&!n.check(n.side)&&b.half<80){
    int victim=abs(b.b[m.to]);if(!victim&&abs(b.b[m.from])==1&&m.to==b.ep)victim=1;
    // Conservative delta bound, and exchange ordering reused for non-checking captures.
    if(staticValue+PIECE_VALUES_MG[victim]+220<alpha)continue;
    if(exchange(b,m)<-80)continue;
   }
   int nd=depth-1+(CLASH_SEARCH_V2>=1&&!q&&check&&ply<24?1:0);int reduction=!q&&depth>=3&&i>=4&&quiet&&!check&&!n.check(n.side)?1:0;if((CLASH_SEARCH_V3&4)&&reduction&&depth>=6&&i>=10&&!(m==killers[ply][0])&&!(m==killers[ply][1])&&history[b.side>0][m.from][m.to]<depth*depth*8)reduction=2;
   path.push_back(n.hash());int v;
   auto descend=[&](int d,int lo,int hi,int qd=0){int score=-search(n,d,lo,hi,ply+1,qd,true,nodeUnique);if(n.half)quietSpan[ply]=max(quietSpan[ply],min(120,quietSpan[ply+1]+1));return score;};
   try{if(i==0||q)v=descend(nd,-beta,-alpha,q?qdepth+1:0);else{v=descend(nd-reduction,-alpha-1,-alpha);if(reduction&&v>alpha)v=descend(nd,-alpha-1,-alpha);if(v>alpha&&v<beta)v=descend(nd,-beta,-alpha);}}catch(...){path.pop_back();throw;}path.pop_back();if(v>best){best=v;bm=m;}alpha=max(alpha,v);if(alpha>=beta){if(quiet){killers[ply][1]=killers[ply][0];killers[ply][0]=m;auto&h=history[b.side>0][m.from][m.to];h=min(70000,h+max(1,depth)*max(1,depth));}break;}
  }
  if(!q){int v=best;if(v>28000)v+=ply;if(v< -28000)v-=ply;tt[key&(tt.size()-1)]={key,ctx,bm,depth,v,best<=original?-1:best>=beta?1:0,b.half,nodeUnique?quietSpan[ply]:-1};if(!ply)rootbest=bm;return best;}return alpha;
 }
 Move choose(Board b,vector<uint64_t> historyPath,double seconds,int maxdepth,uint64_t limit){nodes=0;completed=0;safeCutoffs=0;evalHits=evalMisses=0;nodeLimit=limit;rootbest={};deadline=Clock::now()+chrono::duration_cast<Clock::duration>(chrono::duration<double>(seconds));path=historyPath;if(path.empty()||path.back()!=b.hash())throw runtime_error("search history does not match board");auto moves=b.legal();if(moves.empty())return {};if(moves.size()==1){emit("info string forced legal move");return moves[0];}bool rootUnique=true;for(int i=max(0,int(path.size())-b.half-1);i<int(path.size());i++)for(int j=i+1;j<int(path.size());j++)if(path[i]==path[j])rootUnique=false;
  Move best=moves[0];int previousScore=0;auto start=Clock::now();if(seconds<=0)return best;
  for(int d=1;d<=min(100,maxdepth);d++){try{if(Clock::now()>=deadline||stop)break;int value;if(CLASH_SEARCH_V2>=1&&d>=4&&abs(previousScore)<28000){int lo=max(-32000,previousScore-40),hi=min(32000,previousScore+40);value=search(b,d,lo,hi,0,0,true,rootUnique);if(value<=lo||value>=hi)value=search(b,d,-32000,32000,0,0,true,rootUnique);}else value=search(b,d,-32000,32000,0,0,true,rootUnique);previousScore=value;if(rootbest.from>=0)best=rootbest;completed=d;auto ms=chrono::duration_cast<chrono::milliseconds>(Clock::now()-start).count();ostringstream out;out<<"info depth "<<d<<" score ";if(abs(value)>28000)out<<"mate "<<(value>0?1:-1)*((30000-abs(value)+1)/2);else out<<"cp "<<value;out<<" nodes "<<nodes<<" time "<<ms<<" pv "<<uci(best);emit(out.str());if(abs(value)>28000)break;}catch(Halt&){break;}}
  emit("info string history_guarded_tt_cutoffs "+to_string(safeCutoffs)+" static_eval_hits "+to_string(evalHits)+" misses "+to_string(evalMisses));return best;
 }
};
uint64_t perft(const Board&b,int d){if(!d)return 1;uint64_t n=0;for(auto m:b.legal())n+=perft(b.moved(m),d-1);return n;}
int main(){uint64_t seed=191827;for(auto&row:zob)for(auto&v:row)v=random64(seed);for(auto&v:castlekeys)v=random64(seed);for(auto&v:epkeys)v=random64(seed);turnkey=random64(seed);
 Board board=fen(START);vector<uint64_t>path{board.hash()};Engine engine;thread worker;
 auto halt=[&](){if(worker.joinable()){engine.stop=true;worker.join();}};
 string line;while(getline(cin,line)){istringstream in(line);string cmd;in>>cmd;try{
  if(cmd=="uci")emit(string("id name Clash Native C++ learning candidate weights ")+WEIGHTS_ID+"\nid author AI-assisted original development\nuciok");
  else if(cmd=="isready")emit("readyok");
  else if(cmd=="quit"){halt();break;}
  else if(cmd=="stop")halt();
  else if(cmd=="ucinewgame"){halt();fill(engine.tt.begin(),engine.tt.end(),Entry{});fill(engine.staticCache.begin(),engine.staticCache.end(),StaticEvalEntry{});board=fen(START);path={board.hash()};}
  else if(cmd=="position"){halt();string kind;in>>kind;Board n;string tok;if(kind=="startpos")n=fen(START);else if(kind=="fen"){string f;for(int i=0;i<6;i++){if(!(in>>tok))throw runtime_error("incomplete position");f+=tok+" ";}n=fen(f);}else throw runtime_error("unknown position format");vector<uint64_t>hist{n.hash()};if(in>>tok){if(tok!="moves")throw runtime_error("expected moves");while(in>>tok){bool found=false;for(auto m:n.legal())if(uci(m)==tok){n=n.moved(m);hist.push_back(n.hash());found=true;break;}if(!found)throw runtime_error("illegal position move");}}board=n;path=hist;}
  else if(cmd=="legalcaptures"){halt();for(auto m:board.legal(true))cout<<uci(m)<<" ";cout<<endl;}
  else if(cmd=="legal"){halt();for(auto m:board.legal())cout<<uci(m)<<" ";cout<<endl;}
  else if(cmd=="eval"){halt();cout<<evaluate(board)<<endl;}
  else if(cmd=="features"){halt();array<double,MODEL_FEATURES>v;int score=evaluateGroups<true>(board,&v);ostringstream out;out<<"info string features "<<score*board.side;for(double x:v)out<<" "<<setprecision(12)<<x;emit(out.str());}
  else if(cmd=="perft"){halt();int depth;in>>depth;if(depth<0||depth>6)throw runtime_error("perft range");cout<<perft(board,depth)<<endl;}
  else if(cmd=="go"){halt();long long wt=10000,bt=10000,wi=0,bi=0,mt=-1,moves=30,nodes=-1;int depth=100;bool infinite=false,hasclock=false,hasdepth=false;string k;while(in>>k){if(k=="infinite"){infinite=true;continue;}long long v;if(k=="wtime"||k=="btime"||k=="winc"||k=="binc"||k=="movetime"||k=="depth"||k=="nodes"||k=="movestogo"){if(!(in>>v))throw runtime_error("missing go value");v=max(0LL,v);if(k=="wtime"){wt=v;hasclock=true;}if(k=="btime"){bt=v;hasclock=true;}if(k=="winc")wi=v;if(k=="binc")bi=v;if(k=="movetime")mt=v;if(k=="depth"){depth=max(1LL,v);hasdepth=true;}if(k=="nodes")nodes=v;if(k=="movestogo")moves=max(1LL,v);}}
   double remaining=(board.side>0?wt:bt)/1000.,inc=(board.side>0?wi:bi)/1000.;double seconds=min({remaining-min(.25,remaining*.2),remaining/double(moves)+.65*inc,remaining*.25});if(mt>=0){double av=mt/1000.;seconds=max(0.,av-min(.05,av*.2));}else if(infinite||(!hasclock&&(hasdepth||nodes>=0)))seconds=86400;engine.stop=false;worker=thread([&,b=board,h=path,seconds,depth,nodes](){try{Move m=engine.choose(b,h,max(0.,seconds),depth,nodes<0?~0ULL:uint64_t(nodes));emit("bestmove "+uci(m));}catch(exception&e){cerr<<"search error: "<<e.what()<<endl;auto legal=b.legal();emit("bestmove "+(legal.empty()?string("0000"):uci(legal[0])));}});
  }
 }catch(exception&e){cerr<<"input error: "<<e.what()<<endl;}}
 halt();return 0;
}
