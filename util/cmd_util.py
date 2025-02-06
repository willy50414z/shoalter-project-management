import subprocess


def exec(cmd, cwd=None):
    output = subprocess.run(cmd, check=True,  # Raises an exception if the command fails
                            cwd=cwd,
                            text=True,
                            stdout=subprocess.PIPE,  # Captures the standard output
                            stderr=subprocess.PIPE  # Captures the standard error
                            )
    return output.stdout
