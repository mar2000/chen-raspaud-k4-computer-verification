#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

struct Bits {
    uint64_t lo=0, hi=0;
    friend bool operator==(Bits a, Bits b){ return a.lo==b.lo && a.hi==b.hi; }
};
struct BitsLess {
    bool operator()(Bits a, Bits b) const {
        return a.hi < b.hi || (a.hi==b.hi && a.lo < b.lo);
    }
};
static Bits bor(Bits a, Bits b){ return {a.lo|b.lo,a.hi|b.hi}; }
static Bits band(Bits a, Bits b){ return {a.lo&b.lo,a.hi&b.hi}; }
static bool empty(Bits a){ return a.lo==0 && a.hi==0; }

struct K94 {
    std::vector<int> mask;
    std::vector<Bits> neigh;
    std::vector<std::vector<Bits>> reach;
    K94(int maxLen=14){
        for(int m=0;m<(1<<9);++m) if(std::popcount((unsigned)m)==4) mask.push_back(m);
        if(mask.size()!=126) throw std::runtime_error("bad color count");
        neigh.resize(126);
        for(int i=0;i<126;++i){
            Bits b{};
            for(int j=0;j<126;++j) if((mask[i]&mask[j])==0){
                if(j<64) b.lo|=1ULL<<j; else b.hi|=1ULL<<(j-64);
            }
            neigh[i]=b;
        }
        reach.assign(maxLen+1,std::vector<Bits>(126));
        for(int i=0;i<126;++i){
            if(i<64) reach[0][i].lo=1ULL<<i; else reach[0][i].hi=1ULL<<(i-64);
        }
        for(int l=1;l<=maxLen;++l){
            for(int i=0;i<126;++i){
                Bits out{}, cur=reach[l-1][i];
                uint64_t x=cur.lo;
                while(x){ int j=std::countr_zero(x); x&=x-1; out=bor(out,neigh[j]); }
                x=cur.hi;
                while(x){ int j=std::countr_zero(x)+64; x&=x-1; out=bor(out,neigh[j]); }
                reach[l][i]=out;
            }
        }
    }
};
static K94 K;

static std::vector<Bits> unique_center_sets(int a,int b){
    std::set<Bits,BitsLess> uniq;
    for(int x=0;x<126;++x) for(int y=0;y<126;++y){
        Bits u=band(K.reach[a][x],K.reach[b][y]);
        if(!empty(u)) uniq.insert(u);
    }
    return {uniq.begin(),uniq.end()};
}

static Bits reachable4_from_set(Bits u){
    Bits out{};
    uint64_t x=u.lo;
    while(x){ int s=std::countr_zero(x); x&=x-1; out=bor(out,K.reach[4][s]); }
    x=u.hi;
    while(x){ int s=std::countr_zero(x)+64; x&=x-1; out=bor(out,K.reach[4][s]); }
    return out;
}

int main(){
    auto left=unique_center_sets(3,3);
    std::vector<Bits> leftReach;
    for(auto u:left) leftReach.push_back(reachable4_from_set(u));
    std::cout << "unique realizable U_{3,3} sets: " << left.size() << "\n";

    std::vector<std::pair<int,int>> bad;
    for(int a=1;a<=7;++a) for(int b=a;b<=7;++b){
        auto right=unique_center_sets(a,b);
        bool incompatible=false;
        for(auto R:leftReach){
            for(auto U:right){
                if(empty(band(R,U))){ incompatible=true; break; }
            }
            if(incompatible) break;
        }
        if(incompatible) bad.push_back({a,b});
        std::cout << "("<<a<<","<<b<<"): unique U="<<right.size()
                  << ", incompatible="<<(incompatible?"yes":"no") << "\n";
    }
    std::vector<std::pair<int,int>> expected={{1,1},{1,2},{1,3}};
    bool ok=(bad==expected);
    std::cout << "bad pairs:";
    for(auto [a,b]:bad) std::cout << " ("<<a<<","<<b<<")";
    std::cout << "\n" << (ok?"ALL EXACT C++ 334 SUPPORT CHECKS PASSED":"FAILURE") << "\n";
    return ok?0:1;
}
