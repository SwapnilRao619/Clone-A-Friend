import os
from groq import Groq, GroqError
from typing import List, Dict, Optional

# Model to use. You can try different Llama3 versions available on Groq.
# e.g., "llama3-8b-8192", "llama3-70b-8192"
LLM_MODEL = "llama3-8b-8192"
MAX_EXAMPLE_MESSAGES = 15 # Number of friend's example messages to include in prompt
MAX_CONVERSATION_TOKENS = 4096 # Max tokens for conversation history to keep it manageable

class LLMHandler:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Groq API key not provided.")
        self.client = Groq(api_key=api_key)
        self.model = LLM_MODEL

    def generate_response(self, friend_name: str, user_name: Optional[str],
                          friend_style_examples: List[str],
                          conversation_history: List[Dict[str, str]],
                          user_message: str) -> Optional[str]:
        """
        Generates a response from the LLM emulating the friend.

        Args:
            friend_name (str): The name of the friend being cloned.
            user_name (str): The name of the person chatting with the clone (the original chat partner).
            friend_style_examples (List[str]): A list of messages from the friend for style guidance.
            conversation_history (List[Dict[str,str]]): Current chat history [{'role': 'user'/'assistant', 'content': ...}].
            user_message (str): The latest message from the user.

        Returns:
            Optional[str]: The LLM's generated response, or None if an error occurs.
        """
        
        # Construct the system prompt
        system_prompt_content = f"You are {friend_name}. You are talking to {user_name if user_name else 'your friend'}."
        system_prompt_content += " Your goal is to impersonate {friend_name} as accurately as possible, mimicking their texting style, tone, common phrases, emoji usage, and typical response length based on the following examples of their past messages."
        system_prompt_content += " Do not explicitly state you are an AI or a clone. Respond naturally as if you are {friend_name}.\n\n"
        system_prompt_content += "Here are some examples of how {friend_name} texts:\n"

        # Add examples, ensuring not to make the prompt too long
        # Using a subset of examples
        examples_to_use = friend_style_examples[-MAX_EXAMPLE_MESSAGES:]
        for i, example in enumerate(examples_to_use):
            system_prompt_content += f"- \"{example}\"\n"
        
        system_prompt_content += f"\nNow, continue the conversation. You are {friend_name}. The user ({user_name if user_name else 'your friend'}) has just said: \"{user_message}\"."
        system_prompt_content += f"\nOnly output {friend_name}'s response. Do not add any prefixes like '{friend_name}: '."


        messages_for_api = [
            {"role": "system", "content": system_prompt_content}
        ]

        # Add recent conversation history (ensure it doesn't get too long)
        # A simple way is to take the last N turns. More sophisticated methods could count tokens.
        # For now, let's keep it simple. The system prompt contains most context.
        # The Groq API expects 'user' and 'assistant' roles.
        # Our 'conversation_history' is already in this format.

        # Add existing conversation history
        # The prompt is structured so the latest user message is part of the system prompt's instruction,
        # but for API consistency, it's better to pass full history.
        
        # Build the message list for the API
        # System prompt first
        api_messages = [{"role": "system", "content": system_prompt_content}]
        
        # Add conversation history (user prompts and assistant responses)
        # The 'user' in conversation_history is the actual human user.
        # The 'assistant' is the clone.
        for chat_turn in conversation_history:
            api_messages.append(chat_turn)
        
        # Add the current user's message
        api_messages.append({"role": "user", "content": user_message})


        try:
            # print("\n--- Sending to Groq API ---")
            # print(f"System Prompt: {system_prompt_content[:500]}...") # Print start of system prompt
            # print(f"Last few messages for API: {api_messages[-3:]}")  # Print last few actual messages sent
            
            chat_completion = self.client.chat.completions.create(
                messages=api_messages,
                model=self.model,
                temperature=0.7, # Adjust for creativity vs. predictability
                max_tokens=150,   # Max length of the generated response
            )
            response = chat_completion.choices[0].message.content.strip()
            # print(f"Raw LLM Response: '{response}'") # Debugging
            return response
        except GroqError as e:
            print(f"Groq API Error: {e}")
            if "context_length_exceeded" in str(e).lower():
                print("Context length exceeded. Try reducing MAX_EXAMPLE_MESSAGES or a shorter chat history.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with the LLM: {e}")
            return None

if __name__ == '__main__':
    # This is a simple test. Requires .env to be set up.
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not found in .env file. Skipping LLMHandler test.")
    else:
        handler = LLMHandler(api_key=api_key)
        
        # Dummy data for testing
        test_friend_name = "Alice"
        test_user_name = "Bob"
        test_friend_examples = [
            "Hey Bob! How's it going? 😄",
            "lol totally! we should hang out soon",
            "Ugh, work was so draining today 😩",
            "OMG guess what happened?!",
            "Sounds good, ttyl!",
            "Haha you're hilarious 😂"
        ]
        test_conversation_history = [
            {"role": "user", "content": "Hey Alice, what's up?"},
            {"role": "assistant", "content": "Not much, just chilling! You?"} # This would be a previous response from the clone
        ]
        test_user_message = "Thinking of grabbing some pizza later, wanna join?"

        print(f"\n--- Testing LLMHandler for {test_friend_name} talking to {test_user_name} ---")
        print(f"{test_user_name} (User): {test_user_message}")
        
        response = handler.generate_response(
            friend_name=test_friend_name,
            user_name=test_user_name,
            friend_style_examples=test_friend_examples,
            conversation_history=test_conversation_history,
            user_message=test_user_message
        )
        
        if response:
            print(f"{test_friend_name} (Clone): {response}")
        else:
            print(f"Failed to get a response for {test_friend_name}.")