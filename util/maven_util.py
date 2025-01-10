import subprocess

def update_maven_property(pom_dir, property_name, new_value):
    """
    Update a Maven property using the Maven CLI.

    :param property_name: The name of the property to update.
    :param new_value: The new value for the property.
    :param pom_path: The path to the pom.xml file (default is current directory).
    """
    try:
        cmd = [
            "E:/execute/updateGrpcProtoVersion", f"{pom_dir}", f"{new_value}"
        ]
        output = subprocess.run(cmd, check=True,  # Raises an exception if the command fails
        stdout=subprocess.PIPE,  # Captures the standard output
        stderr=subprocess.PIPE   # Captures the standard error
        )
        print(f"Property '{property_name}' updated to '{new_value}' successfully, output[{output}]")
    except subprocess.CalledProcessError as e:
        print(f"Error updating property: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")