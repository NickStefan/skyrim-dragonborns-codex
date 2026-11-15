#include "Console.h"

namespace Console
{
	void Run(std::string a_command, RE::ObjectRefHandle a_target)
	{
		SKSE::GetTaskInterface()->AddTask([command = std::move(a_command), a_target]() {
			auto factory = RE::IFormFactory::GetConcreteFormFactoryByType<RE::Script>();
			auto script = factory ? factory->Create() : nullptr;
			if (!script) {
				logger::error("Failed to create console script for '{}'", command);
				return;
			}
			auto target = a_target.get();
			script->SetCommand(command);
			script->CompileAndRun(target.get());
			delete script;
			logger::info("console: {}", command);
		});
	}

	void RunCaptured(std::string a_command, RE::ObjectRefHandle a_target, std::function<void(std::string)> a_done)
	{
		SKSE::GetTaskInterface()->AddTask([command = std::move(a_command), a_target, done = std::move(a_done)]() {
			// What the command printed = what was added to the log.
			auto log = RE::ConsoleLog::GetSingleton();
			if (log && std::string_view{ log->buffer.c_str() }.size() > 48000) {
				log->buffer = "";  // a full log (64 KB) takes no more lines at all
			}
			const std::string before = log ? std::string{ log->buffer.c_str() } : std::string{};
			auto        factory = RE::IFormFactory::GetConcreteFormFactoryByType<RE::Script>();
			auto        script = factory ? factory->Create() : nullptr;
			std::string output;
			if (script) {
				auto target = a_target.get();
				script->SetCommand(command);
				script->CompileAndRun(target.get());
				delete script;
				logger::info("console: {}", command);
			}
			if (log) {
				const std::string_view all{ log->buffer.c_str() };
				output = all.starts_with(before) ? std::string{ all.substr(before.size()) } : std::string{ all };
			}
			done(std::move(output));
		});
	}

	void Print(std::string_view a_text)
	{
		if (auto log = RE::ConsoleLog::GetSingleton()) {
			log->Print("%.*s", static_cast<int>(a_text.size()), a_text.data());
		}
	}

	namespace
	{
		std::string Utf8(const std::filesystem::path& a_path)
		{
			const auto text = a_path.u8string();
			return { reinterpret_cast<const char*>(text.data()), text.size() };
		}

		std::string Lower(std::string a_text)
		{
			std::ranges::transform(a_text, a_text.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
			return a_text;
		}
	}

	std::filesystem::path BatDirectory()
	{
		std::wstring exe(MAX_PATH, L'\0');
		for (;;) {
			const auto size = ::GetModuleFileNameW(nullptr, exe.data(), static_cast<DWORD>(exe.size()));
			if (size == 0) {
				return std::filesystem::current_path() / "bat";
			}
			if (size < exe.size()) {
				exe.resize(size);
				break;
			}
			exe.resize(exe.size() * 2);
		}
		return std::filesystem::path{ exe }.parent_path() / "bat";
	}

	std::vector<BatFile> FindBatFiles()
	{
		const auto           root = BatDirectory();
		std::vector<BatFile> files;
		std::error_code      error;
		for (std::filesystem::recursive_directory_iterator it{ root, std::filesystem::directory_options::skip_permission_denied, error }, end; !error && it != end;
			 it.increment(error)) {
			if (!it->is_regular_file(error) || Lower(Utf8(it->path().extension())) != ".txt") {
				continue;
			}
			std::string group;
			for (const auto& part : it->path().parent_path().lexically_relative(root)) {
				if (part != ".") {
					group += (group.empty() ? "" : " / ") + Utf8(part);
				}
			}
			files.push_back({ std::move(group), Utf8(it->path().stem()), it->path() });
		}
		std::ranges::sort(files, [](const BatFile& a, const BatFile& b) {
			const auto ag = Lower(a.group), bg = Lower(b.group);
			return ag != bg ? ag < bg : Lower(a.name) < Lower(b.name);
		});
		return files;
	}

	std::optional<std::vector<std::string>> ReadBatFile(const std::filesystem::path& a_path)
	{
		std::ifstream file{ a_path };
		if (!file) {
			logger::warn("bat: can't read {}", Utf8(a_path));
			return std::nullopt;
		}
		std::vector<std::string> lines;
		std::string              line;
		for (bool first = true; std::getline(file, line); first = false) {
			if (first && line.starts_with("\xEF\xBB\xBF")) {
				line.erase(0, 3);
			}
			if (line.ends_with('\r')) {
				line.pop_back();
			}
			lines.push_back(std::move(line));
		}
		return lines;
	}

	bool IsBatCommand(std::string_view a_line)
	{
		const auto start = a_line.find_first_not_of(" \t");
		if (start == std::string_view::npos) {
			return false;
		}
		a_line.remove_prefix(start);
		return !a_line.starts_with(';') && !a_line.starts_with("//");
	}

	std::optional<int> RunBatFile(const std::filesystem::path& a_path, RE::ObjectRefHandle a_target)
	{
		auto lines = ReadBatFile(a_path);
		if (!lines) {
			return std::nullopt;
		}
		int count = 0;
		for (auto& line : *lines) {
			if (!IsBatCommand(line)) {
				continue;
			}
			line.erase(0, line.find_first_not_of(" \t"));
			line.erase(line.find_last_not_of(" \t") + 1);
			Run(line, a_target);
			++count;
		}
		logger::info("bat: {} ({} commands)", Utf8(a_path), count);
		return count;
	}
}
