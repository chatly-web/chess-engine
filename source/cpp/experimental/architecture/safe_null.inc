  if(!q&&depth>=3&&ply&&!check&&allowNull&&!verificationNesting&&beta-alpha==1&&abs(beta)<28000){
   int ownPieces=0,materialPhase=0;
   for(int piece:b.b){int type=abs(piece);if(type>=2&&type<=5){materialPhase+=type<=3?1:type==4?2:4;if(sign(piece)==b.side)ownPieces++;}}
   if(ownPieces&&evaluate(b)>=beta){
    nullAttempts++;Board n=b;n.side=-n.side;n.ep=-1;path.push_back(n.hash());int value;
    try{value=-search(n,depth-3,-beta,-beta+1,ply+1,0,false,false);}catch(...){path.pop_back();throw;}path.pop_back();
    if(value>=beta&&abs(value)<28000){
     bool endgame=materialPhase<=8||ownPieces<=1;
     if(endgame){
      nullVerifications++;int verified;
      struct Guard{int&n;Guard(int&value):n(value){n++;}~Guard(){n--;}};
      {Guard guard(verificationNesting);verified=search(b,depth-1,beta-1,beta,ply,0,false,priorUnique);}
      if(verified>=beta){nullCutoffs++;quietSpan[ply]=120;return verified;}
      nullRejected++;quietSpan[ply]=0;b.legalInto(buf.pseudo,buf.legal,false);
     }else{nullCutoffs++;quietSpan[ply]=120;return value;}
    }
   }
  }
