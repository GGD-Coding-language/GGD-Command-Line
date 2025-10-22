from pathlib import Path
import random

def compile_custom_file(source: Path, install_dir: Path, togd: bool = False) -> Path:
    """
    Compile a .ggd source file to .cpp. If `togd` is True, prepare it for Geode mod build.
    Returns the path to the generated .cpp file.
    """

    # Ensure build folder exists
    build_dir = install_dir / "build"
    build_dir.mkdir(exist_ok=True)

    cpp_path = build_dir / f"{source.stem}.cpp"

    # Read GGD code
    code = source.read_text()

    # Start C++ output
    cpp_code = "#include <Geode>\nusing namespace geode::prelude;\n\n"

    for line in code.splitlines():
        line = line.strip()
        if line.startswith("//") or line == "":
            cpp_code += line + "\n"
            continue
        # Handle CreateButton
        if line.startswith("CreateButton("):
            parts = line[len("CreateButton("):-1].split(",")
            name = parts[0].strip().strip('"')
            place = parts[1].strip()
            id_val = parts[2].strip()
            enabled = parts[3].strip().lower() == "true"
            cpp_code += f'auto {id_val} = ButtonSprite::create("{name}");\n'
            cpp_code += f'menu->addChild({id_val});\n'
        # Handle MMnewButton
        elif line.startswith("MMnewButton("):
            parts = line[len("MMnewButton("):-1].split(",")
            name = parts[0].strip().strip('"')
            filename = parts[1].strip()
            id_val = parts[2].strip()
            cpp_code += f'auto {id_val} = CCMenuItemSpriteExtra::create(ButtonSprite::create("{name}"), this, nullptr);\n'
            cpp_code += f'menu->addChild({id_val});\n'
        else:
            cpp_code += f"// {line}\n"

    cpp_path.write_text(cpp_code)
    print(f"✅ Generated: {cpp_path}")

    return cpp_path
