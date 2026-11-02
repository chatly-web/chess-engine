#define main clash_original_main
#include "engine.cpp"
#undef main
int main(){uint64_t seed=191827;for(auto&row:zob)for(auto&v:row)v=random64(seed);for(auto&v:castlekeys)v=random64(seed);for(auto&v:epkeys)v=random64(seed);turnkey=random64(seed);string text;while(getline(cin,text)){Board b=fen(text);Engine e;e.path={b.hash()};e.deadline=Clock::now()+chrono::seconds(5);cout<<evaluate(b)<<" "<<e.search(b,0,-32000,32000)<<endl;}}
