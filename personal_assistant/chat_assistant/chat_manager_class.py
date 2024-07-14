# chat_manager.py

class ChatManager:
    def __init__(self):
        self.chat_history = []
        self.user_name = "You"  # Default user name

    def add_message(self, user_query, bot_response):
        self.chat_history.append({'user': user_query, 'bot': bot_response})

    def clear_history(self):
        self.chat_history = []

    def restart_session(self):
        self.chat_history = []
        self.user_name = "You"  # Reset to default user name

    def get_chat_history(self):
        return self.chat_history

    def get_user_name(self):
        return self.user_name

    def set_user_name(self, user_name):
        self.user_name = user_name
    
    def print_chat_history(self):
        for chat in self.chat_history:
            print(f"User: {chat['user']}")
            print(f"Bot: {chat['bot']}")
            print("\n")

# Instantiate the ChatManager
chat_manager = ChatManager()
