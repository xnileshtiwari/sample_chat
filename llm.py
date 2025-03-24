from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langsmith import Client, traceable
from dotenv import load_dotenv
from prompts import instructions

# Load environment variables
load_dotenv()

# Enable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "true"
custom_client = Client(api_key=os.environ["LANGSMITH_API_KEY"])

# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    verbose=True,
    api_key=os.environ["GOOGLE_API_KEY"],
)

@traceable(client=custom_client, run_type="llm", name="AI-CASE", project_name="Freelancer.com")
def get_completion(messages):
    """Generate a streaming response based on the conversation history."""
    try:
        # Format messages for the model: prepend system instructions and map roles
        formatted_messages = [("system", instructions)] + [
            ("human" if msg["role"] == "user" else "ai", msg["content"])
            for msg in messages
        ]
        
        # Return a generator for streaming response chunks
        def generate():
            for chunk in llm.stream(formatted_messages):
                yield chunk.content
        return generate()
    except Exception as e:
        print(f"An error occurred in llm.py: {str(e)}")
        # Return an error message as an iterator if streaming fails
        return iter([f"An error occurred: {str(e)}"])