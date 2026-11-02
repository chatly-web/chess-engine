#define main clash_protocol_main
#include "engine.cpp"
#undef main
#include <cassert>
#ifdef NDEBUG
#error "Compile unit checks without NDEBUG"
#endif
#if !CLASH_CLUSTER_TT
#error "Required architecture feature is disabled in this test"
#endif
int main(){
#if CLASH_CLUSTER_TT
 static_assert(sizeof(Entry)==48,"Keep the baseline 12MiB entry budget");
 Engine e;assert(e.tt.size()==(1u<<18));e.generation=1;
 uint64_t stride=e.tt.size()/4;
 for(int i=0;i<4;i++)e.storeTT(7+stride*i,100+i,Move{1,2,0},(i==0?12:i==1?8:i==2?5:3),50+i,0,10,2);
 e.storeTT(7+stride*4,104,Move{2,3,0},6,70,0,10,2);
 assert(e.probeTT(7,100,10,true).depth==12);assert(e.probeTT(7+stride*3,103,10,true).depth<0);
 e.storeTT(7,100,Move{3,4,0},2,999,1,10,2);auto retained=e.probeTT(7,100,10,true);assert(retained.depth==12&&retained.score==50);
 // Different reversible histories can coexist in a cluster.
 e.storeTT(19,501,Move{1,3,0},4,10,0,80,-1);e.storeTT(19,502,Move{2,4,0},10,20,0,80,-1);
 assert(e.probeTT(19,501,80,false).context==501);assert(e.probeTT(19,502,80,false).context==502);
 // Fresh shallow data replaces old entries; timestamps cross uint16 wrap correctly.
 Engine f;f.generation=65535;for(int i=0;i<4;i++)f.storeTT(9+stride*i,1,Move{1,2,0},10+i,30,0,5,1);
 f.generation=0;f.storeTT(9,1,Move{2,3,0},1,900,1,5,1);assert(f.probeTT(9,1,5,true).depth==10);
 f.generation=40;f.storeTT(9,1,Move{2,3,0},1,900,1,5,1);assert(f.probeTT(9,1,5,true).depth==1);
#endif
 std::cout<<"PASS: table byte budget, colliding keys, history contexts, deep-result retention, aging and timestamp wrap\n";
}
