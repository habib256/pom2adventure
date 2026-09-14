#include "hgrpaint/HgrConvert.h"
#include "hgrpaint/HgrPaintModel.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace {
constexpr std::size_t kDhgrBytes = 16384;
constexpr std::size_t kHgrBytes = 8192;
struct Rgb { std::uint8_t r, g, b; };
/* The same 4-bit indices have two materially different display palettes.
 * The converter writes indices, not RGB values; keeping both previews is the
 * only honest way to review an asset intended for composite and Péritel. */
constexpr Rgb kPaletteComposite[16] = {
    {0x00,0x00,0x00},{0xa7,0x0b,0x40},{0x40,0x1c,0xf7},{0xe6,0x28,0xff},
    {0x00,0x74,0x40},{0x80,0x80,0x80},{0x19,0x90,0xff},{0xbf,0x9c,0xff},
    {0x40,0x63,0x00},{0xe6,0x6f,0x00},{0x80,0x80,0x80},{0xff,0x8b,0xbf},
    {0x19,0xd7,0x00},{0xbf,0xe3,0x08},{0x58,0xf4,0xbf},{0xff,0xff,0xff}
};
constexpr Rgb kPaletteChatMauve[16] = {
    {0x00,0x00,0x00},{0xac,0x12,0x4c},{0x00,0x07,0x83},{0xaa,0x1a,0xd1},
    {0x00,0x83,0x2f},{0x9f,0x97,0x7e},{0x00,0x8a,0xb5},{0x9f,0x9e,0xff},
    {0x7a,0x5f,0x00},{0xff,0x72,0x47},{0x78,0x68,0x7f},{0xff,0x7a,0xcf},
    {0x6f,0xe6,0x2c},{0xff,0xf6,0x7b},{0x6c,0xee,0xb2},{0xff,0xff,0xff}
};

bool writeFile(const std::filesystem::path& p, const std::vector<std::uint8_t>& v) {
    std::error_code ec; std::filesystem::create_directories(p.parent_path(), ec);
    std::ofstream out(p, std::ios::binary | std::ios::trunc);
    return out && static_cast<bool>(out.write(reinterpret_cast<const char*>(v.data()), v.size()));
}

bool readFile(const std::filesystem::path& p, std::vector<std::uint8_t>& v) {
    std::ifstream in(p, std::ios::binary);
    if (!in) return false;
    in.seekg(0, std::ios::end); const auto n=in.tellg(); if (n<0) return false;
    v.resize(static_cast<std::size_t>(n)); in.seekg(0, std::ios::beg);
    return v.empty() || static_cast<bool>(in.read(reinterpret_cast<char*>(v.data()), v.size()));
}

bool decode(const std::vector<std::uint8_t>& in, std::vector<std::uint8_t>& raw) {
    static const std::uint8_t hdr[8]={'D','H','R','R',1,0,0,0x40};
    if (in.size()<8 || !std::equal(hdr,hdr+8,in.begin())) return false;
    raw.clear(); raw.reserve(kDhgrBytes);
    for (std::size_t i=8; raw.size()<kDhgrBytes && i<in.size();) {
        const auto t=in[i++];
        if (t&0x80) { const std::size_t n=(t&0x7f)+3; if(i>=in.size()||n>kDhgrBytes-raw.size()) return false; raw.insert(raw.end(),n,in[i++]); }
        else { const std::size_t n=t+1; if(n>in.size()-i||n>kDhgrBytes-raw.size()) return false; raw.insert(raw.end(),in.begin()+i,in.begin()+i+n); i+=n; }
        if (raw.size()==kDhgrBytes) return i==in.size();
    }
    return false;
}

bool decodeHgr(const std::vector<std::uint8_t>& in, std::vector<std::uint8_t>& raw) {
    static const std::uint8_t hdr[8]={'H','G','R','R',1,0,0,0x20};
    if (in.size()<8 || !std::equal(hdr,hdr+8,in.begin())) return false;
    raw.clear(); raw.reserve(kHgrBytes);
    for (std::size_t i=8; raw.size()<kHgrBytes && i<in.size();) {
        const auto t=in[i++];
        if (t&0x80) { const std::size_t n=(t&0x7f)+3; if(i>=in.size()||n>kHgrBytes-raw.size()) return false; raw.insert(raw.end(),n,in[i++]); }
        else { const std::size_t n=t+1; if(n>in.size()-i||n>kHgrBytes-raw.size()) return false; raw.insert(raw.end(),in.begin()+i,in.begin()+i+n); i+=n; }
        if (raw.size()==kHgrBytes) return i==in.size();
    }
    return false;
}

std::size_t hgrOffset(int col,int y) {
    return std::size_t((y&7)<<10)+std::size_t((y&0x38)<<4)+std::size_t((y>>6)*40)+col;
}

std::vector<std::uint8_t> renderOldHgr(const std::vector<std::uint8_t>& page) {
    static constexpr Rgb banks[2][4]={
        {{0,0,0},{0xaa,0x1a,0xd1},{0x6f,0xe6,0x2c},{255,255,255}},
        {{0,0,0},{0,0x8a,0xb5},{0xff,0x72,0x47},{255,255,255}}
    };
    std::vector<std::uint8_t> rgba(280*192*4,255);
    for(int y=0;y<192;++y){std::uint8_t bits[280]{},bank[40]{};
        for(int col=0;col<40;++col){const auto b=page[hgrOffset(col,y)];bank[col]=b>>7;for(int k=0;k<7;++k)bits[col*7+k]=(b>>k)&1;}
        for(int x=0;x<280;x+=2){const auto c=banks[bank[x/7]][bits[x]|(bits[x+1]<<1)];for(int q=0;q<2;++q){auto o=(y*280+x+q)*4;rgba[o]=c.r;rgba[o+1]=c.g;rgba[o+2]=c.b;}}
    }
    return rgba;
}

std::vector<std::uint8_t> encode(const std::vector<std::uint8_t>& raw) {
    std::vector<std::uint8_t> out{'D','H','R','R',1,0,0,0x40};
    for (std::size_t i = 0; i < raw.size();) {
        std::size_t run = 1;
        while (i + run < raw.size() && raw[i + run] == raw[i] && run < 130) ++run;
        if (run >= 3) { out.push_back(std::uint8_t(0x80 + run - 3)); out.push_back(raw[i]); i += run; continue; }
        const auto begin = i; i += run;
        while (i < raw.size() && i - begin < 128) {
            run = 1; while (i + run < raw.size() && raw[i + run] == raw[i] && run < 130) ++run;
            if (run >= 3) break; i += std::min(run, 128 - (i - begin));
        }
        out.push_back(std::uint8_t(i - begin - 1));
        out.insert(out.end(), raw.begin() + begin, raw.begin() + i);
    }
    return out;
}

std::vector<std::uint8_t> preview(const std::vector<std::uint8_t>& pair,
                                  const Rgb (&palette)[16]) {
    constexpr int w = 280, h = 192;
    std::vector<std::uint8_t> rgb(w * h * 3);
    for (int y = 0; y < h; ++y) for (int x = 0; x < 140; ++x) {
        const auto c = palette[hgrpaint::dhgrColorAt(pair.data(), x, y) & 15];
        for (int q = 0; q < 2; ++q) { const auto o = (y * w + x * 2 + q) * 3; rgb[o]=c.r; rgb[o+1]=c.g; rgb[o+2]=c.b; }
    }
    return rgb;
}
}

// Stable machine interface for the local workshop. Options are validated by
// its recipe reader; the legacy convert command deliberately keeps its defaults.
int importImage(int argc, char** argv) {
    if (argc != 8) return 2;
    hgrpaint::ImportOptions opt;
    int model = 1;
    std::ifstream settings(argv[4]);
    std::string key; double value;
    if (!settings) return 2;
    while (settings >> key >> value) {
        if (key == "brightness") opt.brightness=value;
        else if (key == "contrast") opt.contrast=value;
        else if (key == "gamma") opt.gamma=value;
        else if (key == "colourNoise") opt.chromaWeight=6.0-value*5.2;
        else if (key == "diffusion") opt.diffusion=value;
        else if (key == "dither") opt.dither=value!=0;
        else if (key == "stretch") opt.stretch=value!=0;
        else if (key == "kernel") opt.kernel=value ? hgrpaint::DitherKernel::JarvisMod : hgrpaint::DitherKernel::FloydSteinberg;
        else if (key == "model") model=value;
        else if (key == "cropX0") opt.cropX0=value;
        else if (key == "cropY0") opt.cropY0=value;
        else if (key == "cropX1") opt.cropX1=value;
        else if (key == "cropY1") opt.cropY1=value;
        else return 2;
    }
    if (!settings.eof() || model<0 || model>3) return 2;
    const bool hgr=std::string(argv[3])=="hgr";
    if (!hgr && std::string(argv[3])!="dhgr") return 2;
    int w,h,n; auto* rgba=stbi_load(argv[2],&w,&h,&n,4);
    if (!rgba) return 1;
    // The block quantiser's fit uses square 140px cells. In DHGR those
    // cells are twice as wide: letterbox the source in visual 280:192 space
    // before its exact resampling/quantisation, otherwise fit squashes it.
    std::vector<uint8_t> padded;
    auto* input=rgba;
    if (!hgr && model==1 && !opt.stretch) {
        const bool crop=opt.cropX1>opt.cropX0 && opt.cropY1>opt.cropY0;
        const int x0=crop?std::clamp(opt.cropX0,0,w-1):0;
        const int y0=crop?std::clamp(opt.cropY0,0,h-1):0;
        const int cw=(crop?std::clamp(opt.cropX1,x0+1,w):w)-x0;
        const int ch=(crop?std::clamp(opt.cropY1,y0+1,h):h)-y0;
        const int pw=std::max(cw,(ch*35+23)/24), ph=std::max(ch,(cw*24+34)/35);
        padded.assign(static_cast<size_t>(pw)*ph*4,0);
        for(int yy=0;yy<ch;yy++)
            std::copy_n(rgba+((y0+yy)*w+x0)*4,cw*4,
                        padded.data()+(((ph-ch)/2+yy)*pw+(pw-cw)/2)*4);
        w=pw;h=ph;input=padded.data();opt.stretch=true;
        opt.cropX0=opt.cropY0=opt.cropX1=opt.cropY1=0;
    }
    std::vector<uint8_t> raw(hgr?kHgrBytes:kDhgrBytes);
    if (hgr) hgrpaint::imageToHgrPage(input,w,h,opt,raw.data());
    else if (model==0) hgrpaint::imageToDhgrPage560(input,w,h,opt,raw.data());
    else if (model==2) hgrpaint::imageToDhgrMonoPage(input,w,h,opt,raw.data());
    else if (model==3) hgrpaint::imageToDhgrPage560Ntsc(input,w,h,opt,raw.data());
    else hgrpaint::imageToDhgrPage(input,w,h,opt,raw.data());
    stbi_image_free(rgba);
    if (!writeFile(argv[5],hgr?raw:encode(raw))) return 1;
    // Full dot resolution, decoded by POM2's own ColorNTSC scanline path.
    const int pw=hgr?280:560;
    std::vector<uint32_t> pixels(pw*192);
    for (int y=0;y<192;y++) {
        auto* row=pixels.data()+y*pw;
        const auto base=hgrOffset(0,y);
        if (hgr) hgrpaint::hgrDecodeScanlineRgb(raw.data()+base,row);
        else if (model==2) {
            for (int x=0;x<560;x++) {
                const auto byte=raw[base+((x/7)&1)*8192+(x/14)];
                row[x]=(byte&(1<<(x%7)))?0xffffffff:0xff000000;
            }
        } else hgrpaint::dhgrDecodeScanlineRgb(raw.data()+base,raw.data()+8192+base,row);
    }
    if (!stbi_write_png(argv[6],pw,192,4,pixels.data(),pw*4)) return 1;
    if (!hgr) {
        const auto rgb=preview(raw,kPaletteChatMauve);
        if (!stbi_write_png(argv[7],280,192,3,rgb.data(),280*3)) return 1;
    } else if (!stbi_write_png(argv[7],pw,192,4,pixels.data(),pw*4)) return 1;
    return 0;
}

int main(int argc, char** argv) {
    if (argc>1 && std::string(argv[1])=="import") return importImage(argc,argv);
    if (argc>=3 && std::string(argv[1])=="validate") {
        std::vector<std::uint8_t> packed,raw;
        if(!readFile(argv[2],packed)||!decode(packed,raw)){std::cerr<<"invalid DHRR v1 stream\n";return 1;}
        std::cout<<argv[2]<<": valid DHRR v1, 16384 bytes decoded\n"; return 0;
    }
    if (argc==4 && std::string(argv[1])=="migrate-hgr") {
        std::vector<std::uint8_t> packed,hgr;
        if(!readFile(argv[2],packed)||!decodeHgr(packed,hgr)){std::cerr<<"invalid HGRR v1 stream\n";return 1;}
        const auto rgba=renderOldHgr(hgr); std::vector<std::uint8_t> pair(kDhgrBytes);
        hgrpaint::ImportOptions opt; opt.stretch=true; opt.dither=false;
        hgrpaint::imageToDhgrPage(rgba.data(),280,192,opt,pair.data());
        if(!writeFile(argv[3],encode(pair))) return 1;
        return 0;
    }
    if (argc < 4 || std::string(argv[1]) != "convert") {
        std::cerr << "usage:\n  scoswamp_dhgr convert INPUT.png OUTPUT.DHGR.RLE.BIN [COMPOSITE_PREVIEW.png [CHAT_MAUVE_PREVIEW.png]]\n  scoswamp_dhgr migrate-hgr INPUT.HGR.RLE.BIN OUTPUT.DHGR.RLE.BIN\n  scoswamp_dhgr validate INPUT.DHGR.RLE.BIN\n"; return 2;
    }
    int w=0,h=0,n=0; auto* rgba = stbi_load(argv[2], &w, &h, &n, 4);
    if (!rgba) { std::cerr << "cannot decode " << argv[2] << "\n"; return 1; }
    std::vector<std::uint8_t> pair(kDhgrBytes);
    hgrpaint::ImportOptions opt; opt.stretch=true; opt.dither=false; opt.chromaWeight=2.4f;
    hgrpaint::imageToDhgrPage(rgba, w, h, opt, pair.data()); stbi_image_free(rgba);
    const auto packed = encode(pair);
    if (!writeFile(argv[3], packed)) { std::cerr << "cannot write output\n"; return 1; }
    if (argc >= 5) { const auto rgb=preview(pair,kPaletteComposite); if (!stbi_write_png(argv[4],280,192,3,rgb.data(),280*3)) return 1; }
    if (argc >= 6) { const auto rgb=preview(pair,kPaletteChatMauve); if (!stbi_write_png(argv[5],280,192,3,rgb.data(),280*3)) return 1; }
    std::cout << argv[3] << ": " << packed.size() << " bytes (DHGR 140x192, 16 colours)\n";
    return 0;
}
