#pragma once

// Key glyphs, read from the game's own Interface/exported/*.png.dds (loose or in its BSAs). Loaded on first use,
// cached, released with the device.
namespace Textures
{
	struct Image
	{
		unsigned long long id{ 0 };  // ImTextureID; 0 when the file is missing or broken
		float              width{ 0 };
		float              height{ 0 };

		explicit operator bool() const { return id != 0; }
	};

	void Init(void* a_device);  // ID3D11Device*

	// "keys/<name>" for Interface/exported/<name>.png.dds, e.g. "keys/esc"; any other name is an empty image.
	// A failed load is remembered, so a missing file is looked for only once.
	const Image& Get(std::string_view a_name);

	void ReleaseAll();
}
