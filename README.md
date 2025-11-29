# QA Overlay Builder

A powerful tool for creating time-limited AI-powered question answering overlays with self-destruct capabilities.

## 🚀 Features

- **AI-Powered Answers**: Uses Groq API with LLaMA models for accurate multiple choice answers
- **Multiple Question Support**: Process single questions or multiple questions at once
- **Time-Limited Execution**: Built-in expiration system with automatic self-destruct
- **Customizable UI**: Configure hotkeys, overlay position, and appearance
- **Executable Builder**: Generate standalone .exe files with PyInstaller
- **Real-Time Feedback**: Live countdown showing time remaining until expiration
- **Compact Display**: Shows answers in format like "1.a 2.c 3.b"

## 📋 Requirements

- Python 3.7+
- Required packages (install via `pip install -r requirements.txt`):
  - tkinter (usually included with Python)
  - requests
  - pyperclip
  - keyboard
  - pyinstaller

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/Animhassen/QA-overlay-builder.git
cd QA-overlay-builder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get a Groq API key from [Groq Console](https://console.groq.com/)

## 🎯 Usage

### Running the Builder

```bash
python QA_builder.py
```

### Configuration Options

1. **API Configuration**:
   - Enter your Groq API key
   - Select AI model (LLaMA 3.1 8B Instant recommended)

2. **UI Configuration**:
   - Set hotkey (default: Ctrl+Shift+Q)
   - Choose overlay position (bottom-left, bottom-right, top-left, top-right)

3. **Build Configuration**:
   - Set output executable name
   - Configure expiration date and time (12-hour format)
   - Optional: Add custom icon

### Using Generated Overlays

1. Run the generated script or executable
2. Select question text in any application
3. Press the configured hotkey (default: Ctrl+Shift+Q)
4. Wait for AI-powered answer to appear

### Answer Formats

- **Single Question**: `1.a`
- **Multiple Questions**: `1.a 2.c 3.b`
- **Processing**: Shows "Analyzing..." briefly, then hides until answer ready

## ⚡ How It Works

1. **Text Capture**: Automatically copies selected text when hotkey is pressed
2. **Question Detection**: Identifies single or multiple numbered questions
3. **AI Processing**: Sends questions to Groq API for analysis
4. **Answer Display**: Shows compact answers in overlay window
5. **Auto-Hide**: Overlay disappears after showing results

## 🔒 Security Features

- **Time-Limited**: Scripts expire on specified date/time
- **Self-Destruct**: Automatically deletes itself when expired
- **Periodic Checks**: Monitors expiration every 30 seconds while running

## 📁 File Structure

```
QA_overlay/
├── QA_builder.py          # Main builder application
├── QA_standalone.py       # Template script (for reference)
├── requirements.txt       # Python dependencies
├── image.ico             # Default icon
└── README.md             # This file
```

## 🎨 Customization

### Overlay Positions
- `bottom-left`: Bottom-left corner of screen
- `bottom-right`: Bottom-right corner of screen  
- `top-left`: Top-left corner of screen
- `top-right`: Top-right corner of screen

### Hotkey Options
- `ctrl+shift+q` (default)
- `ctrl+alt+q`
- `alt+shift+q`
- `ctrl+q`

### AI Models
- `llama-3.1-8b-instant` (fastest, recommended)
- `llama-3.1-70b-versatile` (more accurate, slower)
- `mixtral-8x7b-32768` (alternative option)

## 🚨 Important Notes

- **API Key Required**: You must provide your own Groq API key
- **Windows Only**: Self-destruct mechanism designed for Windows
- **Admin Rights**: May require administrator privileges for some operations
- **Antivirus**: Some antivirus software may flag self-modifying executables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for complying with their institution's policies and applicable laws. The authors are not responsible for any misuse of this software.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Animhassen/QA-overlay-builder/issues) page
2. Create a new issue with detailed information
3. Include error messages and system information

---

**Made with ❤️ for educational purposes**
