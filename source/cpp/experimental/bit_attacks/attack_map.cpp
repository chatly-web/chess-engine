#define main embedded_engine_entry
#include "build-candidate/engine.cpp"
#undef main
int main(){initializeAttackMasks();string text;while(getline(cin,text)){try{Board b=fen(text);for(int c:{-1,1}){uint64_t mask=0;for(int sq=0;sq<64;sq++)if(b.attacked(sq,c))mask|=uint64_t(1)<<sq;cout<<mask<<" ";}cout<<endl;}catch(exception&e){cerr<<e.what()<<endl;return 1;}}}
