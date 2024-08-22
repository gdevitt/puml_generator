import inspect
import os
import importlib


def generate_plantuml_script(modules):
    """
    Generates a PlantUML script to represent the classes in the given modules.

    Args:
        modules (list): List of Python module objects to analyze.

    Returns:
        str: The PlantUML script.
    """
    plantuml_script = "@startuml\n\n"

    for module in modules:
        plantuml_script += f'package "{module.__name__}" {{\n'

        # Extract classes from each module
        classes = inspect.getmembers(module, inspect.isclass)
        for name, cls in classes:
            if (
                cls.__module__ == module.__name__
            ):  # Only include classes from this module
                # Add the class declaration
                plantuml_script += f"class {name} {{\n"

                # Get the source of the class to maintain the order of methods
                try:
                    source = inspect.getsource(cls)
                    method_names = []
                    for line in source.splitlines():
                        line = line.strip()
                        if line.startswith("def "):
                            method_name = line.split("(")[0].replace("def ", "")
                            method_names.append(method_name)

                    # Add methods in the order they appear in the source code
                    for method_name in method_names:
                        plantuml_script += f"  {method_name}()\n"

                except Exception as e:
                    print(f"Could not retrieve source for {name}: {e}")

                plantuml_script += "}\n\n"

                # Handle inheritance
                for base in cls.__bases__:
                    if base.__module__ != "builtins":  # Skip built-in base classes
                        plantuml_script += f"{base.__name__} <|-- {name}\n"

        plantuml_script += "}\n"

    plantuml_script += "\n@enduml"
    return plantuml_script


def save_plantuml_script(plantuml_script, output_file):
    """
    Saves the PlantUML script to a file.

    Args:
        plantuml_script (str): The PlantUML script.
        output_file (str): The file path to save the script.
    """
    with open(output_file, "w") as file:
        file.write(plantuml_script)


if __name__ == "__main__":
    # List of module names (add your module names here)
    module_names = [
        "data_fetcher",
        "data_preprocessor",
        "technical_analysis",
        "signal_generator",
        "order_manager",
        "order_placer",
        "indicator_calculatons",
        "ema_rsi_strategy",
        "macd_strategy",
        "strategy",
        "utilities",
        "account_history_mt5",
    ]  # Add more modules as needed

    # Dynamically import the modules
    modules = []
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            modules.append(module)
        except ModuleNotFoundError:
            print(f"Module {module_name} not found. Skipping.")

    # Generate the PlantUML script for all modules
    plantuml_script = generate_plantuml_script(modules)

    # Save the script to a .puml file
    output_file = os.path.join(os.path.dirname(__file__), "uml_diagram.puml")
    save_plantuml_script(plantuml_script, output_file)

    print(f"PlantUML script has been saved to {output_file}")
