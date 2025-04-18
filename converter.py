import ast

def python_to_mermaid(code):
    try:
        tree = ast.parse(code)
        converter = MermaidFlowchartConverter()
        converter.visit(tree)
        return converter.generate()
    except Exception as e:
        return f"%% Error: {str(e)}"

class MermaidFlowchartConverter(ast.NodeVisitor):
    def __init__(self):
        self.lines = ["graph TD"]
        self.node_count = 0
        self.prev_node = None

    def add_node(self, label):
        node_name = f"N{self.node_count}"
        self.lines.append(f'{node_name}["{label}"]')
        if self.prev_node is not None:
            self.lines.append(f"{self.prev_node} --> {node_name}")
        self.prev_node = node_name
        self.node_count += 1
        return node_name

    def visit_Assign(self, node):
        code_line = f"{ast.unparse(node)}"
        self.add_node(code_line)

    def visit_Expr(self, node):
        self.add_node(ast.unparse(node))

    def visit_If(self, node):
        cond = f"If: {ast.unparse(node.test)}?"
        if_node = self.add_node(cond)
        true_branch = self.node_count
        self.prev_node = if_node
        for stmt in node.body:
            self.visit(stmt)
        true_end = self.prev_node

        self.prev_node = if_node
        false_start = self.node_count
        for stmt in node.orelse:
            self.visit(stmt)
        false_end = self.prev_node

        self.lines.append(f"{if_node} -- True --> N{true_branch}")
        self.lines.append(f"{if_node} -- False --> N{false_start}")

    def visit_While(self, node):
        cond = f"While: {ast.unparse(node.test)}?"
        loop_node = self.add_node(cond)
        self.prev_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.lines.append(f"{self.prev_node} --> {loop_node}")

    def visit_For(self, node):
        loop_var = node.target.id if isinstance(node.target, ast.Name) else "item"
        iter_code = f"for {loop_var} in {ast.unparse(node.iter)}"
        loop_node = self.add_node(iter_code)
        self.prev_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.lines.append(f"{self.prev_node} --> {loop_node}")

    def visit_FunctionDef(self, node):
        self.add_node(f"Function: {node.name}()")
        for stmt in node.body:
            self.visit(stmt)

    def visit_Return(self, node):
        self.add_node(f"Return {ast.unparse(node.value)}")

    def generate(self):
        return "\n".join(self.lines)
