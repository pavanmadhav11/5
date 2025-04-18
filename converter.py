import ast
import html

def sanitize_label(label):
    return html.escape(label.replace('"', "'"))

def python_to_mermaid(code):
    try:
        tree = ast.parse(code)
        converter = MermaidFlowchartConverter()
        converter.visit(tree)
        output = converter.generate()
        if "graph TD" not in output or len(output.strip()) < 10:
            return "%% Error: Invalid Mermaid flowchart generated"
        return output
    except Exception as e:
        return f"%% Error: {str(e)}"

class MermaidFlowchartConverter(ast.NodeVisitor):
    def __init__(self):
        self.lines = ["graph TD"]
        self.node_count = 0
        self.prev_node = None
        self.stack = []

    def add_node(self, label):
        safe_label = sanitize_label(label)
        node_name = f"N{self.node_count}"
        self.lines.append(f'{node_name}["{safe_label}"]')
        if self.prev_node is not None:
            self.lines.append(f"{self.prev_node} --> {node_name}")
        self.prev_node = node_name
        self.node_count += 1
        return node_name

    def visit_Assign(self, node):
        self.add_node(ast.unparse(node))

    def visit_Expr(self, node):
        self.add_node(ast.unparse(node))

    def visit_If(self, node):
        cond = f"If: {ast.unparse(node.test)}?"
        if_node = self.add_node(cond)

        # Save previous node
        original_prev = self.prev_node

        # True branch
        self.lines.append(f"{if_node} -- True --> N{self.node_count}")
        self.prev_node = if_node
        for stmt in node.body:
            self.visit(stmt)
        true_end = self.prev_node

        # False branch
        if node.orelse:
            self.lines.append(f"{if_node} -- False --> N{self.node_count}")
            self.prev_node = if_node
            for stmt in node.orelse:
                self.visit(stmt)
            false_end = self.prev_node
        else:
            false_end = if_node

        # Reconnect flow
        self.prev_node = if_node  # Allow next node to link from if-node or both branches

    def visit_While(self, node):
        loop_cond = f"While: {ast.unparse(node.test)}?"
        loop_node = self.add_node(loop_cond)

        start_node = self.node_count
        self.lines.append(f"{loop_node} -- True --> N{start_node}")
        self.prev_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.lines.append(f"{self.prev_node} --> {loop_node}")  # Loop back

        # False condition exit
        self.lines.append(f"{loop_node} -- False --> N{self.node_count}")
        self.prev_node = loop_node  # Continue from here after loop

    def visit_For(self, node):
        loop_label = f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}"
        loop_node = self.add_node(loop_label)

        start_node = self.node_count
        self.lines.append(f"{loop_node} --> N{start_node}")
        self.prev_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.lines.append(f"{self.prev_node} --> {loop_node}")  # Loop back

        self.lines.append(f"{loop_node} --> N{self.node_count}")  # Exit after loop
        self.prev_node = loop_node

    def visit_FunctionDef(self, node):
        self.add_node(f"Function: {node.name}()")
        for stmt in node.body:
            self.visit(stmt)

    def visit_Return(self, node):
        self.add_node(f"Return {ast.unparse(node.value)}")

    def generate(self):
        return "\n".join(self.lines)
