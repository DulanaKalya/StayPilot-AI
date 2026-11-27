from src.services.chat_service import ChatService


def main():

    service = ChatService()

    print("StayPilot AI Chatbot")
    print("Type 'exit' to quit.\n")

    while True:

        message = input("You: ").strip()

        if message.lower() == "exit":
            break

        if not message:
            continue

        print("StayPilot AI: ", end="", flush=True)

        for chunk in service.stream(message):
            print(chunk, end="", flush=True)

        print("\n")


if __name__ == "__main__":
    main()