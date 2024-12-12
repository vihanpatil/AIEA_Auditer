from pyswip import Prolog

def main():
    # Initialize the Prolog engine
    prolog = Prolog()

    # Path to your Prolog knowledge base file
    modern_family_kb = "mod_fam_kb.pl"

    # Consult the Prolog knowledge base file
    try:
        prolog.consult(modern_family_kb)
        print(f"Successfully loaded {modern_family_kb}")
    except Exception as e:
        print(f"Error loading {modern_family_kb}: {e}")
        return  # Exit if KB loading fails

    # Define a list of queries to execute
    queries = [
        # Modern Family Queries
        "female(gloria).",
        "male(joe).",
        "mother(gloria, joe).",
        "father(jay, joe).",
        "grandparent(jay, haley).",
        "son(david, mike).",
        "daughter(emily, mitchell).",
        "pet(stella, jay).",
        "pet(larry, mitchell).",
        "grandparent(mitchell, karen)."
    ]

    # Execute each query and print the result
    for query in queries:
        # Remove the trailing period for query execution
        stripped_query = query.strip().rstrip('.')
        try:
            # Execute the query
            result = list(prolog.query(stripped_query))
            if result:
                print(f"Query: {query} => True")
            else:
                print(f"Query: {query} => False")
        except Exception as e:
            print(f"Error executing query '{query}': {e}")

if __name__ == "__main__":
    main()
