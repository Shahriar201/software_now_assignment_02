import os
import re

# --- Tokenizer ---

def tokenize(text):
    """Converts a string into a list of tokens and validates characters."""
    # Pattern groups: 1. Numbers, 2. Operators/Parens, 3. Non-whitespace errors
    token_pattern = re.compile(r'(\d+\.?\d*)|([\+\-\*/\(\)])|(\S)')
    tokens = []
    
    for match in token_pattern.finditer(text):
        num, op_paren, error = match.groups()
        
        if error:
            raise ValueError(f"Invalid character: {error}")
        
        if num:
            tokens.append({'type': 'NUM', 'val': num})
        elif op_paren:
            if op_paren in '+-*/':
                tokens.append({'type': 'OP', 'val': op_paren})
            elif op_paren == '(':
                tokens.append({'type': 'LPAREN', 'val': op_paren})
            elif op_paren == ')':
                tokens.append({'type': 'RPAREN', 'val': op_paren})
    
    tokens.append({'type': 'END', 'val': '[END]'})
    return tokens

# --- Parser ---

def get_parser(tokens):
    """Recursive Descent Parser using closure for state management."""
    state = {'pos': 0}

    def peek():
        return tokens[state['pos']]

    def consume(expected_type=None):
        token = peek()
        if expected_type and token['type'] != expected_type:
            raise SyntaxError(f"Expected {expected_type}")
        state['pos'] += 1
        return token

    def parse_expression():
        """Level 1: Addition and Subtraction"""
        left_tree, left_val = parse_term()
        while peek()['val'] in ('+', '-'):
            op = consume()['val']
            right_tree, right_val = parse_term()
            left_tree = f"({op} {left_tree} {right_tree})"
            left_val = (left_val + right_val) if op == '+' else (left_val - right_val)
        return left_tree, left_val

    def parse_term():
        """Level 2: Multiplication, Division, and Implicit Multiplication"""
        left_tree, left_val = parse_factor()
        # Implicit multiplication occurs if a number/paren is followed by a number or '('
        while peek()['val'] in ('*', '/') or peek()['type'] in ('NUM', 'LPAREN'):
            if peek()['val'] in ('*', '/'):
                op = consume()['val']
            else:
                op = '*' # Implicit
            
            right_tree, right_val = parse_factor()
            
            if op == '/':
                if right_val == 0: raise ZeroDivisionError("Division by zero")
                left_val /= right_val
            else:
                left_val *= right_val
            left_tree = f"({op} {left_tree} {right_tree})"
        return left_tree, left_val

    def parse_factor():
        """Level 3: Unary negation"""
        if peek()['val'] == '-':
            consume()
            tree, val = parse_factor() 
            return f"(neg {tree})", -val
        elif peek()['val'] == '+':
            # Standard math allows unary +, we can just skip it
            consume()
            return parse_factor()
        return parse_primary()

    def parse_primary():
        """Level 4: Numbers and Parentheses"""
        token = peek()
        if token['type'] == 'NUM':
            consume()
            return token['val'], float(token['val'])
        elif token['type'] == 'LPAREN':
            consume('LPAREN')
            tree, val = parse_expression()
            consume('RPAREN')
            return tree, val
        else:
            raise SyntaxError(f"Unexpected token: {token['val']}")

    return parse_expression, peek

# --- Formatting ---

def format_result(val):
    if val == "ERROR": return "ERROR"
    # Convert to int if it's a whole number, else round to 4 decimals
    if isinstance(val, (int, float)):
        if val == int(val):
            return str(int(val))
        return f"{val:.4f}".rstrip('0').rstrip('.')
    return "ERROR"

def format_tokens(tokens):
    return " ".join([f"[{t['type']}:{t['val']}]" if t['type'] != 'END' else "[END]" for t in tokens])

# --- Main Logic ---

def evaluate_file(input_path: str) -> list[dict]:
    results = []
    output_lines = []
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return []

    with open(input_path, 'r') as f:
        # Filter out truly empty lines
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        entry = {"input": line, "tree": "ERROR", "tokens": "ERROR", "result": "ERROR"}
        try:
            # Step 1: Tokenize
            tokens = tokenize(line)
            entry["tokens"] = format_tokens(tokens)
            
            # Step 2: Parse and Evaluate
            parse_expr, peek_func = get_parser(tokens)
            tree, val = parse_expr()
            
            # Step 3: Check for trailing garbage
            if peek_func()['type'] != 'END':
                raise SyntaxError("Trailing tokens after expression")
            
            entry["tree"] = tree
            entry["result"] = val
        except Exception as e:
            # You can print(e) here for debugging purposes
            pass

        results.append(entry)
        
        # Build output format
        output_lines.append(f"Input: {entry['input']}")
        output_lines.append(f"Tree: {entry['tree']}")
        output_lines.append(f"Tokens: {entry['tokens']}")
        output_lines.append(f"Result: {format_result(entry['result'])}")
        output_lines.append("") 

    # Write output.txt
    output_path = os.path.join(os.path.dirname(input_path) or ".", "output.txt")
    with open(output_path, 'w') as f:
        f.write("\n".join(output_lines).strip() + "\n")

    print(f"Processed {len(results)} lines. Results saved to {output_path}")
    return results

if __name__ == "__main__":
    # Ensure sample_input.txt exists for testing
    if not os.path.exists("sample_input.txt"):
        with open("sample_input.txt", "w") as f:
            f.write("3 + 5 * (2 - 8)\n-5 - -5\n2(3 + 4)\n10 / 2.5\n@invalid")
            
    evaluate_file("sample_input.txt")