#define main clash_protocol_main
#include "engine.cpp"
#undef main
#include <cassert>
#ifdef NDEBUG
#error "Compile unit checks without NDEBUG"
#endif
#if !CLASH_SAFE_NULL
#error "Required architecture feature is disabled in this test"
#endif
int main(){
 uint64_t seed=191827;for(auto&row:zob)for(auto&v:row)v=random64(seed);for(auto&v:castlekeys)v=random64(seed);for(auto&v:epkeys)v=random64(seed);turnkey=random64(seed);
 uint64_t verified=0,rejected=0,cutoffs=0,interrupts=0;int cases=0;
 for(auto text:{"8/8/8/2k5/8/2K5/4P3/4N3 w - - 0 1","4k3/3p4/8/8/2K5/8/8/4r3 b - - 0 1","8/1p6/1k6/8/8/4K3/4P3/3B4 w - - 0 1"}){
  Board b=fen(text);
  for(int limit:{128,256,512,1024,4096,20000}){
   Engine e;e.path={b.hash()};e.deadline=Clock::now()+chrono::seconds(10);e.nodeLimit=limit;int beta=evaluate(b)-50;
   try{e.search(b,7,beta-1,beta,1);}catch(Halt&){interrupts++;}
   assert(e.verificationNesting==0);assert(e.path.size()==1&&e.path.back()==b.hash());
   verified+=e.nullVerifications;rejected+=e.nullRejected;cutoffs+=e.nullCutoffs;cases++;
  }
 }
 assert(verified>0&&interrupts>0);
 std::cout<<"{\"passed\":true,\"cases\":"<<cases<<",\"verification_searches\":"<<verified<<",\"rejected_shortcuts\":"<<rejected<<",\"null_cutoffs\":"<<cutoffs<<",\"node_interruptions\":"<<interrupts<<",\"verification_scope_and_history_restored\":true,\"note\":\"Mechanism and cancellation checks, not an independent endgame-solving oracle\"}\n";
}
