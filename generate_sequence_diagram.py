import ast
import os
import argparse


class SequenceDiagramGenerator(ast.NodeVisitor):
    def __init__(self):
        self.diagram = '@startuml\nactor User\nparticipant "Main" as Main\n'
        self.current_function = None
        self.called_classes = {}
        self.sequence_steps = []
        self.instances = {}

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None

    def visit_ClassDef(self, node):
        class_name = node.name
        self.called_classes[class_name] = (
            f'participant "{class_name}" as {class_name.lower()}\n'
        )
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    instance_name = target.id
                    class_name = self._get_class_name_from_call(node.value)
                    if class_name:
                        self.instances[instance_name] = class_name
                        self.process_function_call(node.value, instance_name)
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.process_function_call(node.value)
        self.generic_visit(node)

    def process_function_call(self, call_node, instance_name=None):
        func_name = self._get_func_name(call_node)
        if func_name:
            if isinstance(call_node.func, ast.Attribute):
                obj_name = call_node.func.value
                if isinstance(obj_name, ast.Name) and obj_name.id in self.instances:
                    class_name = self.instances[obj_name.id]
                    if class_name not in self.called_classes:
                        self.called_classes[class_name] = (
                            f'participant "{class_name}" as {class_name.lower()}\n'
                        )
                    step = f"Main -> {class_name.lower()}: {func_name}()\n"
                    if step not in self.sequence_steps:
                        self.sequence_steps.append(step)
            else:
                step = f"Main -> Main: {func_name}()\n"
                if step not in self.sequence_steps:
                    self.sequence_steps.append(step)

    def _get_func_name(self, call_node):
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def _get_class_name_from_call(self, call_node):
        """Attempt to determine the class name being instantiated from the call node."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def finalize(self):
        unique_called_classes = "".join(set(self.called_classes.values()))
        self.sequence_steps.append("@enduml")
        return self.diagram + unique_called_classes + "".join(self.sequence_steps)


def generate_sequence_diagram(py_file):
    with open(py_file, "r") as file:
        tree = ast.parse(file.read(), filename=os.path.basename(py_file))

    generator = SequenceDiagramGenerator()
    generator.visit(tree)

    return generator.finalize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a PlantUML sequence diagram from a Python file."
    )
    parser.add_argument("python_file", help="The Python file to analyze.")
    args = parser.parse_args()

    if not os.path.exists(args.python_file):
        print(f"File {args.python_file} does not exist.")
        exit(1)

    puml_diagram = generate_sequence_diagram(args.python_file)
    output_file = os.path.splitext(args.python_file)[0] + "_sequence.puml"

    with open(output_file, "w") as file:
        file.write(puml_diagram)

    print(f"PlantUML sequence diagram has been saved to {output_file}")
