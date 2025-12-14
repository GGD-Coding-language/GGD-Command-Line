import sys
import subprocess
import shutil
import os
from pathlib import Path
from my_compiler import compile_custom_file
from colorama import Fore, Style, init # type: ignore
import requests  # type: ignore
from tqdm import tqdm # type: ignore
import hashlib
import zipfile
import io

init(autoreset=True)

CVERSION = "1.0.3"
VERSION = "1.0.3"
INSTALL_DIR = Path(__file__).parent.parent

# ====================== Logging ======================
def success(msg): print(f"✅ {msg}")
def warn(msg): print(f"⚠️ {msg}")
def fail(msg): print(f"❌ {msg}")
def info(msg): print(f"| Info | {msg}")

# ====================== Dependency Checks ======================
def ensure_scoop():
    """Try to detect Scoop automatically."""
    scoop_exe = shutil.which("scoop")
    if scoop_exe:
        return scoop_exe

    # Check default user install location
    default_path = Path.home() / "scoop" / "shims" / "scoop.exe"
    if default_path.exists():
        return str(default_path)

    return None

def ensure_cmake_installed():
    if shutil.which("cmake"):
        return True

    warn("CMake not found. Installing manually with progress bars...")
    cmake_version = "3.27.7"
    cmake_zip_url = f"https://github.com/Kitware/CMake/releases/download/v{cmake_version}/cmake-{cmake_version}-windows-x86_64.zip"

    # You must replace this with the official SHA256 from CMake releases
    expected_hash = "YOUR_EXPECTED_SHA256_HASH_HERE"

    install_dir = Path.home() / "cmake_manual"
    install_dir.mkdir(exist_ok=True)

    # Download with progress
    r = requests.get(cmake_zip_url, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    block_size = 1024

    buffer = io.BytesIO()
    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading CMake") as pbar:
        for data in r.iter_content(block_size):
            buffer.write(data)
            pbar.update(len(data))

    buffer.seek(0)
    
    # Hash check with progress
    sha256 = hashlib.sha256()
    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Verifying hash") as pbar:
        for chunk in iter(lambda: buffer.read(4096), b""):
            sha256.update(chunk)
            pbar.update(len(chunk))
    buffer.seek(0)

    if sha256.hexdigest() != expected_hash:
        fail("Hash check failed. Download may be corrupted.")
        return False

    # Extract with progress
    with zipfile.ZipFile(buffer) as zf:
        file_list = zf.namelist()
        with tqdm(total=len(file_list), desc="Extracting CMake") as pbar:
            for file in file_list:
                zf.extract(file, install_dir)
                pbar.update(1)

    # Add cmake to PATH for this session
    os.environ["PATH"] += os.pathsep + str(install_dir / f"cmake-{cmake_version}-windows-x86_64" / "bin")
    success(f"CMake installed successfully to {install_dir}")
    return True

def ensure_geode_cli_installed():
    geode_cli = shutil.which("geode")
    if geode_cli:
        return geode_cli

    warn("Geode CLI not found. Installing via Scoop...")
    scoop_exe = ensure_scoop()
    if not scoop_exe:
        fail("Scoop not found. Please install Scoop manually from https://scoop.sh/")
        return None

    try:
        subprocess.run([scoop_exe, "bucket", "add", "extras"], check=True)
        subprocess.run([scoop_exe, "install", "geode"], check=True)
        success("Geode CLI installed successfully via Scoop.")
        return shutil.which("geode")
    except subprocess.CalledProcessError:
        fail("Failed to install Geode CLI. Please install manually from https://docs.geode-sdk.org/cli.")
        return None

def ensure_compiler():
    if shutil.which("cl"):
        success("MSVC detected.")
        return "cl"
    if shutil.which("g++"):
        success("g++ detected.")
        return "g++"

    warn("No C++ compiler detected.")
    choice = input("Which compiler do you want to install? (MSVC/g++): ").strip().lower()

    if choice == "msvc":
        info("Installing Visual Studio Build Tools (MSVC)...")
        try:
            subprocess.run([
                "powershell", "Start-Process", "vs_buildtools.exe",
                "--add", "Microsoft.VisualStudio.Workload.VCTools",
                "--quiet", "--wait"
            ], check=True)
            success("MSVC installed successfully.")
            return "cl"
        except Exception as e:
            fail(f"MSVC installation failed: {e}")
            return None

    elif choice == "g++":
        info("Installing g++ via Scoop...")
        scoop_exe = ensure_scoop()
        if not scoop_exe:
            fail("Scoop not found, cannot install g++")
            return None
        try:
            subprocess.run([scoop_exe, "install", "gcc"], check=True)
            success("g++ installed successfully.")
            return "g++"
        except Exception as e:
            fail(f"Failed to install g++: {e}")
            return None
    else:
        fail("Invalid choice.")
        return None

# ====================== Geode Build ======================
def detect_geometry_dash():
    """Try to detect Geometry Dash folder automatically."""
    possible_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Packages" / "RobTopGames.GeometryDash_8wekyb3d8bbwe" / "LocalCache",
        Path("C:/Program Files (x86)/Steam/steamapps/common/Geometry Dash"),
        Path("C:/Program Files/Steam/steamapps/common/Geometry Dash"),
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return None

def build_geode_mod(cpp_file: Path):
    success(f"Generated: {cpp_file}")
    geode_cli = ensure_geode_cli_installed()
    if not geode_cli:
        return fail("❌ Geode CLI not found, could not continue.")

    if not ensure_cmake_installed():
        return fail("❌ CMake installation failed, cannot continue.")

    gd_folder = detect_geometry_dash()
    if not gd_folder:
        gd_folder = input("Could not detect Geometry Dash. Enter GD folder path manually: ")
        gd_folder = Path(gd_folder)
        if not gd_folder.exists():
            return fail("Invalid Geometry Dash path.")

    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    info("Setting up Geode project...")
    try:
        subprocess.run([geode_cli, "setup"], cwd=build_dir, check=True)
    except subprocess.CalledProcessError:
        warn("Profiles already exist, skipping setup.")

    info("Configuring Geode project...")
    try:
        subprocess.run([geode_cli, "config"], cwd=build_dir, check=True)
    except subprocess.CalledProcessError as e:
        return fail(f"Config setup failed: {e}")

    info("Building Geode mod...")
    try:
        subprocess.run([geode_cli, "build"], cwd=build_dir, check=True)
        # Copy mod to Geometry Dash folder automatically
        mods_folder = gd_folder / "Mods"
        mods_folder.mkdir(exist_ok=True)
        # Assume build produces a .geode file in build_dir/dist
        for file in (build_dir / "dist").glob("*.geode"):
            shutil.copy(file, mods_folder)
            success(f"Copied {file.name} to {mods_folder}")
        success("🎉 Geode mod compiled and deployed successfully!")
    except subprocess.CalledProcessError:
        fail("❌ Geode build failed.")

# ====================== Help Menu ======================
def show_version():
    print(f"GGD Compiler v{CVERSION} GGD CLI v{VERSION}")
    print(f"Installed at: {INSTALL_DIR}")
    print("Made by GGD Organization")

def show_usage():
    print(f"{Fore.CYAN}Usage:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}GGD compile <source_file.ggd> [-togd]{Style.RESET_ALL}  → Compile file, optionally to GD mods")
    print(f"  {Fore.YELLOW}GGD run <source_file.ggd>{Style.RESET_ALL}              → Compile and run")
    print(f"  {Fore.YELLOW}GGD --version{Style.RESET_ALL}                          → Show version info")
    print(f"  {Fore.YELLOW}GGD install_geode{Style.RESET_ALL}                      → Instructions to install Geode CLI")
    print(f"  {Fore.YELLOW}GGD docs{Style.RESET_ALL}                               → Open GGD documentation")
    print(f"  {Fore.YELLOW}--offical_COMMANDNAME{Style.RESET_ALL}                  → Show Geode official version of command")
    print()
    print(f"{Fore.MAGENTA}Example:{Style.RESET_ALL}")
    print(f"  GGD compile example.ggd -togd")
    print(f"  GGD run test.ggd")
    print(f"  GGD install_geode")
    print()
    print(f"{Fore.GREEN}Made by the GGD Organization 💾{Style.RESET_ALL}")

# ====================== Main CLI ======================
def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() in ["help", "--help", "-h"]:
        show_usage()
        return

    command = sys.argv[1].lower()

    if command in ["--offical_version"]:
        print('This is not an official CLI, there is no official "version"')
        return

    if command in ["--version", "version"]:
        show_version()
        return

    if command in ["install_geode", "--install geode", "install geode"]:
        print("If you get errors, please make sure you have installed Scoop")
        print("Since I cannot run commands from python (The language this is written in) Please run the following commands:")
        print("scoop bucket add extras")
        print("scoop install geode-sdk-cli")
        return

    if command in ["--offical_docs", "offical_docs"]:
        print("Go to https://docs.geode-sdk.org/ Hover and ctrl+click")
        return

    if command in ["--docs", "docs", "documentation"]:
        print("Go to https://ggd-coding-language.github.io/Documentation.html Hover and ctrl+click")
        return

    if command == "compile":
        if len(sys.argv) < 3:
            fail("Missing source file.")
            return
        source = Path(sys.argv[2])
        togd = "-togd" in sys.argv
        exe_file = compile_custom_file(source, INSTALL_DIR)
        if togd:
            build_geode_mod(exe_file)

    elif command == "run":
        if len(sys.argv) < 3:
            fail("Missing source file.")
            return
        source = Path(sys.argv[2])
        exe_file = compile_custom_file(source, INSTALL_DIR)
        if exe_file and exe_file.exists():
            success("\n🚀 Running program:\n")
            subprocess.run([str(exe_file)])
        else:
            fail("Could not run — compile failed.")

    else:
        fail(f"Unknown command: {command}")
        show_usage()

if __name__ == "__main__":
    main()

