#include "MenuFramework.h"

#include "Hotkeys.h"
#include "Input.h"
#include "Settings.h"

// The framework's own ImGui (ImGuiMCP), called through its DLL; this file must not include the menu's imgui.h.
#include <SKSEMenuFramework.h>

namespace MenuFramework
{
	namespace
	{
		// The framework releases the game's input and pause a frame or two after its window closes.
		constexpr int kSettleFrames = 3;

		std::atomic<bool> g_openRequested{ false };
		int               g_settled = 0;

		void __stdcall RenderGeneral()
		{
			ImGuiMCP::TextWrapped("%s", "An in-game cheat and tool menu.");
			ImGuiMCP::Spacing();
			ImGuiMCP::Text("Keyboard: %s", Hotkeys::KeyName(Settings::Get().toggleKey).c_str());
			const auto& pad = Settings::Get().gamepadToggle;
			ImGuiMCP::Text("Gamepad: %s", pad.empty() ? "not set (gamepadToggle= in DragonbornsCodex.ini)" : pad.c_str());
			ImGuiMCP::Spacing();
			if (ImGuiMCP::Button("Open Dragonborn's Codex")) {
				if (auto window = SKSEMenuFramework::GetMainWindow()) {
					window->IsOpen = false;
				}
				g_settled = 0;
				g_openRequested = true;
			}
		}
	}

	void Register()
	{
		if (!SKSEMenuFramework::IsInstalled()) {
			return;
		}
		SKSEMenuFramework::SetSection("Dragonborn's Codex");
		SKSEMenuFramework::AddSectionItem("General", RenderGeneral);
		logger::info("SKSE Menu Framework: added the Dragonborn's Codex section");
	}

	void Update()
	{
		if (!g_openRequested) {
			return;
		}
		if (SKSEMenuFramework::IsAnyBlockingWindowOpened()) {
			g_settled = 0;
			return;
		}
		if (++g_settled < kSettleFrames) {
			return;
		}
		g_openRequested = false;
		Input::TryOpenMenu();
	}
}
