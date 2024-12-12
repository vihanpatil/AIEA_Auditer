import openai
from pyswip import Prolog
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


# PROBLEM FORMULATOR, page 3
# # Uses LLMs to translate NLP into symbolic representaion
def get_nlp(natural_language_input):
    """
    Sends a request to the OpenAI API to process the natural language input.
    This step is optional and depends on your specific use case.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"{natural_language_input}"
                }
            ],
            temperature=0  # Set to 0 for deterministic output
        )
        nlp_content = response.choices[0].message.content
        #logging.info("Natural language processing obtained successfully.")
        return nlp_content
    except Exception as e:
        #logging.error(f"Error communicating with OpenAI API for NLP: {e}")
        return None

# Part of PROBLEM FORMULATOR
def translate_to_prolog(natural_language_input):
    """
    Sends a request to the OpenAI API to translate natural language input into Prolog code.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Replace with your accessible model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Prolog expert. "
                        "Translate the following natural language descriptions into Prolog code. "
                        "Provide only the Prolog code without any explanations or markdown formatting. NO EXPLANATIONS, COMMENTS, or FORMATTING!"
                        "Please also give a few sample queries after the facts for a few tests against the knowledge base. NO EXPLANATIONS, COMMENTS, or FORMATTING for these either!"
                    )
                },
                {
                    "role": "user",
                    "content": f"Translate the following response to Prolog:\n\n{natural_language_input}"
                }
            ],
            temperature=0  # Set to 0 for deterministic output
        )
        prolog_code = response.choices[0].message.content.strip()
        #logging.info("Prolog translation obtained successfully.")
        return prolog_code
    except Exception as e:
        #logging.error(f"Error communicating with OpenAI API for Prolog translation: {e}")
        return None

# SYMBOLIC REASONER, page 4
# #  
def execute_prolog_code(prolog_code):
    prolog = Prolog()
    try:
        # Initialize lists for clauses and queries
        clauses = []
        queries = []
        current_clause = ''
        in_clause = False

        # Process each line
        lines = prolog_code.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):
                continue  # Skip empty lines and comments
            elif line.startswith('?-'):
                # This is a query
                query = line[2:].strip()
                if query.endswith('.'):
                    query = query[:-1].strip()  # Remove trailing period
                queries.append(query)
            else:
                # Accumulate clauses
                if line.endswith('.'):
                    # End of clause
                    current_clause += ' ' + line[:-1].strip()
                    clauses.append(current_clause.strip())
                    current_clause = ''
                else:
                    # Continue accumulating clause
                    current_clause += ' ' + line.strip()

        print("Clauses to assert:")
        print(clauses)
        print("Queries to execute:")
        print(queries)

        # Load each clause into Prolog
        for clause in clauses:
            print(f"Asserting clause: {clause}")
            prolog.assertz(clause)

        # Execute each query
        results = []
        for query in queries:
            print(f"Executing query: {query}")
            result = list(prolog.query(query))
            results.append((query, result))

        return results, None
    except Exception as e:
        return None, str(e)




# SELF REFINER, page 4
# # Modifies innacurate logical formulations using error message with LLM to refine
def self_refine_prolog_code(question, prolog_code, error_message):
    response = openai.chat.completions.create(
        model='gpt-4o-mini',  # or 'gpt-4' if you have access
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that refines Prolog code based on an error message from the Prolog interpreter. NO EXPLANATIONS, COMMENTS, or FORMATTING! ONLY RETURNT THE REFINED PROLOG CODE."
            },
            {
                "role": "user",
                "content": f"""
                  Original Problem:
                  {question}

                  Original Prolog code:
                  {prolog_code}

                  Error message from Prolog:
                  {error_message}

                  Please correct the Prolog code based on the error message.

                  Refined Prolog code:
                """
            }
        ],
        temperature=0,
    )
    refined_prolog_code = response.choices[0].message.content.strip()
    return refined_prolog_code

# RESULT INTERPRETER, page 5
# # Translates results from symbolic solver to natural language answer
def interpret_result(result):
    # Interpret the Prolog result and convert it into a natural language answer
    # This will depend on the structure of your Prolog query and expected results
    if result:
        answer = "Yes, the statement is true."
    else:
        answer = "No, the statement is false."
    return answer


def extract_query(prolog_code):
    # Extract the query from the Prolog code
    # For simplicity, let's assume the query is in the last line starting with '?-'
    lines = prolog_code.strip().split('\n')
    for line in reversed(lines):
        line = line.strip()
        if line.startswith('?-'):
            query = line[2:].strip()
            return query
    return None

def main():
    question = input("Please enter your logical reasoning question:\n")
    max_iterations = 3
    iteration = 0
    natural_lang = get_nlp(question)
    prolog_code = translate_to_prolog(natural_lang)
    
    while iteration < max_iterations:
        results, error = execute_prolog_code(prolog_code)
        if error:
            print(f"Error executing Prolog code:\n{error}")
            prolog_code = self_refine_prolog_code(question, prolog_code, error)
            iteration += 1
            time.sleep(1)  # To comply with API rate limits
        else:
            break

    if results is not None:
        for query, result in results:
            answer = interpret_result(result)
            print(f"\nQuery: {query}")
            print(f"Answer: {answer}")
    else:
        print("Sorry, I couldn't determine the answer.")

if __name__ == "__main__":
    main()
