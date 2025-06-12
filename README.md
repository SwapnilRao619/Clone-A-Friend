# Clone A Friend

**Clone A Friend** allows you to create a conversational AI that mimics the texting style and persona of a friend, based on an exported chat history text file. Chat with a digital version of someone you miss, or just explore the possibilities of personalized AI!

This project uses a Large Language Model (LLM) via the Groq API (currently leveraging Llama 3) to understand and replicate your friend's communication patterns.

## Features

*   **Chat History Parsing:** Intelligently extracts messages from a specific friend in an exported chat file (e.g., WhatsApp export).
*   **Persona Emulation:** Uses the friend's messages as style examples to guide the LLM in adopting their tone, vocabulary, emoji usage, and common phrases.
*   **Interactive Chat:** Engage in a real-time conversation with the "cloned" friend via a command-line interface.
*   **Contextual Conversation:** The clone remembers the recent parts of your current conversation to provide relevant responses.
*   **Powered by Groq & Llama 3:** Utilizes the speed of Groq and the capabilities of Llama 3 (or other compatible models) for response generation.

## How It Works

1.  **Input:** You provide an exported chat history file (e.g., `.txt` from WhatsApp) and the exact name of the friend you wish to clone.
2.  **Parsing:** The `chat_parser.py` script reads the file, filters out system messages, and isolates all messages sent by the specified friend. It also tries to identify the other main chat participant (you).
3.  **Persona Priming:** The `llm_handler.py` script constructs a detailed system prompt for the LLM. This prompt includes:
    *   Instructions to act as the specified friend.
    *   A selection of the friend's actual messages as examples of their texting style.
    *   The context of who the LLM (as the friend) is talking to.
4.  **LLM Interaction:** Your messages are sent to the Groq API, along with the system prompt and recent conversation history. The LLM generates a response in the style of your friend.
5.  **Conversation Loop:** The `main.py` script manages the user interface, sending your inputs to the LLM handler and displaying the clone's responses.

## Tech Stack

*   Python 3.x
*   [Groq API](https://groq.com/) for LLM inference
*   [Llama 3](https://llama.meta.com/) (or other compatible models available on Groq)
*   `python-dotenv` for environment variable management
*   `groq` Python client library

## Project Structure

clone_a_friend/
├── .env # Stores your GROQ_API_KEY (you create this)
├── requirements.txt # Python dependencies
├── chat_parser.py # Logic to parse the chat file
├── llm_handler.py # Logic to interact with the Groq API
├── main.py # Main application script
└── example_chat.txt # Example chat file (or your own)


## Getting Started

### Prerequisites

*   Python 3.7 or higher.
*   A Groq API Key:
    1.  Sign up or log in at [Groq Console](https://console.groq.com/).
    2.  Navigate to the API Keys section and create a new key.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/clone-a-friend.git
    cd clone-a-friend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    Create a file named `.env` in the root of the `clone_a_friend` directory and add your Groq API key:
    ```env
    # clone_a_friend/.env
    GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"
    ```
    Replace `"YOUR_GROQ_API_KEY_HERE"` with your actual key.

### Running the Application

1.  Ensure your terminal is in the `clone_a_friend` directory and your virtual environment (if used) is activated.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  **Follow the prompts:**
    *   **Enter the path to the exported chat text file:** Provide the path to your chat history `.txt` file (e.g., `example_chat.txt` or `/path/to/your/chat.txt`).
    *   **Enter the exact name of the friend you want to clone:** Type the friend's name exactly as it appears in the chat file (e.g., "John Doe", "Alice B (Work)"). This is case-sensitive.

4.  **Start chatting!** Type your messages and press Enter. To quit, type `quit` or `exit`.


## 📝 Key Files Overview

*   `main.py`: Orchestrates the application flow, handles user input/output, and initializes other components.
*   `chat_parser.py`: Responsible for reading the chat file, cleaning the data, and extracting messages from the specified friend.
*   `llm_handler.py`: Manages communication with the Groq API, constructs the necessary prompts, and retrieves the LLM's responses.

## Important Considerations & Limitations

*   **LLM Model:** The default model is Llama 3 8B (`llama3-8b-8192`). You can experiment with other models available on Groq (e.g., `llama3-70b-8192` for potentially higher quality but possibly slower responses) by changing `LLM_MODEL` in `llm_handler.py`.
*   **Context Window:** LLMs have a limited context window. The number of example messages (`MAX_EXAMPLE_MESSAGES`) and conversation history turns (`MAX_CONVERSATION_HISTORY_TURNS`) are capped to prevent exceeding this limit. If you encounter errors, try reducing these values.
*   **Chat Parsing:** The parser is designed for a common WhatsApp export format. Variations might require adjustments to the regex in `chat_parser.py`.
*   **Persona Consistency:** While the LLM tries its best, the clone might occasionally break character or not perfectly replicate every nuance, especially in very long conversations. The quality of the clone heavily depends on the quantity and distinctiveness of the provided chat examples.
*   **Knowledge Limitation:** The clone's "knowledge" is primarily derived from the style and content of the provided chat history. It will not have external knowledge or memory of events not discussed in the chats used for priming.
*   **Groq API Usage:** Be mindful of Groq's API rate limits and usage policies.
*   **Ethical Considerations:** This tool is intended for personal, experimental, or sentimental use. Please be respectful of privacy and the concept of digital likeness. Always ensure you have the right to use any chat data.

## Potential Future Enhancements

*   Graphical User Interface (GUI).
*   Support for more chat platforms and export formats.
*   More advanced context management and RAG (Retrieval Augmented Generation) for better long-term memory and consistency.
*   Option to save and load "clones."
*   Fine-tuning (if feasible and appropriate LLMs become available) for deeper persona adoption.

## Contributing

Contributions are welcome! If you have ideas for improvements or find bugs, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

---
