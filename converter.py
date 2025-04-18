import ast

def python_to_mermaid(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "flowchart TD\nerror[Syntax Error in code]"

    mermaid = ["flowchart TD"]
    node_counter = [0]
    edges = []

    def add_node(label):
        node_name = f"N{node_counter[0]}"
        label = label.replace('"', "'")
        mermaid.append(f'{node_name}["{label}"]')
        node_counter[0] += 1
        return node_name

    def visit_node(node, prev=None):
        if isinstance(node, ast.FunctionDef):
            cur = add_node(f"Function: {node.name}")
        elif isinstance(node, ast.If):
            cond = ast.unparse(node.test)
            cur = add_node(f"If: {cond}?")
            for stmt in node.body:
                body_node = visit_node(stmt, cur)
                edges.append((cur, body_node, "True"))
            for stmt in node.orelse:
                else_node = visit_node(stmt, cur)
                edges.append((cur, else_node, "False"))
            return cur
        elif isinstance(node, ast.While):
            cond = ast.unparse(node.test)
            cur = add_node(f"While: {cond}")
            for stmt in node.body:
                loop = visit_node(stmt, cur)
                edges.append((loop, cur, "Loop"))
        elif isinstance(node, ast.Assign):
            cur = add_node(ast.unparse(node))
        elif isinstance(node, ast.Expr):
            cur = add_node(ast.unparse(node))
        elif isinstance(node, ast.Return):
            cur = add_node(f"Return: {ast.unparse(node.value)}")
        else:
            cur = add_node(type(node).__name__)
        
        if prev:
            edges.append((prev, cur, ""))
        return cur

    for stmt in tree.body:
        visit_node(stmt)

    for from_node, to_node, label in edges:
        if label:
            mermaid.append(f"{from_node} -->|{label}| {to_node}")
        else:
            mermaid.append(f"{from_node} --> {to_node}")

    return "\n".join(mermaid)
