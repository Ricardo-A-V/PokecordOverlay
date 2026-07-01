# Pokémon Discord Voice Overlay

A lightweight, borderless desktop overlay that displays Pokémon sprites reacting in real-time to Discord voice channel activity.

Built with Python and PyQt6, this application bypasses Windows Taskbar Z-order restrictions to remain strictly topmost while being completely transparent to mouse inputs (click-through). It relies on Discord's StreamKit WebEngine, meaning it does not require Discord API developer tokens or bot installations.

## 📥 Installation (End Users)

Do not download the source code unless you intend to modify it. For standard use, download the compiled release.

1. Go to the [Releases](../../releases) page of this repository.
2. Download the latest `.zip` file.
3. Extract the contents into a folder.
4. **CRITICAL:** The executable (`.exe`) must always remain in the same directory as the `assets/` folder and the `config.json` file. If you separate them, the application will crash. Create a shortcut of the executable if you want to launch it from your desktop.

## ⚙️ Configuration

Before running the application, you must configure your `config.json` file (rename `config.example.json` to `config.json` if you are setting it up for the first time).

### 1. Extracting your StreamKit URL

Due to Discord's privacy model, voice data is extracted via their official broadcasting widget.

1. Open your browser and navigate to: [Discord StreamKit Overlay](https://streamkit.discord.com/overlay)
2. Click on **Install for OBS**.
3. Select the **Voice Widget** tab at the top.
4. Using the dropdown menus, select your target **Server** and **Voice Channel**.
5. Copy the generated URL located in the dark preview box on the right side of the screen.
6. Open `config.json` and paste this URL into the `"channels"` block. You can save multiple channels by giving them unique names.

### 2. Mapping Users to Pokémon

The `"users"` block in `config.json` maps a user's Discord ID to a specific Pokémon sprite.

**How to get a Discord User ID:**

1. In Discord, go to User Settings > Advanced > Enable **Developer Mode**.
2. Right-click any user's avatar and select **Copy User ID**.
3. Paste the ID as a key in the JSON file.

**User Parameters:**

- `"species"`: The exact name of the folder inside `assets/sprites/` (e.g., `"gengar"`).
- `"offset_y"`: Vertical adjustment in pixels. Use negative values (e.g., `-10`) to lower the sprite, or positive values to raise it.

_Note: If an unmapped user joins the voice channel, the application will automatically render the fallback species defined in the `"default"` variable (e.g., `"ditto"`)._

---

## 🚀 Usage

1. Double-click the executable. There is no main window; this is intentional.
2. The Pokémon sprites will instantly appear at the bottom left of your primary monitor once users connect to the configured voice channel.
3. **Changing Channels & Exiting:** Locate the application icon (computer shape) in your Windows System Tray (bottom right, near the clock).
   - **Left Click:** Opens a quick menu to switch between the Discord channels defined in your `config.json` and opens the context menu to safely quit the application.
