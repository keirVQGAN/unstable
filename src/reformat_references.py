from src.utils.sys_utils import read_excel, read_docx, read_txt, write_docx, write_txt_or_csv, write_xlsx

def reformat_references(bot, model, references_path, citation_styles, output_type='txt'):
    # Set the model
    bot.model = model

    # Map file extensions to their corresponding file reading functions
    file_readers = {'.xlsx': read_excel, '.docx': read_docx, '.txt': read_txt}

    # Get the file extension
    _, ext = os.path.splitext(references_path)

    # Read the references from the file
    references = file_readers.get(ext)(references_path)

    # Join the references into a single text
    references_text = '\n'.join(references)

    # Get the base name for the output files
    output_base = os.path.splitext(os.path.basename(references_path))[0]

    # Map output types to their corresponding file writing functions
    file_writers = {'docx': write_docx, 'txt': write_txt_or_csv, 'csv': write_txt_or_csv, 'xlsx': write_xlsx}

    # For each citation style
    for style in citation_styles:
        # Ask the chatbot to rewrite the references in the citation style
        reformatted_refs = bot.chat(f"Please rewrite the following references in {style} style: {references_text}")

        # Get the output file path
        output_path = f"{output_base}_{style}.{output_type}"

        # Write the reformatted references to the output file
        file_writers.get(output_type)(output_path, reformatted_refs)

        print(f'Reformatted references in {style} style have been written to {output_path}.')
