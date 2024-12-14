import os
import openai
from dotenv import load_dotenv
import janus_swi as janus
import logging

# Configure logging
logging.basicConfig(
    filename='baseline_experiment.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    logging.error("OpenAI API key not found. Please set it in the .env file.")
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

# Configure the OpenAI API client
openai.api_key = openai_api_key

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
        logging.info("Natural language processing obtained successfully.")
        return nlp_content
    except Exception as e:
        logging.error(f"Error communicating with OpenAI API for NLP: {e}")
        return None

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
                        "Provide only the Prolog code without any explanations or markdown formatting."
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
        logging.info("Prolog translation obtained successfully.")
        return prolog_code
    except Exception as e:
        logging.error(f"Error communicating with OpenAI API for Prolog translation: {e}")
        return None

def run_prolog_code_with_janus(prolog_code):
    """
    Executes the Prolog code using janus_swi by consulting it.
    """
    try:
        # Consult the Prolog code by providing an identifier and the code itself
        # The identifier can be any string; it's used for source tracking in Prolog
        janus.consult("translated_code", data=prolog_code)
        logging.info("Prolog code consulted successfully.")
        return True
    except janus.PrologError as e:
        logging.error(f"PrologError during consulting: {e}")
        return False
    except Exception as e:
        logging.error(f"Error consulting Prolog code with Janus: {e}")
        return False

def run_prolog_query_once(query, inputs={}):
    """
    Executes a deterministic Prolog query using janus.query_once().
    """
    try:
        result = janus.query_once(query, inputs, truth_vals=janus.PLAIN_TRUTHVALS)
        if result['truth'] is True:
            return result
        elif isinstance(result['truth'], janus.Undefined):
            logging.warning(f"Query '{query}' returned undefined.")
            return {'truth': 'Undefined'}
        else:
            return {'truth': False}
    except janus.PrologError as e:
        logging.error(f"PrologError during query '{query}': {e}")
        return {'truth': False}
    except Exception as e:
        logging.error(f"Error executing Prolog query '{query}': {e}")
        return {'truth': False}

def run_prolog_query_iterator(query, inputs={}):
    """
    Executes a non-deterministic Prolog query using janus.query().
    Returns a list of results.
    """
    results = []
    try:
        with janus.query(query, inputs) as q:
            for result in q:
                # Extract only the relevant variable bindings
                filtered_result = {k: v for k, v in result.items() if not k.startswith('_')}
                results.append(filtered_result)
        logging.info(f"Executed non-deterministic query: {query}")
    except janus.PrologError as e:
        logging.error(f"PrologError during query '{query}': {e}")
    except Exception as e:
        logging.error(f"Error executing Prolog query '{query}': {e}")
    return results

def main():
    # Prompt user for natural language input
    natural_language_input = input("Enter the natural language response to translate to Prolog:\n")

    nlp = get_nlp(natural_language_input)
    # Step 1: Translate to Prolog
    prolog_code = translate_to_prolog(nlp)

    if not prolog_code:
        print("Failed to obtain Prolog translation. Check logs for details.")
        return

    print("\nGenerated Prolog Code:\n")
    print(prolog_code)

    # Step 2: Run Prolog code using janus_swi by consulting it
    consult_success = run_prolog_code_with_janus(prolog_code)

    if consult_success:
        print("\nProlog code consulted successfully using Janus.")
        logging.info("Prolog code consulted successfully.")

        print("You can now enter Prolog queries. Type 'exit' to quit.")

        while True:
            user_query = input("\nEnter a Prolog query (terminated with a period): ")
            if user_query.lower() == 'exit':
                break
            if not user_query.endswith('.'):
                user_query += '.'

            # Determine if the query is deterministic or non-deterministic
            # For simplicity, we'll treat queries with variables as non-deterministic
            if any(char.isupper() for char in user_query):
                # Non-deterministic query
                results = run_prolog_query_iterator(user_query)
                if results:
                    for idx, result in enumerate(results, start=1):
                        print(f"Result {idx}: {result}")
                else:
                    print("No results found or query failed.")
            else:
                # Deterministic query
                result = run_prolog_query_once(user_query)
                if result['truth'] is True:
                    print("Result: True")
                elif result['truth'] == 'Undefined':
                    print("Result: Undefined")
                else:
                    print("Result: False")

        print("\nBaseline experiment completed successfully.")
        logging.info("Baseline experiment completed successfully.")
    else:
        print("Baseline experiment failed. Check logs for details.")
        logging.error("Baseline experiment failed.")

if __name__ == "__main__":
    main()
