import os
import tempfile
import pandas as pd
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

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

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
pg_engine = create_engine(DATABASE_URL)
llm = get_llm()

def strip_sql_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith("```sql"):
        text = text[6:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    if text.startswith("SQLQuery:"):
        text = text[9:]
    return text.strip()

def create_isolated_db(shop_id: int) -> str:
    """Creates a temporary SQLite DB containing ONLY the specific shop's data."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    sqlite_url = f"sqlite:///{path}"
    sqlite_engine = create_engine(sqlite_url)
    
    from models.database import Base
    Base.metadata.create_all(sqlite_engine)
    
    tables = ["products", "sales", "inventory_transactions", "employees", "expenses"]
    
    with sqlite_engine.begin() as conn:
        # We also need the shop record for FK integrity
        shop_df = pd.read_sql(f"SELECT * FROM shops WHERE id = {shop_id}", pg_engine)
        if not shop_df.empty:
            shop_df.to_sql("shops", conn, if_exists="append", index=False)
            
        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table} WHERE shop_id = {shop_id}", pg_engine)
            if not df.empty:
                df.to_sql(table, conn, if_exists="append", index=False)
                
    return path

def ask_database(question: str, shop_id: int) -> dict:
    temp_db_path = None
    try:
        # Create an ephemeral isolated database
        temp_db_path = create_isolated_db(shop_id)
        isolated_db = SQLDatabase.from_uri(f"sqlite:///{temp_db_path}")
        
        generate_query_chain = create_sql_query_chain(llm, isolated_db)
        raw_sql_query = generate_query_chain.invoke({"question": question})
        sql_query = strip_sql_markdown(raw_sql_query)
        
        query_result = isolated_db.run(sql_query)
        
        answer_prompt = PromptTemplate.from_template(
            "Given the following user question, corresponding SQL query, and SQL result, answer the user question in a human-readable, conversational format.\n\n"
            "Question: {question}\n"
            "SQL Query: {query}\n"
            "SQL Result: {result}\n\n"
            "Answer: "
        )
        
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
                "response": "The AI Assistant is currently resting due to daily API rate limits. Try again tomorrow!",
                "answer": "The AI Assistant is currently resting due to daily API rate limits. Try again tomorrow!"
            }
        return {"error": error_msg}
    finally:
        # Ensure the temporary isolated DB is deleted
        if temp_db_path and os.path.exists(temp_db_path):
            os.remove(temp_db_path)
