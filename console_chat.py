import requests

def console_chat():
    client_name = input("Enter your name: ")
    chat_id = "console-chat"
    while True:
        message = input("You: ")
        if message.lower() in ['exit', 'quit']:
            break
        response = requests.post('http://127.0.0.1:8000/chat', json={'message': {'content': message, 'id': chat_id}})
        print(f"Agent: {response.json()['message']['content']}")

if __name__ == '__main__':
    console_chat()