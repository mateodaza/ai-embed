from flask import Flask, render_template, request
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
import environ

env = environ.Env()
environ.Env.read_env()

API_KEY = env('OPENAI_API_KEY')

# Setup database
db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://postgres:{env('DBPASS')}@localhost:5432/{env('DATABASE')}",
)
db._include_tables = ["project",  "user", "donation"]

# setup llm
llm = ChatOpenAI( model_name="gpt-4", max_tokens=1000 )
# Create db chain
QUERY = """
Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

{question}
"""

# Setup the database chain
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/get')
def get_prompt():
    prompt = request.args.get('msg')
    if prompt.lower() == 'exit':
        return 'Exiting...'
    else:
        try:
            question = QUERY.format(question=prompt)
            return db_chain.run(question)
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    app.run(debug=True)
