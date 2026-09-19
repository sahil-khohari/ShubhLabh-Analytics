import os
import re
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Initialize LLM based on available keys
def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            return ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0, google_api_key=api_key)
        except ImportError:
            raise Exception("langchain-google-genai is not installed")
    else:
        raise Exception("No API key found for OpenAI or Google/Gemini")

# Build the DB connection
# We reuse the same URL format from models/database.py
DATABASE_URL = "postgresql://retail_user:retail_password@localhost/retail_db"
db = SQLDatabase.from_uri(DATABASE_URL)

llm = get_llm()

def strip_sql_markdown(text: str) -> str:
    """Strips ```sql formatting and SQLQuery prefixes from LLM generated queries."""
    text = text.strip()
    
    # Remove markdown formatting
    if text.startswith("```sql"):
        text = text[6:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    text = text.strip()
    
    # Remove SQLQuery prefix if present (common with LangChain prompts)
    if text.startswith("SQLQuery:"):
        text = text[9:]
        
    return text.strip()

def ask_database(question: str) -> dict:
    """
    Takes a natural language question, generates SQL, executes it, 
    and returns a conversational explanation.
    """
    try:
        # Create the initial Text-to-SQL chain
        # The built-in create_sql_query_chain generates the SQL query
        generate_query_chain = create_sql_query_chain(llm, db)
        
        # Step 1: Generate SQL and strip markdown
        raw_sql_query = generate_query_chain.invoke({"question": question})
        sql_query = strip_sql_markdown(raw_sql_query)
        
        # Step 2: Execute SQL against the database
        # We manually execute it to capture the result robustly
        query_result = db.run(sql_query)
        
        # Step 3: Pass the result back to the LLM for a final conversational answer
        answer_prompt = PromptTemplate.from_template(
            "Given the following user question, corresponding SQL query, and SQL result, answer the user question in a human-readable, conversational format.\n\n"
            "Question: {question}\n"
            "SQL Query: {query}\n"
            "SQL Result: {result}\n\n"
            "Answer: "
        )
        
        # Create the final answer chain
        answer_chain = answer_prompt | llm | StrOutputParser()
        
        final_answer = answer_chain.invoke({
            "question": question,
            "query": sql_query,
            "result": query_result
        })
        
        return {
            "question": question,
            "generated_sql": sql_query,
            "sql_result": query_result,
            "answer": final_answer
        }
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
            return {
                "error": False,
                "response": "The AI Assistant is currently resting due to daily API rate limits, but your database is fully secure. Try again tomorrow or use the dashboard analytics!",
                "answer": "The AI Assistant is currently resting due to daily API rate limits, but your database is fully secure. Try again tomorrow or use the dashboard analytics!"
            }
        return {
            "error": error_msg
        }
