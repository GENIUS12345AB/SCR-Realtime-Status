import pyfiglet

DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"


def startup(HUBSITE_VERSION, SCRRTS_VERSION):
    title = pyfiglet.figlet_format("SCR Realtime Status", font="small").rstrip()
    lines = title.split("\n")
    lines.append("")
    lines.append(f"{SCRRTS_VERSION} for SCR Hub Site {HUBSITE_VERSION}")
    width = max(len(line) for line in lines)
    border = "#" * (width + 4)
    print(CYAN + border)
    for line in lines:
        print(f"# {line.center(width)} #")
    print(border + RESET)