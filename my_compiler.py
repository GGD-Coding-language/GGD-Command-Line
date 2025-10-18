
# This is not the real compiler since I am still working on it.

import os
import subprocess
from pathlib import Path

def translate_custom_to_cpp(source_code: str) -> str:
    # Always start with <Geode> for the conversion to C++
    cpp = ["#include <Geode>", "", "#include <iostream>", "using namespace std;", ""]
    lines = source_code.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Fake syntax rules
        if line.startswith("say "):
            cpp.append(f'cout << {line[4:]} << endl;')
        elif line.startswith("let "):
            cpp.append("int " + line[4:] + ";")
        elif line.startswith("add "):
            parts = line.split()
            if len(parts) == 4:
                _, a, b, c = parts
                cpp.append(f"{c} = {a} + {b};")
        else:
            cpp.append("// Unknown syntax: " + line)

    return "\n".join(cpp)

def compile_custom_file(input_path: Path, install_dir: Path):
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        return

    # Load your custom language code
    source_code = input_path.read_text(encoding="utf-8")

    # Translate to C++
    cpp_code = translate_custom_to_cpp(source_code)

    # Output file names
    cpp_path = install_dir / (input_path.stem + ".cpp")
    exe_path = install_dir / (input_path.stem + ".exe")

    cpp_path.write_text(cpp_code, encoding="utf-8")
    print(f"✅ Generated: {cpp_path}")

    # Compile using gdd
    try:
        subprocess.run(["gdd", str(cpp_path), "-o", str(exe_path)], check=True)
        print(f"✅ Compiled successfully → {exe_path}") # Will not work if you use my custom syntax in GGD-Coding-language/Documentation
        return exe_path
    except subprocess.CalledProcessError:
        print("❌ Compilation failed. Make sure gdd is installed and in PATH.")
        return None

