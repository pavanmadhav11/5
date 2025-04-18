import ast

class MermaidFlowchartConverter(ast.NodeVisitor):
    def __init__(self):
        self.lines = ["graph TD"]
        self.node_count = 0
        self.prev_node = None

    def add_node(self, label):
        label = self.clean_label(label)
        node_name = f"N{self.node_count}"
        self.lines.append(f'{node_name}["{label}"]')
        if self.prev_node is not None:
            self.lines.append(f"{self.prev_node} --> {node_name}")
        self.prev_node = node_name
        self.node_count += 1
        return node_name

    def clean_label(self, label):
        label = label.strip()
        if label.startswith("print("):
            return "print()"
        elif label.startswith("input("):
            return "input()"
        return label.replace('"', "'").replace("\\n", " ")

    def visit_FunctionDef(self, node):
        self.add_node(f"Function: {node.name}()")
        for stmt in node.body:
            self.visit(stmt)

    def visit_If(self, node):
        cond = f"If: {ast.unparse(node.test)}?"
        if_node = self.add_node(cond)

        true_branch_start = self.node_count
        self.prev_node = if_node
        for stmt in node.body:
            self.visit(stmt)
        true_end = self.prev_node

        if node.orelse:
            false_branch_start = self.node_count
            self.prev_node = if_node
            for stmt in node.orelse:
                self.visit(stmt)
            false_end = self.prev_node
            self.lines.append(f"{if_node} -- False --> N{false_branch_start}")
        self.lines.append(f"{if_node} -- True --> N{true_branch_start}")

    def visit_For(self, node):
        loop_node = self.add_node(f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}")
        self.prev_node = loop_node
        body_start = self.node_count
        for stmt in node.body:
            self.visit(stmt)
        self.lines.append(f"{self.prev_node} --> {loop_node}")

    def visit_While(self, node):
        loop_node = self.add_node(f"While: {ast.unparse(node.test)}?")
        self.prev_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.lines.append(f"{self.prev_node} --> {loop_node}")

    def visit_Expr(self, node):
        self.add_node(self.clean_label(ast.unparse(node)))

    def visit_Assign(self, node):
        self.add_node(ast.unparse(node))

    def visit_AugAssign(self, node):
        self.add_node(ast.unparse(node))

    def visit_Return(self, node):
        self.add_node(f"Return {ast.unparse(node.value)}")

    def visit_Call(self, node):
        self.add_node(ast.unparse(node))

    def generate(self):
        return "\n".join(self.lines)


def python_to_mermaid(code):
    try:
        tree = ast.parse(code)
        converter = MermaidFlowchartConverter()
        converter.visit(tree)
        return converter.generate()
    except Exception as e:
        return f"%% Error: {str(e)}"
