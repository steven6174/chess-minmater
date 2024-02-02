
def is_windows() -> bool:
    from sys import platform
    # assume that otherwise it's Linux
    return platform.startswith('win')


def clear_console():
    clear_cmd = 'clear'
    if is_windows():
        clear_cmd = 'cls'
    import subprocess
    subprocess.run(clear_cmd, shell=True, check=False)
