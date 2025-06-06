import json
import os

def extract_code_from_notebook(notebook_path):
    """
    Extracts code from code cells of a Jupyter Notebook and saves it to a text file.

    Args:
        notebook_path (str): The full path to the input .ipynb notebook file.
    """
    # --- Configuration ---
    # Ensure the provided path exists
    if not os.path.exists(notebook_path):
        print(f"Error: The file '{notebook_path}' was not found.")
        return

    # Define the output file path by replacing the extension with '_code.txt'
    base_name = os.path.splitext(notebook_path)[0]
    output_path = f"{base_name}_code.txt"

    try:
        # Open and read the notebook file with UTF-8 encoding
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)

        # List to hold all the extracted code blocks
        extracted_code = []
        code_cell_counter = 1

        # Iterate through each cell in the notebook
        for cell in notebook_content['cells']:
            # Check if the cell is a code cell and not empty
            if cell['cell_type'] == 'code' and cell['source']:
                # Create the cell header comment
                header = f"#cell{code_cell_counter}"
                
                # The source is a list of strings (lines of code), join them
                source_code = "".join(cell['source'])
                
                # Add the header and the code to our list
                extracted_code.append(f"{header}\n{source_code}\n")
                
                # Increment the counter for the next code cell
                code_cell_counter += 1

        # Check if any code was extracted
        if not extracted_code:
            print(f"No code cells were found in '{notebook_path}'.")
            return

        # Write the extracted code to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            # Add a couple of newlines between each cell's code for readability
            f.write("\n".join(extracted_code))

        print(f"Successfully extracted code from {code_cell_counter - 1} cells.")
        print(f"Output saved to: {output_path}")

    except json.JSONDecodeError:
        print(f"Error: Could not parse '{notebook_path}'. It might not be a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Main execution block ---
if __name__ == "__main__":
    # SET THE PATH TO YOUR JUPYTER NOTEBOOK FILE HERE <<
    
    input_notebook_path = "C:/Users/User/PycharmProjects/Random/RandomML/BankTransFraudPred/modularized/run_pipeline.ipynb"
    
    # Call the function to perform the extraction
    extract_code_from_notebook(input_notebook_path)


