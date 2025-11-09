from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os

# Create a new chatbot instance
bot = ChatBot(
    'InteractiveBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter'
)

# Use a list of custom conversations to train the bot
trainer = ListTrainer(bot)
trainer.train([
    "Hello",
    "Hi there!",
    "How are you?",
    "I'm great! How can I help you today?",
    "What services do you offer?",
    "We provide custom chatbot development and AI consulting.",
    "Tell me a joke",
    "Why don't scientists trust atoms? Because they make up everything!",
    "Bye",
    "Goodbye! Have a great day."
])

# Interactive chat loop
print("Bot: Hi! I am your interactive bot. Type 'bye' to exit.")
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() == 'bye':
            print("Bot: Goodbye!")
            break

        response = bot.get_response(user_input)
        print(f"Bot: {response}")

    except (KeyboardInterrupt, EOFError, SystemExit):
        break
