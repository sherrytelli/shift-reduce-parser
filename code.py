import sys
import os
from tabulate import tabulate  # Import the tabulate library

# Data Structure for the Parse Tree
class ParseTreeNode:
    """A node for constructing the parse tree."""
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children is not None else []
        self.parent = None
        if self.children:
            for child in self.children:
                child.parent = self

# ---------------------------------------------------------------------------
# The Shift-Reduce Parser Class
# ---------------------------------------------------------------------------
class ShiftReduceParser:
    """
    A class that encapsulates the entire Shift-Reduce parsing process.
    """
    def __init__(self, grammar_filename):
        """Initializes the parser by loading the grammar."""
        self.grammar = {}
        self.grammar_reverse_lookup = {}
        self.start_symbol = ''
        self._load_grammar(grammar_filename)
        
        # State variables for a specific parse run
        self.parsing_stack = []
        self.node_stack = []
        self.input_buffer = []
        self.parsing_table_rows = []

    def _load_grammar(self, filename):
        """(Internal) Reads and processes grammar rules from a file."""
        try:
            with open(filename, 'r') as f:
                first_line = True
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('->')
                    if len(parts) != 2:
                        print(f"Skipping malformed line: {line}")
                        continue
                    
                    lhs = parts[0].strip()
                    rhs_productions = parts[1].strip().split('|')
                    
                    if first_line:
                        self.start_symbol = lhs
                        first_line = False
                        
                    if lhs not in self.grammar:
                        self.grammar[lhs] = []
                    
                    for prod_str in rhs_productions:
                        symbols = tuple(prod_str.strip().split())
                        if symbols == ('',):
                            symbols = () # Epsilon
                            
                        self.grammar[lhs].append(symbols)
                        
                        if symbols in self.grammar_reverse_lookup:
                            self.grammar_reverse_lookup[symbols].append(lhs)
                        else:
                            self.grammar_reverse_lookup[symbols] = [lhs]
            
            print("--- 1. Grammar Rules Read ---")
            print(f"Start Symbol: {self.start_symbol}")
            for lhs, rhs_list in self.grammar.items():
                for rhs_tuple in rhs_list:
                    print(f"{lhs} -> {' '.join(rhs_tuple) or 'ε'}")
            print("-" * 30)
            
        except FileNotFoundError:
            print(f"Error: Grammar file '{filename}' not found.")
            sys.exit(1)

    def _shift(self, input_symbol):
        """(Internal) Performs the shift action."""
        self.parsing_stack.append(input_symbol)
        self.node_stack.append(ParseTreeNode(input_symbol))
        self.input_buffer.pop(0)

    def _reduce(self, lhs, rhs_symbols):
        """(Internal) Performs the reduce action."""
        # Update parsing stack
        for _ in range(len(rhs_symbols)):
            if self.parsing_stack: self.parsing_stack.pop()
        self.parsing_stack.append(lhs)
        
        # Update node stack to build the tree
        child_nodes = []
        for _ in range(len(rhs_symbols)):
            if self.node_stack: child_nodes.append(self.node_stack.pop())
        child_nodes.reverse()
        
        parent_node = ParseTreeNode(lhs, children=child_nodes)
        self.node_stack.append(parent_node)

    def parse(self, input_string):
        """
        Parses a given input string according to the loaded grammar.
        Returns the final status and the root of the parse tree.
        """
        # 1. Reset state for the new run
        self.input_buffer = input_string.strip().split() + ['$']
        self.parsing_stack = ['$']
        self.node_stack = []
        self.parsing_table_rows = []
        step = 1

        while True:
            stack_str = " ".join(self.parsing_stack)
            input_str = " ".join(self.input_buffer)
            # Row format: [Step, Stack, Input, Action, Rule]
            current_row = [str(step), stack_str, input_str, "", ""]

            # 2. Find all possible reductions
            potential_reductions = []
            temp_suffix = []
            for i in range(len(self.parsing_stack) - 1, 0, -1):
                temp_suffix.insert(0, self.parsing_stack[i])
                suffix_tuple = tuple(temp_suffix)
                if suffix_tuple in self.grammar_reverse_lookup:
                    for lhs in self.grammar_reverse_lookup[suffix_tuple]:
                        potential_reductions.append((lhs, suffix_tuple))

            # 3. Decision logic
            can_shift = len(self.input_buffer) > 0 and self.input_buffer[0] != '$'

            if not potential_reductions:
                if can_shift: # Must shift
                    symbol_to_shift = self.input_buffer[0]
                    current_row[3:5] = ["Shift", f"Shift {symbol_to_shift}"]
                    self.parsing_table_rows.append(current_row)
                    self._shift(symbol_to_shift)
                else: # Check for accept or reject
                    if stack_str == f"$ {self.start_symbol}" and input_str == "$":
                        current_row[3] = "Accept"
                        self.parsing_table_rows.append(current_row)
                        # Return the single node left on the stack
                        return "Accepted", self.node_stack[0]
                    else:
                        current_row[3] = "Reject (Error)"
                        self.parsing_table_rows.append(current_row)
                        return "Rejected (Invalid State)", None
            else:
                # Policy: Prefer the longest possible reduction
                max_len = max(len(rhs) for _, rhs in potential_reductions)
                longest_reductions = [r for r in potential_reductions if len(r[1]) == max_len]

                if len(longest_reductions) > 1: # Reduce-Reduce Conflict
                    rules = ", ".join([f"{l}->{' '.join(r)}" for l, r in longest_reductions])
                    current_row[3:5] = ["Reduce-Reduce Conflict", f"Rules: [{rules}]"]
                    self.parsing_table_rows.append(current_row)
                    return "Rejected (Conflict)", None

                # Perform the reduction
                lhs, rhs_symbols = longest_reductions[0]
                action = "Reduce"
                rule_str = f"{lhs} -> {' '.join(rhs_symbols) or 'ε'}"

                if can_shift: # Shift-Reduce Conflict (resolved by reducing)
                    action = "Reduce (S/R Conflict)"
                    rule_str += " (Prefer Reduce)"
                
                current_row[3:5] = [action, rule_str]
                self.parsing_table_rows.append(current_row)
                self._reduce(lhs, rhs_symbols)

            step += 1
            if step > 100: # Safety break
                current_row[3:5] = ["Reject (Loop Limit)", "Over 100 steps"]
                self.parsing_table_rows.append(current_row)
                return "Rejected (Loop Limit)", None

    def _print_tree_recursive(self, node, prefix):
        """Internal recursive helper for printing the tree."""
        children = node.children
        num_children = len(children)
        
        for i, child in enumerate(children):
            # Check if this is the last child
            is_last = (i == num_children - 1)
            
            # Connector for this child
            connector = "└── " if is_last else "├── "
            
            # Print the child's line. Use repr() to keep quotes around terminals
            print(f"{prefix}{connector}{repr(child.value)}")
            
            # Calculate the prefix for its children
            # If last child, prefix is blank. If not, it's a vertical bar.
            child_prefix = "    " if is_last else "│   "
            
            # Recurse
            self._print_tree_recursive(child, prefix + child_prefix)

    def print_parse_tree(self, root_node):
        """Prints the final parse tree in a structured format."""
        print("\n--- 4. Parse Tree ---")
        if not root_node:
            print("No parse tree generated.")
            return
        
        # Print the root node
        # We use repr() to be consistent and show 'E' instead of E
        print(f"└── {repr(root_node.value)}")
        
        # Start the recursion for its children with an empty prefix
        self._print_tree_recursive(root_node, "    ")

    def display_results(self, status, parse_tree):
        """Prints the final parsing table, result, and parse tree."""
        # Print Table using tabulate
        print("\n--- 2. Shift-Reduce Parsing Table ---")
        if not self.parsing_table_rows:
            print("No parsing steps were taken.")
        else:
            headers = ['Step', 'Stack', 'Input String', 'Action', 'Associative Rule']
            print(tabulate(self.parsing_table_rows, headers=headers, tablefmt="grid"))

        # Print Final Result
        print("\n--- 3. Final Result ---")
        print(f"Parsing Status: {status}")

        # Print Parse Tree (UPDATED)
        self.print_parse_tree(parse_tree)

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
def main():
    """Main function to create and run the parser."""
    grammar_filename = "grammar.txt"
    
    # 1. Instantiate the parser with the grammar file
    parser = ShiftReduceParser(grammar_filename)
    
    # 2. Get user input
    print("NOTE: Please enter your string with spaces between tokens.")
    print("Example: id * id + id")
    input_str = input("Enter input string: ")
    
    # 3. Run the parsing process
    status, tree = parser.parse(input_str)
    
    # 4. Display all results
    parser.display_results(status, tree)

if __name__ == "__main__":
    main()