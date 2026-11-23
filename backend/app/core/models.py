from dotenv import load_dotenv

from langchain_google_genai import(
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    max_retries=3,
    timeout=60
)

embeddings = GoogleGenerativeAIEmbeddings(
    model = "gemini-embedding-001"
)