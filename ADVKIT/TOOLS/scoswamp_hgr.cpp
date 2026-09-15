#include "Cam16.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace {

constexpr int kWidth = 280;
constexpr int kHeight = 192;
constexpr std::size_t kHgrBytes = 8192;

struct Rgb { std::uint8_t r, g, b; };

// Exact POM2 Le Chat Mauve / AppleWin Feline palette. This is also the ink
// palette the reference planches are authored in (the generation prompts name
// these very hex values), so source pixels are snapped against THIS table.
constexpr Rgb kPaletteFeline[2][4] = {
    {{0x00,0x00,0x00}, {0xaa,0x1a,0xd1}, {0x6f,0xe6,0x2c}, {0xff,0xff,0xff}},
    {{0x00,0x00,0x00}, {0x00,0x8a,0xb5}, {0xff,0x72,0x47}, {0xff,0xff,0xff}},
};

// Steady-state colours of the six HGR inks under POM2's OpenEmulator
// composite demod (Apple2Display::renderCompositeOeCpu FIR kernels, NTSC,
// sharpness 0.5, hue 0), averaged over the four subcarrier phases. The
// display target is the OpenEmulator pipeline, so bank substitution costs
// and the preview use these values by default (--palette feline reverts).
constexpr Rgb kPaletteOE[2][4] = {
    {{0x00,0x00,0x00}, {0xff,0x03,0xff}, {0x00,0xfc,0x00}, {0xff,0xff,0xff}},
    {{0x00,0x00,0x00}, {0x00,0x97,0xff}, {0xff,0x68,0x00}, {0xff,0xff,0xff}},
};

std::size_t hgrOffset(int x, int y)
{
    return static_cast<std::size_t>((y & 7) << 10)
         + static_cast<std::size_t>((y & 0x38) << 4)
         + static_cast<std::size_t>((y >> 6) * 40)
         + static_cast<std::size_t>(x / 7);
}

bool readFile(const std::filesystem::path& path, std::vector<std::uint8_t>& out)
{
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;
    in.seekg(0, std::ios::end);
    const auto end = in.tellg();
    if (end < 0) return false;
    out.resize(static_cast<std::size_t>(end));
    in.seekg(0, std::ios::beg);
    return out.empty() || static_cast<bool>(in.read(
        reinterpret_cast<char*>(out.data()), static_cast<std::streamsize>(out.size())));
}

bool writeFile(const std::filesystem::path& path, const std::vector<std::uint8_t>& data)
{
    std::error_code ec;
    std::filesystem::create_directories(path.parent_path(), ec);
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) return false;
    out.write(reinterpret_cast<const char*>(data.data()),
              static_cast<std::streamsize>(data.size()));
    return static_cast<bool>(out);
}

std::vector<std::uint8_t> encodeRle(const std::vector<std::uint8_t>& raw)
{
    std::vector<std::uint8_t> out{'H','G','R','R',1,0,0,0x20};
    std::size_t i = 0;
    while (i < raw.size()) {
        std::size_t run = 1;
        while (i + run < raw.size() && raw[i + run] == raw[i] && run < 130) ++run;
        if (run >= 3) {
            out.push_back(static_cast<std::uint8_t>(0x80u + run - 3));
            out.push_back(raw[i]);
            i += run;
            continue;
        }
        const std::size_t begin = i;
        i += run;
        while (i < raw.size() && i - begin < 128) {
            run = 1;
            while (i + run < raw.size() && raw[i + run] == raw[i] && run < 130) ++run;
            if (run >= 3) break;
            i += run;
        }
        out.push_back(static_cast<std::uint8_t>(i - begin - 1));
        out.insert(out.end(), raw.begin() + static_cast<std::ptrdiff_t>(begin),
                   raw.begin() + static_cast<std::ptrdiff_t>(i));
    }
    return out;
}

bool decodeRle(const std::vector<std::uint8_t>& in, std::vector<std::uint8_t>& raw,
               std::string& error)
{
    if (in.size() < 8 || !std::equal(in.begin(), in.begin() + 4, "HGRR") ||
        in[4] != 1 || in[5] != 0 || in[6] != 0 || in[7] != 0x20) {
        error = "invalid HGRR v1 header";
        return false;
    }
    raw.clear(); raw.reserve(kHgrBytes);
    std::size_t i = 8;
    while (raw.size() < kHgrBytes && i < in.size()) {
        const std::uint8_t token = in[i++];
        if (token & 0x80u) {
            const std::size_t count = (token & 0x7fu) + 3u;
            if (i >= in.size() || count > kHgrBytes - raw.size()) {
                error = "truncated or overflowing repeat run";
                return false;
            }
            raw.insert(raw.end(), count, in[i++]);
        } else {
            const std::size_t count = token + 1u;
            if (count > in.size() - i || count > kHgrBytes - raw.size()) {
                error = "truncated or overflowing literal run";
                return false;
            }
            raw.insert(raw.end(), in.begin() + static_cast<std::ptrdiff_t>(i),
                       in.begin() + static_cast<std::ptrdiff_t>(i + count));
            i += count;
        }
    }
    if (raw.size() != kHgrBytes || i != in.size()) {
        error = raw.size() != kHgrBytes ? "decoded size is not 8192" : "trailing data";
        return false;
    }
    return true;
}

std::vector<std::uint8_t> resampleCover(const std::uint8_t* src, int sw, int sh)
{
    std::vector<std::uint8_t> out(kWidth * kHeight * 3);
    const double scale = std::max(double(kWidth) / sw, double(kHeight) / sh);
    const double cropW = kWidth / scale, cropH = kHeight / scale;
    const double x0 = (sw - cropW) * 0.5, y0 = (sh - cropH) * 0.5;
    for (int y = 0; y < kHeight; ++y) {
        const double sy = y0 + (y + 0.5) / scale - 0.5;
        const int iy0 = std::clamp(static_cast<int>(sy), 0, sh - 1);
        const int iy1 = std::min(iy0 + 1, sh - 1);
        const double fy = std::clamp(sy - iy0, 0.0, 1.0);
        for (int x = 0; x < kWidth; ++x) {
            const double sx = x0 + (x + 0.5) / scale - 0.5;
            const int ix0 = std::clamp(static_cast<int>(sx), 0, sw - 1);
            const int ix1 = std::min(ix0 + 1, sw - 1);
            const double fx = std::clamp(sx - ix0, 0.0, 1.0);
            for (int c = 0; c < 3; ++c) {
                const double a = src[(iy0 * sw + ix0) * 4 + c] * (1.0 - fx)
                               + src[(iy0 * sw + ix1) * 4 + c] * fx;
                const double b = src[(iy1 * sw + ix0) * 4 + c] * (1.0 - fx)
                               + src[(iy1 * sw + ix1) * 4 + c] * fx;
                out[(y * kWidth + x) * 3 + c] = static_cast<std::uint8_t>(
                    std::clamp(a * (1.0 - fy) + b * fy, 0.0, 255.0) + 0.5);
            }
        }
    }
    return out;
}

// Matching ii-pix practice: gamma 0.75 before palette matching gives better
// HGR conversions than matching the sRGB values directly (and this converter
// never dithers -- nearest-colour only -- which is the other half of that
// recipe). 1.0 disables the correction.
constexpr double kDefaultGamma = 0.75;

// The six inks, as (bank, code): black and white exist in both banks.
constexpr int kInks = 6;
constexpr std::uint8_t kInkBank[kInks] = {0, 0, 0, 0, 1, 1};
constexpr std::uint8_t kInkCode[kInks] = {0, 3, 1, 2, 1, 2};

// DP penalties, in squared CAM16-UCS units (hue-to-hue distances are a few
// hundred to a few thousand). They only decide WHERE a forced bank flip
// lands and break black/white ties toward coherence; a genuinely wrong
// colour always costs more than all three combined.
constexpr float kBankChangePenalty = 150.0f;
constexpr float kStraddlePenalty   = 300.0f;  // a pair split across the flip
constexpr float kVerticalPenalty   = 50.0f;   // disagree with the row above

// What a conversion cost: subDE = mean/max CAM16 error the bank sacrifices
// actually incurred, dissent = share of source votes overruled by the pair
// majority (detail lost in the downscale). score mixes both for ranking.
struct ConvertReport { float meanSubDe = 0, maxSubDe = 0, dissentPct = 0; };

std::vector<std::uint8_t> imageToHgr(const std::uint8_t* rgba, int sw, int sh,
                                     double gamma, const Rgb (&target)[2][4],
                                     ConvertReport* report)
{
    // Gamma LUT, applied identically to pixels and to the ink palette so
    // exact planche colours still snap exactly; only blended edge pixels
    // feel the correction.
    std::array<std::uint8_t, 256> lut{};
    for (int v = 0; v < 256; ++v)
        lut[v] = static_cast<std::uint8_t>(
            std::clamp(255.0 * std::pow(v / 255.0, gamma), 0.0, 255.0) + 0.5);

    std::array<hgrpaint::Cam16Ucs, kInks> inkCam{};
    for (int ink = 0; ink < kInks; ++ink) {
        const auto c = kPaletteFeline[kInkBank[ink]][kInkCode[ink]];
        inkCam[ink] = hgrpaint::srgb8ToCam16Ucs(lut[c.r], lut[c.g], lut[c.b]);
    }
    const auto snapInk = [&](std::uint8_t r, std::uint8_t g, std::uint8_t b) {
        const auto want = hgrpaint::srgb8ToCam16Ucs(lut[r], lut[g], lut[b]);
        float best = std::numeric_limits<float>::max();
        int bestInk = 0;
        for (int ink = 0; ink < kInks; ++ink) {
            const float dJ = inkCam[ink].J - want.J, da = inkCam[ink].a - want.a,
                        db = inkCam[ink].b - want.b;
            const float cost = dJ*dJ + da*da + db*db;
            if (cost < best) { best = cost; bestInk = ink; }
        }
        return bestInk;
    };

    // Substitution table against the DISPLAY palette: cost of showing ink i
    // through bank b, and the code that does it best. Black/white cost 0 in
    // both banks; a hue is free in its home bank, expensive in the other.
    std::array<hgrpaint::Cam16Ucs, 8> targetCam{};
    for (int bank = 0; bank < 2; ++bank)
        for (int code = 0; code < 4; ++code) {
            const auto c = target[bank][code];
            targetCam[bank * 4 + code] = hgrpaint::srgb8ToCam16Ucs(c.r, c.g, c.b);
        }
    float inkCost[kInks][2];
    std::uint8_t inkBestCode[kInks][2];
    for (int ink = 0; ink < kInks; ++ink) {
        const auto want = targetCam[kInkBank[ink] * 4 + kInkCode[ink]];
        for (int bank = 0; bank < 2; ++bank) {
            float best = std::numeric_limits<float>::max();
            int bestCode = 0;
            for (int code = 0; code < 4; ++code) {
                const auto& got = targetCam[bank * 4 + code];
                const float dJ = got.J - want.J, da = got.a - want.a, db = got.b - want.b;
                const float cost = dJ*dJ + da*da + db*db;
                if (cost < best) { best = cost; bestCode = code; }
            }
            inkCost[ink][bank] = best;
            inkBestCode[ink][bank] = static_cast<std::uint8_t>(bestCode);
        }
    }

    // Palette-aware downscale: every source pixel votes for the ink of the
    // colour pair (140x192) it lands on; the majority wins. Bilinear
    // averaging here manufactured in-between colours at each stroke edge,
    // which then matched to arbitrary hues -- the blue/violet halo around
    // black trunks. A seed vote from the bilinear resample guarantees every
    // pair is covered even for sources smaller than 280x192.
    constexpr int kPairs = kWidth / 2;
    std::vector<std::uint32_t> votes(
        static_cast<std::size_t>(kHeight) * kPairs * kInks, 0);
    const auto voteAt = [&](int py, int pp) -> std::uint32_t* {
        return votes.data() + (static_cast<std::size_t>(py) * kPairs + pp) * kInks;
    };
    const auto seed = resampleCover(rgba, sw, sh);
    for (int y = 0; y < kHeight; ++y)
        for (int x = 0; x < kWidth; ++x) {
            const int i = (y * kWidth + x) * 3;
            ++voteAt(y, x / 2)[snapInk(seed[i], seed[i+1], seed[i+2])];
        }
    const double scale = std::max(double(kWidth) / sw, double(kHeight) / sh);
    const double x0 = (sw - kWidth / scale) * 0.5, y0 = (sh - kHeight / scale) * 0.5;
    for (int sy = 0; sy < sh; ++sy) {
        const int ty = static_cast<int>(std::lround((sy + 0.5 - y0) * scale - 0.5));
        if (ty < 0 || ty >= kHeight) continue;
        for (int sx = 0; sx < sw; ++sx) {
            const int tx = static_cast<int>(std::lround((sx + 0.5 - x0) * scale - 0.5));
            if (tx < 0 || tx >= kWidth) continue;
            const std::uint8_t* p = rgba + (static_cast<std::size_t>(sy) * sw + sx) * 4;
            ++voteAt(ty, tx / 2)[snapInk(p[0], p[1], p[2])];
        }
    }

    // Ink of every colour pair, image-wide, so the bank map can be settled
    // globally rather than row by row.
    std::vector<std::uint8_t> inks(static_cast<std::size_t>(kHeight) * kPairs);
    for (int y = 0; y < kHeight; ++y)
        for (int pp = 0; pp < kPairs; ++pp) {
            const auto* v = voteAt(y, pp);
            int best = 0;
            for (int ink = 1; ink < kInks; ++ink)
                if (v[ink] > v[best]) best = ink;
            inks[static_cast<std::size_t>(y) * kPairs + pp] =
                static_cast<std::uint8_t>(best);
        }

    // Per-byte cost of each bank (a pair is billed to the byte holding its
    // first pixel). The old per-byte-independent choice flipped banks
    // mid-region on black/white ties and priced a straddling pair as if
    // both its bits lived in one byte.
    constexpr int kCols = 40;
    std::vector<float> colCost(static_cast<std::size_t>(kHeight) * kCols * 2, 0.0f);
    for (int y = 0; y < kHeight; ++y)
        for (int pp = 0; pp < kPairs; ++pp) {
            const int ink = inks[static_cast<std::size_t>(y) * kPairs + pp];
            for (int bank = 0; bank < 2; ++bank)
                colCost[(static_cast<std::size_t>(y) * kCols + (pp * 2) / 7) * 2 + bank]
                    += inkCost[ink][bank];
        }

    // Iterated 2D DP: each sweep runs the per-row DP with a vertical bias
    // toward the neighbouring rows' CURRENT banks; sweeps alternate
    // top-down / bottom-up until the map stops changing (max 4). A single
    // top-down pass left bank walls wiggling row to row in tied regions.
    std::vector<std::uint8_t> banks(static_cast<std::size_t>(kHeight) * kCols, 0);
    for (int pass = 0; pass < 4; ++pass) {
        bool changed = false;
        const bool down = (pass & 1) == 0;
        for (int i = 0; i < kHeight; ++i) {
            const int y = down ? i : kHeight - 1 - i;
            const auto* above = (y > 0 && (pass > 0 || down))
                ? &banks[static_cast<std::size_t>(y - 1) * kCols] : nullptr;
            const auto* below = (y + 1 < kHeight && (pass > 0 || !down))
                ? &banks[static_cast<std::size_t>(y + 1) * kCols] : nullptr;
            float dp[kCols][2];
            std::uint8_t from[kCols][2] = {};
            for (int col = 0; col < kCols; ++col)
                for (int bank = 0; bank < 2; ++bank) {
                    float cost = colCost[(static_cast<std::size_t>(y) * kCols + col) * 2 + bank];
                    if (above && bank != above[col]) cost += kVerticalPenalty;
                    if (below && bank != below[col]) cost += kVerticalPenalty;
                    if (col == 0) { dp[col][bank] = cost; continue; }
                    // Boundaries after even bytes cut a colour pair in two:
                    // flipping banks there garbles that pair's hue.
                    const float flip = kBankChangePenalty
                        + (((col - 1) & 1) == 0 ? kStraddlePenalty : 0.0f);
                    float best = std::numeric_limits<float>::max();
                    for (int pb = 0; pb < 2; ++pb) {
                        const float c = dp[col - 1][pb] + (pb != bank ? flip : 0.0f);
                        if (c < best) { best = c; from[col][bank] = static_cast<std::uint8_t>(pb); }
                    }
                    dp[col][bank] = best + cost;
                }
            auto* row = &banks[static_cast<std::size_t>(y) * kCols];
            std::uint8_t chosen = dp[kCols - 1][1] < dp[kCols - 1][0] ? 1 : 0;
            for (int col = kCols - 1; col >= 0; --col) {
                if (row[col] != chosen) { row[col] = chosen; changed = true; }
                if (col > 0) chosen = from[col][chosen];
            }
        }
        if (pass > 0 && !changed) break;
    }

    // Emit, measuring what the constraints actually cost.
    std::vector<std::uint8_t> page(kHgrBytes, 0);
    double subSum = 0.0, subMax = 0.0;
    std::uint64_t voteTotal = 0, voteLost = 0;
    int pairsN = 0;
    for (int y = 0; y < kHeight; ++y) {
        std::array<std::uint8_t, kWidth> bits{};
        const auto* row = &banks[static_cast<std::size_t>(y) * kCols];
        for (int pp = 0; pp < kPairs; ++pp) {
            const int ink = inks[static_cast<std::size_t>(y) * kPairs + pp];
            const int x = pp * 2;
            const std::uint8_t code = inkBestCode[ink][row[x / 7]];
            bits[x] = code & 1u;
            bits[x + 1] = (code >> 1) & 1u;
            const double de = std::sqrt(inkCost[ink][row[x / 7]]);
            subSum += de; if (de > subMax) subMax = de; ++pairsN;
            const auto* v = voteAt(y, pp);
            std::uint64_t tot = 0;
            for (int k = 0; k < kInks; ++k) tot += v[k];
            voteTotal += tot; voteLost += tot - v[ink];
        }
        for (int col = 0; col < kCols; ++col) {
            std::uint8_t b = static_cast<std::uint8_t>(row[col] << 7);
            for (int bit = 0; bit < 7; ++bit) b |= bits[col * 7 + bit] << bit;
            page[hgrOffset(col * 7, y)] = b;
        }
    }
    if (report) {
        report->meanSubDe = pairsN ? static_cast<float>(subSum / pairsN) : 0.0f;
        report->maxSubDe = static_cast<float>(subMax);
        report->dissentPct = voteTotal
            ? static_cast<float>(100.0 * voteLost / voteTotal) : 0.0f;
    }
    return page;
}

std::vector<std::uint8_t> renderHgr(const std::vector<std::uint8_t>& page,
                                    const Rgb (&pal)[2][4])
{
    std::vector<std::uint8_t> rgb(kWidth * kHeight * 3);
    for (int y = 0; y < kHeight; ++y) {
        std::array<std::uint8_t, kWidth> bits{};
        std::array<std::uint8_t, 40> banks{};
        for (int col = 0; col < 40; ++col) {
            const auto b = page[hgrOffset(col * 7, y)]; banks[col] = b >> 7;
            for (int bit = 0; bit < 7; ++bit) bits[col * 7 + bit] = (b >> bit) & 1u;
        }
        for (int x = 0; x < kWidth; x += 2) {
            const int code = bits[x] | (bits[x + 1] << 1);
            const auto c = pal[banks[x / 7]][code];
            for (int q = 0; q < 2; ++q) {
                const int i = (y * kWidth + x + q) * 3;
                rgb[i] = c.r; rgb[i+1] = c.g; rgb[i+2] = c.b;
            }
        }
    }
    return rgb;
}

// Preview through POM2's OpenEmulator demod itself: the 560-dot line the
// page really produces (a hi-bit byte's dots delayed by one 14M dot), pushed
// through the same 17-tap FIR + YUV decode as Apple2Display::
// renderCompositeOeCpu (NTSC, sharpness 0.5, hue 0). Twice the flat
// preview's width, and it shows the real fringes at bank flips and byte
// boundaries that the flat palette preview hides.
std::vector<std::uint8_t> renderHgrOe(const std::vector<std::uint8_t>& page)
{
    constexpr int W = kWidth * 2;
    constexpr int FN = 8;
    static const float lumaK[FN + 1] = {
        0.27941f, 0.23593f, 0.13462f, 0.03665f, -0.01538f,
        -0.02210f, -0.00999f, -0.00072f, 0.00130f };
    static const float chromaK[FN + 1] = {
        0.26030f, 0.24788f, 0.21373f, 0.16602f, 0.11509f,
        0.07008f, 0.03648f, 0.01543f, 0.00515f };
    static const float sinP[4] = {0.0f, 1.0f, 0.0f, -1.0f};
    static const float cosP[4] = {1.0f, 0.0f, -1.0f, 0.0f};
    std::vector<std::uint8_t> rgb(static_cast<std::size_t>(W) * kHeight * 3);
    for (int y = 0; y < kHeight; ++y) {
        std::array<std::uint8_t, kWidth> bits{};
        std::array<std::uint8_t, 40> banks{};
        for (int col = 0; col < 40; ++col) {
            const auto b = page[hgrOffset(col * 7, y)]; banks[col] = b >> 7;
            for (int bit = 0; bit < 7; ++bit) bits[col * 7 + bit] = (b >> bit) & 1u;
        }
        std::array<std::uint8_t, W> raw{}, sig{};
        for (int x = 0; x < kWidth; ++x)
            raw[2 * x] = raw[2 * x + 1] = bits[x];
        for (int d = 0; d < W; ++d)
            sig[d] = banks[d / 14] ? (d > 0 ? raw[d - 1] : 0) : raw[d];
        for (int x = 0; x < W; ++x) {
            float fy = 0.0f, fu = 0.0f, fv = 0.0f;
            for (int i = -FN; i <= FN; ++i) {
                const int xi = x + i;
                if (xi < 0 || xi >= W) continue;
                const float sv = sig[xi] ? 1.0f : 0.0f;
                const int k = xi & 3;
                const int a = i < 0 ? -i : i;
                fy += sv * lumaK[a];
                fu += sv * sinP[k] * chromaK[a];
                fv += sv * cosP[k] * chromaK[a];
            }
            const float rf = fy + 1.139883f * fv;
            const float gf = fy - 0.394642f * fu - 0.580622f * fv;
            const float bf = fy + 2.032062f * fu;
            const auto cl = [](float v) { return v < 0.0f ? 0.0f : (v > 1.0f ? 1.0f : v); };
            const std::size_t o = (static_cast<std::size_t>(y) * W + x) * 3;
            rgb[o]     = static_cast<std::uint8_t>(cl(rf) * 255.0f + 0.5f);
            rgb[o + 1] = static_cast<std::uint8_t>(cl(gf) * 255.0f + 0.5f);
            rgb[o + 2] = static_cast<std::uint8_t>(cl(bf) * 255.0f + 0.5f);
        }
    }
    return rgb;
}

int usage()
{
    std::cerr << "usage:\n"
              << "  scoswamp_hgr convert INPUT.png OUTPUT.HGR.RLE.BIN [PREVIEW.png]"
                 " [--gamma X] [--palette oe|feline] [--report] [--preview-oe]\n"
              << "      gamma default 0.75 (1.0 = off); palette default oe ="
                 " OpenEmulator composite target; never dithers\n"
              << "      --report prints conversion-quality metrics;"
                 " --preview-oe renders the 560px preview through the OE FIR demod\n"
              << "  scoswamp_hgr encode INPUT.HGR.BIN OUTPUT.HGR.RLE.BIN\n"
              << "  scoswamp_hgr decode INPUT.HGR.RLE.BIN OUTPUT.HGR.BIN\n"
              << "  scoswamp_hgr validate INPUT.HGR.RLE.BIN\n";
    return 2;
}

} // namespace

int main(int argc, char** argv)
{
    if (argc < 3) return usage();
    const std::string command = argv[1];
    std::vector<std::uint8_t> input, raw;
    std::string error;

    if (command == "convert") {
        double gamma = kDefaultGamma;
        std::string palName = "oe";
        bool wantReport = false, previewOe = false;
        std::vector<const char*> pos;
        for (int i = 2; i < argc; ++i) {
            const std::string a = argv[i];
            if (a == "--gamma") {
                if (++i >= argc) return usage();
                gamma = std::atof(argv[i]);
            } else if (a.rfind("--gamma=", 0) == 0) {
                gamma = std::atof(a.c_str() + 8);
            } else if (a == "--report") {
                wantReport = true;
            } else if (a == "--preview-oe") {
                previewOe = true;
            } else if (a == "--palette") {
                if (++i >= argc) return usage();
                palName = argv[i];
            } else if (a.rfind("--palette=", 0) == 0) {
                palName = a.substr(10);
            } else {
                pos.push_back(argv[i]);
            }
        }
        if (pos.size() < 2 || pos.size() > 3 || gamma <= 0.0) return usage();
        if (palName != "oe" && palName != "feline") return usage();
        const auto& target = palName == "oe" ? kPaletteOE : kPaletteFeline;
        int w = 0, h = 0, channels = 0;
        stbi_uc* pixels = stbi_load(pos[0], &w, &h, &channels, 4);
        if (!pixels) { std::cerr << "cannot decode " << pos[0] << "\n"; return 1; }
        ConvertReport rep;
        raw = imageToHgr(pixels, w, h, gamma, target, &rep);
        stbi_image_free(pixels);
        const auto packed = encodeRle(raw);
        if (!writeFile(pos[1], packed)) { std::cerr << "cannot write output\n"; return 1; }
        if (pos.size() == 3) {
            const auto preview = previewOe ? renderHgrOe(raw) : renderHgr(raw, target);
            const int pw = previewOe ? kWidth * 2 : kWidth;
            if (!stbi_write_png(pos[2], pw, kHeight, 3, preview.data(), pw * 3)) {
                std::cerr << "cannot write preview\n"; return 1;
            }
        }
        std::cout << pos[1] << ": " << packed.size() << " bytes ("
                  << (100.0 * packed.size() / kHgrBytes) << "%)\n";
        if (wantReport)
            std::cout << "report: subDE mean=" << rep.meanSubDe
                      << " max=" << rep.maxSubDe
                      << " dissent=" << rep.dissentPct
                      << "% score=" << (rep.meanSubDe + 0.3f * rep.dissentPct) << "\n";
        return 0;
    }
    if (!readFile(argv[2], input)) { std::cerr << "cannot read input\n"; return 1; }
    if (command == "encode") {
        if (argc != 4 || input.size() != kHgrBytes) {
            std::cerr << "raw HGR input must be exactly 8192 bytes\n"; return 1;
        }
        if (!writeFile(argv[3], encodeRle(input))) return 1;
        return 0;
    }
    if (command == "decode" || command == "validate") {
        if ((command == "decode" && argc != 4) || (command == "validate" && argc != 3))
            return usage();
        if (!decodeRle(input, raw, error)) { std::cerr << error << "\n"; return 1; }
        if (command == "decode" && !writeFile(argv[3], raw)) return 1;
        std::cout << argv[2] << ": valid HGRR v1, 8192 bytes decoded\n";
        return 0;
    }
    return usage();
}
