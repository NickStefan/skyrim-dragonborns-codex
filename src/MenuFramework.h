#pragma once

// A "Dragonborn's Codex" section in SKSE Menu Framework's menu, when that mod is installed: a General page with a
// button that opens this menu. Without the framework this does nothing; nothing links against it.
namespace MenuFramework
{
	void Register();

	// Render thread, every frame: opens the menu once the framework's window has let go of the game.
	void Update();
}
