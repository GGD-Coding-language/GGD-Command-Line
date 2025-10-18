import sys
from pathlib import Path
import subprocess
import os
from my_compiler import compile_custom_file

CVERSION = "1.0.2"
VERSION = "1.0.2"

# Automatically find where the compiler is installed
INSTALL_DIR = Path(__file__).parent.parent

def show_version():
    print(f"GGD Compiler v{CVERSION} GGD CLI v{VERSION}")
    print(f"Installed at: {INSTALL_DIR}")
    print("Made by GGD Organization")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  GGD compile <source_file.my>  → Compile a file")
        print("  GGD run <source_file.my>      → Compile and run")
        print("  GGD --version or version      → Show version info")
        print("  GGD install_geode             → Get commands to download geode")
        print("  GGD docs                      → GGD Custom documentaion on github (Not C++)")
        print("  --offical_COMMANDNAME         → Gives you the geode version of the command")
        return

    command = sys.argv[1].lower()
    if command in ["--offical_version"]:
        print('This is not a offical CLI, there is not offical "version"')
        return
    if command in ["--version", "version"]:
        show_version()
        return
    
    elif command in ["install_geode", "--install geode", "install geode"]:
        print("If you get errors, please make sure you have installed Scoop")
        print("Since I cannot run commands from python (The language this is written in) Please run the following commands:")
        print("scoop bucket add extras")
        print("scoop install geode-sdk-cli")


    elif command in ["--offical_docs", "offical_docs"]:
        print("go to https://docs.geode-sdk.org/ Hover and ctrl+click")
        return
    elif command in ["--docs", "docs", "documentaion"]:
        print("go to https://github.com/GGD-Coding-language/Documentation Hover and ctrl+click")
        return

    elif command == "compile":
        if len(sys.argv) < 3:
            print("❌ Missing source file.")
            return
        source = Path(sys.argv[2])
        compile_custom_file(source, INSTALL_DIR)

    elif command == "run":
        if len(sys.argv) < 3:
            print("❌ Missing source file.")
            return
        source = Path(sys.argv[2])
        exe_file = compile_custom_file(source, INSTALL_DIR)
        if exe_file and exe_file.exists():
            print("\n🚀 Running program:\n")
            subprocess.run([str(exe_file)])
        else:
            print("❌ Could not run — compile failed.")

    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'GGD --version' to check your compiler version.")

if __name__ == "__main__":
    main()

