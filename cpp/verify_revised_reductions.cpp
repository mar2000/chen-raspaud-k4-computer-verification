#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <tuple>
#include <unordered_set>
#include <utility>
#include <vector>

struct Bits {
    uint64_t lo = 0, hi = 0;
    friend bool operator==(const Bits& a, const Bits& b){ return a.lo==b.lo && a.hi==b.hi; }
};

static inline Bits bor(Bits a, Bits b){ return {a.lo|b.lo, a.hi|b.hi}; }
static inline Bits band(Bits a, Bits b){ return {a.lo&b.lo, a.hi&b.hi}; }
static inline Bits bdiff(Bits a, Bits b){ return {a.lo & ~b.lo, a.hi & ~b.hi}; }
static inline bool subset(Bits a, Bits b){ return ((a.lo & ~b.lo)==0) && ((a.hi & ~b.hi)==0); }
static inline int popc(Bits a){ return std::popcount(a.lo)+std::popcount(a.hi); }

struct BitsLess {
    bool operator()(const Bits& a, const Bits& b) const {
        return a.hi < b.hi || (a.hi==b.hi && a.lo < b.lo);
    }
};

struct State {
    int k;
    Bits u;
    friend bool operator==(State const&a, State const&b){return a.k==b.k && a.u==b.u;}
};
struct StateHash {
    size_t operator()(State const&s) const noexcept {
        uint64_t h=s.u.lo ^ (s.u.hi + 0x9e3779b97f4a7c15ULL + (s.u.lo<<6) + (s.u.lo>>2));
        h ^= uint64_t(s.k)*0x517cc1b727220a95ULL;
        return size_t(h ^ (h>>32));
    }
};

struct K94 {
    std::vector<int> colorMasks;
    std::vector<Bits> neigh;
    std::vector<std::vector<Bits>> reach; // reach[len][color]
    Bits all;

    K94(int maxLen=14){
        for(int m=0;m<(1<<9);++m) if(std::popcount((unsigned)m)==4) colorMasks.push_back(m);
        if(colorMasks.size()!=126) throw std::runtime_error("bad color count");
        all.lo=~0ULL;
        all.hi=(1ULL<<(126-64))-1;
        neigh.resize(126);
        for(int i=0;i<126;++i){
            Bits b{};
            for(int j=0;j<126;++j) if((colorMasks[i]&colorMasks[j])==0){
                if(j<64) b.lo |= 1ULL<<j; else b.hi |= 1ULL<<(j-64);
            }
            neigh[i]=b;
        }
        reach.assign(maxLen+1,std::vector<Bits>(126));
        for(int i=0;i<126;++i){
            if(i<64) reach[0][i].lo=1ULL<<i; else reach[0][i].hi=1ULL<<(i-64);
        }
        for(int l=1;l<=maxLen;++l){
            for(int i=0;i<126;++i){
                Bits cur=reach[l-1][i], out{};
                uint64_t x=cur.lo;
                while(x){ int j=std::countr_zero(x); x&=x-1; out=bor(out,neigh[j]); }
                x=cur.hi;
                while(x){ int j=std::countr_zero(x); x&=x-1; out=bor(out,neigh[j+64]); }
                reach[l][i]=out;
            }
        }
    }
};

static K94 K;
static int fsize[8];

std::vector<Bits> maximal_masks(std::set<Bits,BitsLess> const& uniq){
    std::vector<Bits> v(uniq.begin(),uniq.end());
    std::sort(v.begin(),v.end(),[](Bits a,Bits b){return popc(a)>popc(b);});
    std::vector<Bits> out;
    for(auto m:v){
        bool dom=false;
        for(auto n:out) if(subset(m,n)){dom=true;break;}
        if(!dom) out.push_back(m);
    }
    return out;
}

static std::vector<Bits> unions_of(const std::vector<std::vector<Bits>>& branches, int lo, int hi){
    std::vector<Bits> states(1);
    for(int k=lo;k<hi;++k){
        std::vector<Bits> next;
        next.reserve(states.size()*branches[k].size());
        for(auto u:states) for(auto m:branches[k]) next.push_back(bor(u,m));
        std::sort(next.begin(),next.end(),BitsLess{});
        next.erase(std::unique(next.begin(),next.end(),[](Bits a,Bits b){return a==b;}),next.end());
        states.swap(next);
    }
    std::sort(states.begin(),states.end(),[](Bits a,Bits b){return popc(a)>popc(b);});
    return states;
}

static bool has_cover_mitm(Bits full, const std::vector<std::vector<Bits>>& branches){
    int n=(int)branches.size();
    if(n==0) return full==Bits{};
    int mid=n/2;
    auto L=unions_of(branches,0,mid);
    auto R=unions_of(branches,mid,n);
    int needCount=popc(full);
    for(auto u:L){
        Bits need=bdiff(full,u);
        int pcNeed=popc(need);
        if(pcNeed==0) return true;
        for(auto v:R){
            if(popc(v)<pcNeed) break;
            if(subset(need,v)) return true;
        }
    }
    return false;
}

bool union_bound_reducible(std::vector<int> const&t){
    int s=0; for(int a:t) s+=fsize[a]; return s<126;
}

bool rooted_star_reducible(std::vector<int> const&t){
    int ar=t[0], rootColor=0;
    Bits C=K.reach[ar][rootColor];
    std::vector<std::vector<Bits>> branches;
    int coarse=0;
    for(int i=1;i<(int)t.size();++i){
        int ai=t[i];
        Bits allowed=K.reach[ar+ai][rootColor];
        std::set<Bits,BitsLess> uniq;
        int maxforb=0;
        uint64_t x=allowed.lo;
        while(x){
            int y=std::countr_zero(x); x&=x-1;
            Bits m=band(C,bdiff(K.all,K.reach[ai][y]));
            uniq.insert(m); maxforb=std::max(maxforb,popc(m));
        }
        x=allowed.hi;
        while(x){
            int y=std::countr_zero(x)+64; x&=x-1;
            Bits m=band(C,bdiff(K.all,K.reach[ai][y]));
            uniq.insert(m); maxforb=std::max(maxforb,popc(m));
        }
        coarse += maxforb;
        branches.push_back(maximal_masks(uniq));
    }
    if(coarse < popc(C)) return true;
    // In all calls that survive the coarse bound in this verifier there are
    // at most four non-root branches.  Meet-in-the-middle is then exhaustive.
    if(branches.size()>4) throw std::runtime_error("unexpected hard rooted-star instance");
    return !has_cover_mitm(C,branches);
}

int excess(std::vector<int> const&t){return std::accumulate(t.begin(),t.end(),0)-9*(int)t.size()+18;}

void gen_types_rec(int d,int pos,int last,std::vector<int>&cur,std::vector<std::vector<int>>&out){
    if(pos==d){out.push_back(cur);return;}
    for(int a=last;a<=7;++a){cur.push_back(a);gen_types_rec(d,pos+1,a,cur,out);cur.pop_back();}
}
std::vector<std::vector<int>> gen_types(int d){std::vector<std::vector<int>> out; std::vector<int> cur; gen_types_rec(d,0,1,cur,out); return out;}

void print_type(std::vector<int> const&t){std::cout<<"(";for(size_t i=0;i<t.size();++i){if(i)std::cout<<",";std::cout<<t[i];}std::cout<<")";}

int main(){
    for(int a=1;a<=7;++a) fsize[a]=126-popc(K.reach[a][0]);
    bool ok=true;
    const std::array<int,7> expectedF={121,105,81,45,21,5,1};
    std::cout<<"=== exact C++ admissible-set audit ===\n";
    std::cout<<"F sizes:";
    for(int a=1;a<=7;++a){ std::cout<<" "<<fsize[a]; if(fsize[a]!=expectedF[a-1]) ok=false; }
    std::cout<<"\n";
    if(popc(K.reach[8][0])!=126 || popc(K.reach[9][0])!=126) ok=false;
    std::cout<<"A8 size="<<popc(K.reach[8][0])<<", A9 size="<<popc(K.reach[9][0])<<"\n\n";
    std::cout<<"=== exact C++ positive-type audit ===\n";
    for(int d=3;d<=8;++d){
        int npos=0,nub=0,nstar=0; std::vector<std::vector<int>> survivors;
        for(auto const&t:gen_types(d)){
            if(excess(t)<=0) continue; ++npos;
            if(union_bound_reducible(t)){++nub;continue;}
            ++nstar;
            if(!rooted_star_reducible(t)) survivors.push_back(t);
        }
        std::cout<<"degree "<<d<<": positive="<<npos<<", union="<<nub<<", star="<<nstar<<", survivors=";
        if(survivors.empty()) std::cout<<"[]"; else {std::cout<<"["; for(auto&t:survivors){print_type(t);std::cout<<" ";}std::cout<<"]";}
        std::cout<<"\n";
        if(d==3){if(!(survivors.size()==1 && survivors[0]==std::vector<int>({3,3,4}))) ok=false;}
        else if(!survivors.empty()) ok=false;
    }

    std::cout<<"\n=== exact C++ capacity audit ===\n";
    for(int d=4;d<=7;++d){
        int nex=0; std::vector<std::vector<int>> survivors;
        for(auto const&t:gen_types(d)){
            int e=excess(t); if(e>0) continue;
            int q=std::count(t.begin(),t.end(),4);
            if(q<=-e) continue;
            ++nex;
            if(!rooted_star_reducible(t)) survivors.push_back(t);
        }
        std::cout<<"degree "<<d<<": exceptions="<<nex<<", survivors=";
        if(survivors.empty()) std::cout<<"[]"; else {std::cout<<"["; for(auto&t:survivors){print_type(t);std::cout<<" ";}std::cout<<"]";}
        std::cout<<"\n";
        if(!survivors.empty()) ok=false;
    }
    std::cout<<"\n"<<(ok?"ALL EXACT C++ STAR CHECKS PASSED":"FAILURE")<<"\n";
    return ok?0:1;
}
