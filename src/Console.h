#pragma once

namespace Console
{
	// Runs a console command on the game thread, optionally against a reference
	// (same as selecting it in the console first).
	void Run(std::string a_command, RE::ObjectRefHandle a_target = {});

	// Like Run, then hands what the command printed into the console to a_done
	// (on the game thread).
	void RunCaptured(std::string a_command, RE::ObjectRefHandle a_target, std::function<void(std::string)> a_done);

	// Prints a line into the in-game console log.
	void Print(std::string_view a_text);

	// A console batch file (what the game's "bat" command runs): a .txt with one command per line.
	struct BatFile
	{
		std::string           group;  // folder under bat/, "" for bat/ itself, "a / b" when nested
		std::string           name;   // file name without .txt
		std::filesystem::path path;
	};

	// <game folder>/bat
	std::filesystem::path BatDirectory();

	// Every .txt under BatDirectory(), searched recursively: bat/ itself first, then by folder, by name in each.
	std::vector<BatFile> FindBatFiles();

	// Runs each command of a batch file in order; returns how many, or nullopt when it can't be read.
	std::optional<int> RunBatFile(const std::filesystem::path& a_path, RE::ObjectRefHandle a_target = {});
}
