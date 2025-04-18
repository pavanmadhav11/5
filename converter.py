import ast

class MermaidFlowchartConverter(ast.NodeVisitor):
    def __init__(self):
        self.lines = ["graph TD"]
        self.node_count = 0
        self.prev_node = None

    def _get_node_id(self):
        self.node_count += 1
        return f"N{self.node_count}"

    def _add_line(self, line):
        self.lines.append(line)

    def _add_node(self, label):
        node_id = self._get_node_id()
        # Escape quotes inside label
        safe_label = label.replace('"', '\\"')
        self._add_line(f'{node_id}["{safe_label}"]')
        return node_id

    def _connect(self, from_node, to_node):
        self._add_line(f"{from_node} --> {to_node}")

    def generic_visit(self, node):
        try:
            super().generic_visit(node)
        except Exception as e:
            # Skip any node that causes an error
            pass

    def visit_FunctionDef(self, node):
        func_node = self._add_node(f"Function: {node.name}()")
        if self.prev_node:
            self._connect(self.prev_node, func_node)
        self.prev_node = func_node
        for stmt in node.body:
            self.visit(stmt)

    def visit_Assign(self, node):
        try:
            value = ast.unparse(node.value) if hasattr(ast, 'unparse') else "..."
            label = f"{ast.unparse(node.targets[0])} = {value}"
        except:
            label = "Assignment"
        assign_node = self._add_node(label)
        if self.prev_node:
            self._connect(self.prev_node, assign_node)
        self.prev_node = assign_node

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'print':
                label = "print()"
            else:
                try:
                    label = ast.unparse(node)
                except:
                    label = "Expression"
        else:
            label = "Expression"

        expr_node = self._add_node(label)
        if self.prev_node:
            self._connect(self.prev_node, expr_node)
        self.prev_node = expr_node

    def visit_If(self, node):
        cond_node = self._add_node(f"If: {ast.unparse(node.test) if hasattr(ast, 'unparse') else 'condition'}?")
        if self.prev_node:
            self._connect(self.prev_node, cond_node)

        self.prev_node = cond_node
        last_if_node = cond_node
        for stmt in node.body:
            self.visit(stmt)
        true_end = self.prev_node

        if node.orelse:
            self.prev_node = cond_node
            for stmt in node.orelse:
                self.visit(stmt)
            false_end = self.prev_node
        self.prev_node = true_end

    def visit_While(self, node):
        loop_node = self._add_node(f"While: {ast.unparse(node.test) if hasattr(ast, 'unparse') else 'loop'}?")
        if self.prev_node:
            self._connect(self.prev_node, loop_node)
        self.prev_node = loop_node
        body_start = self.prev_node
        for stmt in node.body:
            self.visit(stmt)
        self._connect(self.prev_node, body_start)

    def visit_For(self, node):
        try:
            loop_label = f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}"
        except:
            loop_label = "For loop"
        loop_node = self._add_node(loop_label)
        if self.prev_node:
            self._connect(self.prev_node, loop_node)
        self.prev_node = loop_node
        loop_start = self.prev_node
        for stmt in node.body:
            self.visit(stmt)
        self._connect(self.prev_node, loop_start)

    def visit_Call(self, node):
        label = "Function call"
        try:
            if isinstance(node.func, ast.Name):
                label = f"{node.func.id}()"
        except:
            pass
        call_node = self._add_node(label)
        if self.prev_node:
            self._connect(self.prev_node, call_node)
        self.prev_node = call_node

    def visit_Return(self, node):
        return_node = self._add_node("Return")
        if self.prev_node:
            self._connect(self.prev_node, return_node)
        self.prev_node = return_node

    def visit_AugAssign(self, node):
        try:
            label = f"{ast.unparse(node.target)} {ast.unparse(node.op)}= {ast.unparse(node.value)}"
        except:
            label = "Augmented Assignment"
        aug_node = self._add_node(label)
        if self.prev_node:
            self._connect(self.prev_node, aug_node)
        self.prev_node = aug_node

    def generate(self):
        return "\n".join(self.lines)

def python_to_mermaid(code):
    try:
        tree = ast.parse(code)
        converter = MermaidFlowchartConverter()
        converter.visit(tree)
        return converter.generate()
    except Exception as e:
        # Fallback safe output
        return "graph TD\nA[\"Error in code parsing\"]"
