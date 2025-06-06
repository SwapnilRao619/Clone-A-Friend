import os
from dotenv import load_dotenv
from chat_parser import parse_chat_file
from llm_handler import LLMHandler, MAX_EXAMPLE_MESSAGES

# Max turns to keep in conversation history for the LLM (each turn is user + assistant)
MAX_CONVERSATION_HISTORY_TURNS = 10

def main():
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        print("Error: GROQ_API_KEY not found in .env file.")
        print("Please create a .env file in the project root with your Groq API key:")
        print("GROQ_API_KEY=\"your_key_here\"")
        return

    print("Welcome to Clone-A-Friend!")

    while True:
        chat_file_path = input("Enter the path to the exported chat text file: ").strip()
        if os.path.exists(chat_file_path):
            break
        print(f"File not found: {chat_file_path}. Please try again.")

    friend_name_to_clone = input("Enter the exact name of the friend you want to clone (as it appears in the chat file): ").strip()

    print(f"\nParsing chat history for {friend_name_to_clone}'s messages...")
    friend_messages, chat_partner_name = parse_chat_file(chat_file_path, friend_name_to_clone)

    if not friend_messages:
        print(f"Could not find any messages for '{friend_name_to_clone}'. Exiting.")
        return

    print(f"Found {len(friend_messages)} messages from {friend_name_to_clone}.")
    if chat_partner_name:
        print(f"Identified you (the chat partner) as: {chat_partner_name}")
    else:
        print("Could not automatically identify the other chat participant. Will use a generic placeholder.")
        chat_partner_name = "Friend" # Fallback

    # We'll use the most recent messages as style examples
    # The llm_handler will also take a subset if this list is too long.
    # Here, we're just passing all of them; llm_handler will pick from the end.
    friend_style_examples = friend_messages
    print(f"Using up to {min(len(friend_style_examples), MAX_EXAMPLE_MESSAGES)} recent messages from {friend_name_to_clone} as style examples.")

    llm = LLMHandler(api_key=groq_api_key)

    print(f"\n--- Chatting with Clone of {friend_name_to_clone} ---")
    print(f"You are now chatting with a digital clone of {friend_name_to_clone}.")
    print(f"The clone's persona is based on their chat history with {chat_partner_name}.")
    print("Type 'quit' or 'exit' to end the chat.")

    conversation_history_for_llm = [] # Stores {"role": "user", "content": ...} or {"role": "assistant", "content": ...}

    while True:
        user_input = input(f"{chat_partner_name} (User): ") # <--- CORRECTED LINE
        if user_input.lower() in ['quit', 'exit']:
            print("Exiting chat. Goodbye!")
            break

        if not user_input.strip():
            continue

        # Add user's message to LLM history immediately before calling LLM
        # The LLMHandler will structure this into the final API call
        # For our own tracking:
        # current_turn_for_llm_history = [{"role": "user", "content": user_input}]


        print(f"{friend_name_to_clone} (Clone): Thinking...") # Placeholder while waiting

        clone_response = llm.generate_response(
            friend_name=friend_name_to_clone,
            user_name=chat_partner_name,
            friend_style_examples=friend_style_examples,
            conversation_history=conversation_history_for_llm, # Pass the history so far
            user_message=user_input
        )

        if clone_response:
            print(f"\r{friend_name_to_clone} (Clone): {clone_response}") # \r to overwrite "Thinking..."
            # Add user message and assistant response to history
            conversation_history_for_llm.append({"role": "user", "content": user_input})
            conversation_history_for_llm.append({"role": "assistant", "content": clone_response})

            # Trim conversation history to prevent it from growing too large
            if len(conversation_history_for_llm) > MAX_CONVERSATION_HISTORY_TURNS * 2: # *2 for user+assistant
                # Keep only the last MAX_CONVERSATION_HISTORY_TURNS
                conversation_history_for_llm = conversation_history_for_llm[-(MAX_CONVERSATION_HISTORY_TURNS * 2):]
        else:
            print(f"\r{friend_name_to_clone} (Clone): Sorry, I couldn't generate a response right now.")

if __name__ == "__main__":
    main()