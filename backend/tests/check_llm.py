from time import perf_counter

from src.infrastructure.llm import get_llm


def main():

    llm = get_llm()

    start_time = perf_counter()

    response = llm.invoke(
        "Introduce yourself as StayPilot AI, "
        "a hotel concierge assistant for "
        "Azure Bay Resort in Negombo, Sri Lanka. "
        "Keep your response under three sentences."
    )

    elapsed_time = perf_counter() - start_time

    print("\n--- LLM RESPONSE ---")
    print(response.content)

    print("\n--- MODEL INFORMATION ---")
    print("Model:", response.response_metadata.get("model_name"))

    print("\n--- TOKEN USAGE ---")
    print(response.usage_metadata)

    print("\n--- RESPONSE TIME ---")
    print(f"{elapsed_time:.2f} seconds")

    print("\n--- CLIENT CACHE ---")
    print("Same instance:", llm is get_llm())

    print("\nLLM connection successful!")


if __name__ == "__main__":
    main()
