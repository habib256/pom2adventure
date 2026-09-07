// Minimal headless host for the POM2 core (GPL-3.0-or-later).
// No GUI or persistent settings; HDV slot 5, Mockingboard slot 2.
#include "EmulationController.h"
#include "AiControlServer.h"
#include "Apple2Display.h"
#include "ProDOSHardDiskCard.h"
#include "Mockingboard.h"
#include <csignal>
#include <iostream>

static volatile std::sig_atomic_t stopped = 0;
static void stop(int) { stopped = 1; }

int main(int argc, char** argv) {
    try {
        int port = 6503, speed = 200000;
        std::string disk;
        for (int i = 1; i < argc; ++i) {
            std::string a = argv[i];
            if (a == "--preset" && i + 1 < argc) {
                if (std::string(argv[++i]) != "iie") return 2;
            } else if (a == "--speed" && i + 1 < argc) speed = std::stoi(argv[++i]);
            else if (a.rfind("--ai-control=", 0) == 0) port = std::stoi(a.substr(13));
            else if (!a.empty() && a[0] != '-' && disk.empty()) disk = a;
            else return 2;
        }
        if (disk.empty() || port < 1 || port > 65535 || speed < 1) return 2;
        EmulationController ctrl;
        auto& mem = ctrl.memory();
        mem.setIIEMode(true);
        if (!mem.loadAppleIIRom(POM2_ROOT "/roms/apple2e.rom"))
            throw std::runtime_error("Apple IIe ROM unavailable");
        if (!mem.loadCharRom(POM2_ROOT "/roms/apple2e_char_us.rom"))
            throw std::runtime_error("Character ROM unavailable");
        ctrl.cpu().setCpuMode(M6502::CpuMode::CMOS);
        auto hdv = std::make_unique<ProDOSHardDiskCard>(5);
        if (!hdv->loadImage(disk)) throw std::runtime_error("Cannot load HDV");
        auto* diskCard = hdv.get();
        mem.slotBus().plug(5, std::move(hdv));
        mem.slotBus().plug(2, std::make_unique<MockingboardCard>(2));
        if (!ctrl.bootFromSlot(5)) throw std::runtime_error("Cannot boot slot 5");
        ctrl.setCyclesPerFrame(speed);
        Apple2Display display;
        // Match the GUI host: 80-column text and DHGR need the AUX plane.
        display.setAuxMemory(mem.auxData());
        pom2::AiControlServer server;
        server.attach(&ctrl, &display, nullptr, diskCard);
        server.setProfileLabel("Apple //e Enhanced (headless)");
        if (!server.start(static_cast<uint16_t>(port))) return 1;
        std::signal(SIGTERM, stop);
        std::signal(SIGINT, stop);
        ctrl.start();
        ctrl.setMode(EmulationController::Mode::Running);
        while (!stopped) std::this_thread::sleep_for(std::chrono::milliseconds(100));
        server.stop();
        ctrl.stop();
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
