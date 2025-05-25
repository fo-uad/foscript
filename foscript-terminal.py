# put here your custom modules
import game

###############################
import tkinter as tk          #
from tkinter import filedialog#
###############################

# ^^^^^^^^^^^^^^^^^^^^
# don't mess with these

FILENAME = "variables.txt"

# Load saved variables
variables = {}
try:
    with open(FILENAME, "r") as f:
        for line in f:
            if "=" in line:
                name, value = line.strip().split("=", 1)
                variables[name] = value
except:
    pass  # File might not exist yet

def get_value(val):
    return variables[val] if val in variables else val

def handle_terminal_command(command):
    command = command.strip()

    # Handle if statements with comparisons
    if command.startswith("if "):
        comparison_ops = ["==", "!=", "<", ">"]
        for op in comparison_ops:
            if op in command and " draw " in command:
                try:
                    condition_part, draw_part = command[3:].split(" draw ", 1)
                    left, right = condition_part.split(op)
                    left_val = get_value(left.strip())
                    right_val = get_value(right.strip())

                    # Try converting to numbers if possible
                    try:
                        left_val = float(left_val)
                        right_val = float(right_val)
                    except:
                        pass

                    if ((op == "==" and left_val == right_val) or
                        (op == "!=" and left_val != right_val) or
                        (op == "<" and left_val < right_val) or
                        (op == ">" and left_val > right_val)):
                        print(draw_part.strip())
                except:
                    print("Error in if command.")
                return True

    # let x be 2
    if command.startswith("let ") and " be " in command:
        parts = command[4:].split(" be ", 1)
        if len(parts) == 2:
            name, value = parts[0].strip(), parts[1].strip()
            variables[name] = value
            with open(FILENAME, "w") as f:
                for k, v in variables.items():
                    f.write(f"{k}={v}\n")
            print(f"{name} saved as {value}")
            return True

    elif command.startswith("get "):
        name = command[4:].strip()
        if name in variables:
            print(f"{name} = {variables[name]}")
        else:
            print(f"{name} not found.")
        return True

    elif command.startswith("draw "):
        message = command[5:].strip()
        print(message)
        return True

    elif command.startswith("use "):
        module = command[4:].strip()
        if module == "game":
            game.run_minecraft()
        return True

    elif command == "exit":
        print("exiting...")
        return False

    elif command == "open":
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Foscript Files", "*.foscript")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        print(f">>> {line}")
                        keep_running = handle_terminal_command(line)
                        if keep_running is False:
                            break
            except Exception as e:
                print(f"Failed to open file: {e}")
        return True

    else:
        print("Unknown or unsupported command.")
        return True

# Main loop
while True:
    terminal = input("foscript > ")
    if not handle_terminal_command(terminal):
        break
