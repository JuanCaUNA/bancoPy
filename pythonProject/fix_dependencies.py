#!/usr/bin/env python3
"""
Dependency Fix Script - Alternative installation method
"""

import sys
import os
import urllib.request
import subprocess
import tempfile


def download_and_install_wheel(package_name, wheel_url):
    """Download and install a wheel file manually"""
    print(f"📦 Downloading {package_name}...")

    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            wheel_path = os.path.join(temp_dir, f"{package_name}.whl")

            # Download wheel
            urllib.request.urlretrieve(wheel_url, wheel_path)
            print(f"✅ Downloaded {package_name}")

            # Install manually
            import zipfile

            with zipfile.ZipFile(wheel_path, "r") as zip_ref:
                # Extract to site-packages
                site_packages = os.path.join(
                    os.path.dirname(sys.executable), "Lib", "site-packages"
                )
                zip_ref.extractall(site_packages)
                print(f"✅ Installed {package_name}")
                return True

    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False


def check_dependency(module_name):
    """Check if a dependency is available"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def simple_pip_install(package):
    """Try simple pip install with fallback"""
    print(f"📦 Trying to install {package}...")

    try:
        # Try direct Python approach
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import subprocess; subprocess.run(['{sys.executable}', '-m', 'pip', 'install', '--user', '{package}'])",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            print(f"✅ Successfully installed {package}")
            return True
        else:
            print(f"❌ Failed to install {package}: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error installing {package}: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("🔧 DEPENDENCY FIX TOOL - Sistema Bancario SINPE")
    print("=" * 60)
    print()

    # Check current status
    print("🔍 Checking current dependencies...")
    dependencies = {
        "flask": "Flask",
        "requests": "requests",
        "rich": "rich",
        "sqlalchemy": "SQLAlchemy",
    }

    status = {}
    for module, package in dependencies.items():
        available = check_dependency(module)
        status[module] = available
        print(
            f"{'✅' if available else '❌'} {package}: {'Available' if available else 'Missing'}"
        )

    print()

    # If all dependencies are available, we're done
    if all(status.values()):
        print("🎉 All dependencies are already installed!")
        return

    # Try to install missing dependencies
    print("📦 Attempting to install missing dependencies...")
    print()

    for module, package in dependencies.items():
        if not status[module]:
            print(f"Installing {package}...")
            success = simple_pip_install(package)
            if success:
                status[module] = check_dependency(module)

    print()
    print("=" * 60)
    print("📊 FINAL STATUS")
    print("=" * 60)

    for module, package in dependencies.items():
        available = check_dependency(module)
        print(
            f"{'✅' if available else '❌'} {package}: {'Available' if available else 'Still Missing'}"
        )

    print()

    if all(check_dependency(mod) for mod in dependencies.keys()):
        print("🎉 All dependencies successfully installed!")
        print("You can now run:")
        print("  • python main.py (Rich Terminal)")
        print("  • python gui.py (GUI Interface)")
        print("  • python web_gui.py (Web Interface)")
    else:
        print("⚠️ Some dependencies couldn't be installed due to Python corruption.")
        print("Recommendations:")
        print("1. Use CLI Simple: python cli_simple.py")
        print("2. Reinstall Python from python.org")
        print("3. Use a different Python distribution (Anaconda/Miniconda)")


if __name__ == "__main__":
    main()
