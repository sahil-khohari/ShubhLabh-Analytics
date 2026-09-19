import os
import re
import tempfile
import pandas as pd
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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

def _create_isolated_ai_db(shop_id: int, db: Session) -> str:
    """
    Creates an isolated in-memory or temporary SQLite database 
    containing ONLY the data for the authenticated shop_id.
    """
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    
    sqlite_engine = create_engine(f"sqlite:///{temp_db_path}")
    
    # Tables to isolate for the AI
    tables_queries = {
        "shops": f"SELECT * FROM shops WHERE id = {shop_id}",
        "products": f"SELECT * FROM products WHERE shop_id = {shop_id}",
        "sales": f"SELECT * FROM sales WHERE shop_id = {shop_id}",
        "inventory_transactions": f"SELECT * FROM inventory_transactions WHERE shop_id = {shop_id}",
        "expenses": f"SELECT * FROM expenses WHERE shop_id = {shop_id}",
        "employees": f"SELECT * FROM employees WHERE shop_id = {shop_id}"
    }
    
    for table_name, query in tables_queries.items():
        try:
            df = pd.read_sql(query, db.bind)
            df.to_sql(table_name, sqlite_engine, index=False, if_exists="replace")
        except Exception as e:
            # Table might not exist or error in read
            print(f"Failed to isolate {table_name}: {e}")
            
    return temp_db_path

def ask_database(question: str, shop_id: int, db: Session) -> dict:
    """
    Takes a natural language question, generates SQL, executes it against an ISOLATED DB, 
    and returns a conversational explanation.
    """
    temp_db_path = ""
    try:
        temp_db_path = _create_isolated_ai_db(shop_id, db)
        temp_db_uri = f"sqlite:///{temp_db_path}"
        
        isolated_db = SQLDatabase.from_uri(temp_db_uri)
        
        # Create the initial Text-to-SQL chain
        generate_query_chain = create_sql_query_chain(llm, isolated_db)
        
        # Step 1: Generate SQL and strip markdown
        raw_sql_query = generate_query_chain.invoke({"question": question})
        sql_query = strip_sql_markdown(raw_sql_query)
        
        # Step 2: Execute SQL against the ISOLATED database
        query_result = isolated_db.run(sql_query)
        
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
    finally:
        # Cleanup temporary DB file
        if temp_db_path and os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except Exception:
                pass
