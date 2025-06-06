# clone_a_friend/chat_parser.py
import re
from typing import List, Dict, Optional, Tuple

# Regex to capture date, time, sender, and message
# Handles both 12h (am/pm) and potentially 24h if am/pm is missing
# Also handles multi-line messages
MESSAGE_REGEX = re.compile(
    r"(\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s*(?:[ap]\.?m\.?)?)\s*-\s*([^:]+):\s*(.*)",
    re.IGNORECASE
)

# System messages to ignore
SYSTEM_MESSAGE_PATTERNS = [
    re.compile(r".*Messages and calls are end-to-end encrypted.*"),
    re.compile(r".*is a contact.*"),
    re.compile(r".*created group.*"),
    re.compile(r".*added.*"),
    re.compile(r".*left.*"),
    re.compile(r".*changed this group's icon.*"),
    re.compile(r".*changed the subject.*"),
    re.compile(r".*You're now an admin.*"),
]

def is_system_message(line: str) -> bool:
    """Checks if a line is a system message."""
    # First, check if it matches the standard message format. If it does, it's not a system message.
    if MESSAGE_REGEX.match(line):
        # Check for specific content often found in non-message lines but formatted like messages
        parts = MESSAGE_REGEX.match(line)
        if parts:
            content = parts.group(3).strip().lower()
            if content == "null" or content == "<media omitted>" or "<this message was edited>" in content:
                return True # Treat these as ignorable system-like messages

    # Check against explicit system message patterns for lines that DON'T match message format
    if not MESSAGE_REGEX.match(line): # Only apply these patterns if it's not a regular message
        for pattern in SYSTEM_MESSAGE_PATTERNS:
            if pattern.match(line):
                return True
    return False

def clean_message_text(text: str) -> str:
    """Cleans known artifacts from message text."""
    text = text.replace("<This message was edited>", "").strip()
    # Add any other cleaning rules if needed
    return text

def parse_chat_file_from_string(chat_content: str, target_friend_name: str) -> Tuple[List[str], Optional[str]]:
    """
    Parses chat content from a string to extract messages from the target friend
    and identify the other main participant (the user).
    This version is for testing with string input directly.
    """
    friend_messages: List[str] = []
    all_senders = set()
    parsed_messages: List[Dict[str, str]] = []
    current_message_sender = None
    current_message_content = []

    for line in chat_content.splitlines():
        line = line.strip()
        if not line:
            continue

        if is_system_message(line):
            if current_message_sender and current_message_content:
                full_message = " ".join(current_message_content)
                cleaned_message = clean_message_text(full_message)
                if cleaned_message:
                    parsed_messages.append({"sender": current_message_sender, "message": cleaned_message})
                current_message_sender = None
                current_message_content = []
            continue

        match = MESSAGE_REGEX.match(line)
        if match:
            if current_message_sender and current_message_content:
                full_message = " ".join(current_message_content)
                cleaned_message = clean_message_text(full_message)
                if cleaned_message:
                    parsed_messages.append({"sender": current_message_sender, "message": cleaned_message})
            
            _, sender, message_part = match.groups()
            sender = sender.strip()
            current_message_sender = sender
            current_message_content = [message_part.strip()]
            all_senders.add(sender)
        elif current_message_sender:
            current_message_content.append(line.strip())
    
    if current_message_sender and current_message_content:
        full_message = " ".join(current_message_content)
        cleaned_message = clean_message_text(full_message)
        if cleaned_message:
            parsed_messages.append({"sender": current_message_sender, "message": cleaned_message})

    for msg_data in parsed_messages:
        if msg_data["sender"].lower() == target_friend_name.lower():
            friend_messages.append(msg_data["message"])
    
    other_senders = [s for s in all_senders if s.lower() != target_friend_name.lower()]
    user_name = other_senders[0] if other_senders else None
    
    if not friend_messages:
        print(f"Warning (from string parse): No messages found for '{target_friend_name}'.")

    return friend_messages, user_name


def parse_chat_file(filepath: str, target_friend_name: str) -> Tuple[List[str], Optional[str]]:
    """
    Parses the chat file to extract messages from the target friend
    and identify the other main participant (the user).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            chat_content = f.read()
        return parse_chat_file_from_string(chat_content, target_friend_name)
    except FileNotFoundError:
        print(f"Error: Chat file not found at {filepath}")
        return [], None
    except Exception as e:
        print(f"Error parsing chat file: {e}")
        return [], None


if __name__ == '__main__':
    # Dummy chat content for self-testing the parser logic
    dummy_chat_content = """
23/01/01, 10:00 am - Messages and calls are end-to-end encrypted.
23/01/01, 10:00 am - Alice is a contact
23/01/01, 10:01 am - Alice: Hey Bob!
How are you doing today?
23/01/01, 10:02 am - Bob: Hi Alice!
I'm good, thanks for asking.
You?
23/01/01, 10:03 am - Alice: Doing great!
Just working on a fun project.
23/01/01, 10:03 am - Alice: <Media omitted>
23/01/01, 10:04 am - Bob: Oh cool! Tell me more. <This message was edited>
23/01/01, 10:05 am - Alice: It's about AI.
23/01/01, 10:05 am - System Message: Charles was added by Alice.
23/01/01, 10:06 am - Charles: Hey everyone!
23/01/01, 10:07 am - Alice: null
"""

    print("--- Testing parser with dummy chat data for 'Alice' ---")
    messages_alice, user_name_alice_partner = parse_chat_file_from_string(dummy_chat_content, "Alice")
    print(f"Found {len(messages_alice)} messages from Alice.")
    assert len(messages_alice) == 3, f"Expected 3 messages from Alice, got {len(messages_alice)}"
    expected_alice_messages = [
        "Hey Bob! How are you doing today?",
        "Doing great! Just working on a fun project.",
        "It's about AI."
    ]
    for i, msg in enumerate(messages_alice):
        print(f"  Alice Msg {i+1}: {msg}")
        assert msg == expected_alice_messages[i], f"Mismatch in Alice's message {i+1}"
    print(f"Inferred Alice's chat partner: {user_name_alice_partner}")
    assert user_name_alice_partner == "Bob", f"Expected Bob, got {user_name_alice_partner}"
    print("Alice test passed.")

    print("\n--- Testing parser with dummy chat data for 'Bob' ---")
    messages_bob, user_name_bob_partner = parse_chat_file_from_string(dummy_chat_content, "Bob")
    print(f"Found {len(messages_bob)} messages from Bob.")
    assert len(messages_bob) == 2, f"Expected 2 messages from Bob, got {len(messages_bob)}"
    expected_bob_messages = [
        "Hi Alice! I'm good, thanks for asking. You?",
        "Oh cool! Tell me more."
    ]
    for i, msg in enumerate(messages_bob):
        print(f"  Bob Msg {i+1}: {msg}")
        assert msg == expected_bob_messages[i], f"Mismatch in Bob's message {i+1}"
    print(f"Inferred Bob's chat partner: {user_name_bob_partner}")
    assert user_name_bob_partner == "Alice", f"Expected Alice, got {user_name_bob_partner}"
    print("Bob test passed.")
    
    print("\n--- Testing parser with dummy chat data for 'Charles' ---")
    messages_charles, user_name_charles_partner = parse_chat_file_from_string(dummy_chat_content, "Charles")
    print(f"Found {len(messages_charles)} messages from Charles.")
    assert len(messages_charles) == 1
    print(f"  Charles Msg 1: {messages_charles[0]}")
    assert messages_charles[0] == "Hey everyone!"
    # In a group chat context, inferring a single "partner" is ambiguous, so we might get Alice or Bob, or None depending on logic.
    # For this test, just checking messages is fine.
    print(f"Inferred Charles's chat partner(s) from remaining: {user_name_charles_partner}") # Will likely be Alice or Bob
    print("Charles test passed.")

    print("\nAll internal parser tests completed successfully.")