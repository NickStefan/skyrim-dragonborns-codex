#pragma once

namespace Input
{
	// Listens to the game's input stream: the toggle key (Insert by default) opens the menu, and while it is open
	// keyboard/mouse/gamepad events are forwarded to ImGui and gameplay controls are blocked.
	void Install();

	bool IsMenuOpen();

	// A keyboard key (DirectInput code) is held down in the game right now.
	bool IsKeyHeld(std::uint32_t a_dik);

	// Test hook: a keyboard key (DirectInput code) going down or up, handled exactly like
	// one from the game's input stream.
	void SimulateKey(std::uint32_t a_dik, bool a_down);
	void SetMenuOpen(bool a_open);

	// Opens the menu if the game is in a state where the toggle key would (a game loaded, no main menu or console).
	void TryOpenMenu();

	// Gamepad right stick, -1..1 (y up); the overlay moves the cursor with it while the menu is open.
	std::pair<float, float> RightStick();

	// The button names gamepadToggle accepts, comma-separated, for the ini comment.
	std::string PadButtonNames();

	// The gamepad toggle's buttons for the footer hint: "keys/360_x" glyph names, or a name to frame ("DPadUp");
	// empty when gamepadToggle is off.
	std::vector<std::string> GamepadToggleGlyphs();
}
