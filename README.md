# AI-Driven RPG Adventure

An experimental RPG game that uses AI agents to generate dynamic story content, NPC interactions, and quests.

## Features

- Dynamic story generation using AI
- Procedurally generated NPCs with unique personalities
- Adaptive quest system
- Modern UI with pygame
- Scene-based game architecture
- Persistent game state

## Project Structure

```
.
├── src/
│   ├── ai/              # AI agent implementations
│   ├── core/            # Core game systems
│   ├── tools/           # Game tools and utilities
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── game/                # Game data
│   ├── docs/           # Story and NPC documentation
│   └── templates/      # Game element templates
└── saves/              # Game save files
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-rpg-adventure.git
cd ai-rpg-adventure
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

## Running the Game

```bash
python src/main.py
```

## Running Tests

```bash
python tests/test_core.py
```

## Development

The project uses a modular architecture with the following main components:

- `Game`: Main game class that coordinates all systems
- `GameState`: Manages game state and persistence
- `SceneManager`: Handles different game screens
- `UIManager`: Manages UI elements and rendering
- `TemplateManager`: Handles game element templates
- `DocumentManager`: Manages story and NPC documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 