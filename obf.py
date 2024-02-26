import re
import random
import string

def whitespace_remover(a):
    """
    Function to remove all whitespace, except for after functions, variables, and imports
    """
    splits = re.split('\"',a)
    code_string = "((\w+\s+)[a-zA-Z_*][|a-zA-Z0-9_]*|#.*|return [a-zA-Z0-9_]*| [[.].]|else)"
    index = 0
    a = ""
    for s in splits:
            # If its not the contents of a string, remove spaces of everything but code
            if(index%2==0):                
              s_spaceless = re.sub("[\s]", "", s)          # Create a spaceless version of s
              s_code = re.findall(code_string,s)           # find all spaced code blocks in s

              for code in s_code:
               old = re.sub("[\s]", "", code[0])
               new = code[0]

               if(code[0][0] == '#'):
                 new = code[0] + "\n"                      # Adding a newline for preprocesser commands
               elif("unsigned" in code[0] or "else" in code[0]):
                 new = code[0] + " "
               s_spaceless = s_spaceless.replace(old,new) # Replace the spaceless code blocks in s with their spaced equivilents                
            else:
              s_spaceless = s

            if(index >= 1):
             a = a + "\"" + s_spaceless
            else:
             a = a + s_spaceless
            index+=1
    return a

def find_cpp_functions(content):
    # Use regular expression to find all function declarations
    function_declarations = re.finditer(r'\b\w+\s+(\w+)\s*\(.*\)\s*{', content)
    function_names = [match.group(1) for match in function_declarations]
    return function_names

def find_cpp_variables(content):
    # Use regular expression to find all variable declarations
    variable_declarations = re.finditer(r'\b((?:int|bool|float|POINT|RECT|double|long|HWND|HDC|HINSTANCE|LPSTR|HICON|HBRUSH|HMENU|INPUT|COLORREF|int8_t|uint8_t|int16_t|uint16_t|int32_t|uint32_t|int64_t|uint64_t|short|unsigned|char|std::string|std::vector|std::map|std::pair|std::tuple|std::unordered_map)\s+([a-zA-Z_]\w*)\s*(?:=[^;]*)?;)', content)

    # Store variable names and declarations in a list
    variable_info = [(match.group(2), match.group(1)) for match in variable_declarations]

    return variable_info

def insert_junk_variables(content):
    # Insert junk strings and int variables after every semicolon
    content_with_junk = re.sub(
        r';', 
        lambda x: ';\n    const char* s' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8)) + ';\n    int i' + str(random.randint(1, 100)) + ';', 
        content
    )
    return content_with_junk

def remove_comments_and_replace_variables(file_path, excluded_functions=None):
    with open(file_path, 'r') as file:
        content = file.read()

    # Remove single-line comments
    content = re.sub(r'//.*', '', content)

    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # Insert junk variables
    content = insert_junk_variables(content)

    variable_info = find_cpp_variables(content)

    # Generate random strings for each variable
    random_variable_names = [''.join(random.choice(string.ascii_letters) for _ in range(8)) for _ in range(len(variable_info))]

    # Replace variable names with random strings and print the original and replaced declarations
    for (original_name, declaration), new in zip(variable_info, random_variable_names):
        replaced_declaration = re.sub(r'\b' + re.escape(original_name) + r'\b', new, declaration)
        print(f"{declaration.strip()} -> {replaced_declaration.strip()}")
        content = re.sub(r'\b' + re.escape(original_name) + r'\b', new, content)

    # Replace function names with random strings
    function_names = find_cpp_functions(content)

    if excluded_functions:
        function_names = [func for func in function_names if func not in excluded_functions]

    random_function_names = [''.join(random.choice(string.ascii_letters) for _ in range(8)) for _ in range(len(function_names))]

    content = whitespace_remover(content)

    # Replace function names with random strings and print the original and replaced function names
    for old, new in zip(function_names, random_function_names):
        print(f"{old} -> {new}")
        content = re.sub(r'\b' + re.escape(old) + r'\b', new, content)

    with open(file_path, 'w') as file:
        file.write(content)

file_path = "Input.cpp"
excluded_functions = ["main", "WinMain", "WinMainCRTStartup", "wWinMain", "wWinMainCRTStartup", "wmain", "mainCRTStartup", "wmainCRTStartup", "WinMainWOW", "WinMainWOW64"]  # Add functions you want to exclude here
remove_comments_and_replace_variables(file_path, excluded_functions)
print("Comments removed, variables replaced with random strings, and junk variables inserted in the file.")
