"""
Setup script for ms-fabric-core-tools-mcp.
Run with: python setup.py

Checks prerequisites, installs dependencies, and generates config files.
No external dependencies - uses only Python stdlib.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ANSI colors (Windows 10+ supports these)
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

PROJECT_DIR = Path(__file__).resolve().parent
CLAUDE_SETTINGS_DIR = Path.home() / ".claude"
CLAUDE_SETTINGS_FILE = CLAUDE_SETTINGS_DIR / "settings.json"
MCP_JSON_FILE = PROJECT_DIR / ".mcp.json"

# Claude Desktop config location per OS
if platform.system() == "Windows":
    CLAUDE_DESKTOP_CONFIG = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
elif platform.system() == "Darwin":
    CLAUDE_DESKTOP_CONFIG = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
else:
    CLAUDE_DESKTOP_CONFIG = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

MCP_SERVER_KEY = "ms-fabric-core-tools-mcp"


def ok(msg: str) -> None:
    print(f"  {GREEN}[OK]{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"  {RED}[FAIL]{RESET} {msg}")


def header(msg: str) -> None:
    print(f"\n{BOLD}{msg}{RESET}")


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timed out"


def check_python() -> bool:
    """Check Python >= 3.12."""
    header("1. Python version")
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 12:
        ok(f"Python {major}.{minor}")
        return True
    else:
        fail(f"Python {major}.{minor} found, need 3.12+")
        print("     Download: https://www.python.org/downloads/")
        return False


def check_uv() -> bool:
    """Check uv is installed, offer to install if not."""
    header("2. uv package manager")
    code, out, _ = run_cmd(["uv", "--version"])
    if code == 0:
        ok(f"uv {out}")
        return True

    fail("uv not found")
    response = input("     Install uv now? (Y/n): ").strip().lower()
    if response in ("", "y", "yes"):
        print("     Installing uv...")
        if platform.system() == "Windows":
            install_code, _, install_err = run_cmd(
                ["powershell", "-c", "irm https://astral.sh/uv/install.ps1 | iex"],
                timeout=60,
            )
        else:
            install_code, _, install_err = run_cmd(
                ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
                timeout=60,
            )
        if install_code == 0:
            ok("uv installed (restart terminal if not found)")
            return True
        else:
            fail(f"Install failed: {install_err[:200]}")
            return False
    else:
        if platform.system() == "Windows":
            print("     Manual install: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        else:
            print("     Manual install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def check_azure_cli() -> bool:
    """Check Azure CLI is installed, offer to install if not."""
    header("3. Azure CLI")
    code, out, _ = run_cmd(["az", "version", "--output", "json"])
    if code == 0:
        try:
            version_info = json.loads(out)
            az_version = version_info.get("azure-cli", "unknown")
            ok(f"Azure CLI {az_version}")
        except json.JSONDecodeError:
            ok("Azure CLI installed")
        return True

    fail("Azure CLI not found")
    response = input("     Install Azure CLI now? (Y/n): ").strip().lower()
    if response in ("", "y", "yes"):
        print("     Installing Azure CLI...")
        if platform.system() == "Windows":
            install_code, _, install_err = run_cmd(
                ["powershell", "-c", "winget install Microsoft.AzureCLI --accept-source-agreements --accept-package-agreements"],
                timeout=120,
            )
        elif platform.system() == "Darwin":
            install_code, _, install_err = run_cmd(
                ["sh", "-c", "brew install azure-cli"],
                timeout=120,
            )
        else:
            install_code, _, install_err = run_cmd(
                ["sh", "-c", "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"],
                timeout=120,
            )
        if install_code == 0:
            ok("Azure CLI installed (restart terminal if not found)")
            return True
        else:
            fail(f"Install failed: {install_err[:200]}")
            print("     Manual install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli")
            return False
    else:
        print("     Manual install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False


def check_azure_auth() -> bool:
    """Check Azure authentication, offer to login if not."""
    header("4. Azure authentication")
    code, out, err = run_cmd(
        ["az", "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com/"],
        timeout=15,
    )
    if code == 0:
        ok("Authenticated with Fabric API")
        return True

    fail("Not authenticated")
    response = input("     Run az login now? (Y/n): ").strip().lower()
    if response in ("", "y", "yes"):
        print("     Opening browser for Azure login...")
        login_code, _, login_err = run_cmd(["az", "login"], timeout=120)
        if login_code == 0:
            ok("Logged in to Azure")
            # Verify Fabric API access
            verify_code, _, _ = run_cmd(
                ["az", "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com/"],
                timeout=15,
            )
            if verify_code == 0:
                ok("Fabric API access confirmed")
                return True
            else:
                warn("Logged in but Fabric API token failed - check workspace permissions")
                return False
        else:
            fail("az login failed")
            return False
    else:
        print("     Run manually: az login")
        return False


def check_odbc() -> bool:
    """Check ODBC Driver 18 for SQL Server (optional)."""
    header("5. ODBC Driver 18 (optional)")
    if platform.system() == "Windows":
        # Check Windows registry via odbcconf or just try import
        code, out, _ = run_cmd(
            ["reg", "query",
             r"HKLM\SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server"],
        )
        if code == 0:
            ok("ODBC Driver 18 installed")
            return True
    else:
        # Linux/Mac: check odbcinst
        code, out, _ = run_cmd(["odbcinst", "-q", "-d"])
        if code == 0 and "ODBC Driver 18" in out:
            ok("ODBC Driver 18 installed")
            return True

    warn("ODBC Driver 18 not found - SQL tools (sql_query, table_preview) won't work")
    print("     Install: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
    return False


def run_uv_sync() -> bool:
    """Install project dependencies."""
    header("6. Install dependencies")
    print("     Running uv sync...")
    code, out, err = run_cmd(["uv", "sync"], timeout=120)
    if code == 0:
        ok("Dependencies installed")
        return True
    else:
        fail("uv sync failed")
        if err:
            print(f"     {err[:200]}")
        return False


def _find_uv_path() -> str:
    """Find full path to uv executable."""
    uv_path = shutil.which("uv")
    if uv_path:
        return uv_path.replace("\\", "/")
    return "uv"


def _mcp_server_config(use_full_path: bool = False) -> dict:
    """Build the MCP server config block.

    Args:
        use_full_path: Use absolute path to uv (needed for Claude Desktop
                       which may not inherit shell PATH).
    """
    cwd_path = str(PROJECT_DIR).replace("\\", "/")
    command = _find_uv_path() if use_full_path else "uv"
    return {
        "command": command,
        "args": ["--directory", cwd_path, "run", "fabric_mcp_stdio.py"],
    }


def ask_client() -> str:
    """Ask which Claude client to configure."""
    header("7. Choose Claude client")
    print("  1) Claude Code (VS Code)")
    print("  2) Claude Desktop")
    print("  3) Both")
    choice = input("  Select (1/2/3): ").strip()
    if choice == "2":
        return "desktop"
    elif choice == "3":
        return "both"
    return "code"


def generate_mcp_json() -> bool:
    """Add MCP server to .mcp.json for Claude Code. Preserves existing servers."""
    header("  Claude Code - .mcp.json")

    config = {}
    if MCP_JSON_FILE.exists():
        try:
            config = json.loads(MCP_JSON_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warn("Existing .mcp.json has bad JSON, will recreate")
            config = {}

    mcp_servers = config.setdefault("mcpServers", {})

    if MCP_SERVER_KEY in mcp_servers:
        warn(f"'{MCP_SERVER_KEY}' already in .mcp.json")
        response = input("     Update entry? (y/N): ").strip().lower()
        if response != "y":
            ok("Kept existing entry")
            return True

    mcp_servers[MCP_SERVER_KEY] = _mcp_server_config()
    MCP_JSON_FILE.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    server_count = len(mcp_servers)
    if server_count > 1:
        ok(f"Added to {MCP_JSON_FILE} ({server_count} servers total, others preserved)")
    else:
        ok(f"Created {MCP_JSON_FILE}")
    return True


def update_claude_settings() -> bool:
    """Ensure ~/.claude/settings.json has enableAllProjectMcpServers."""
    header("  Claude Code - settings.json")

    CLAUDE_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    settings = {}
    if CLAUDE_SETTINGS_FILE.exists():
        try:
            settings = json.loads(CLAUDE_SETTINGS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warn("Existing settings.json has bad JSON, will recreate")
            settings = {}

    if settings.get("enableAllProjectMcpServers") is True:
        ok("enableAllProjectMcpServers already set")
        return True

    settings["enableAllProjectMcpServers"] = True
    CLAUDE_SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2) + "\n", encoding="utf-8"
    )
    ok(f"Updated {CLAUDE_SETTINGS_FILE}")
    return True


def update_claude_desktop_config() -> bool:
    """Add MCP server to Claude Desktop config."""
    header("  Claude Desktop - claude_desktop_config.json")

    CLAUDE_DESKTOP_CONFIG.parent.mkdir(parents=True, exist_ok=True)

    config = {}
    if CLAUDE_DESKTOP_CONFIG.exists():
        try:
            config = json.loads(CLAUDE_DESKTOP_CONFIG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warn("Existing config has bad JSON, will recreate")
            config = {}

    mcp_servers = config.setdefault("mcpServers", {})

    if MCP_SERVER_KEY in mcp_servers:
        warn(f"'{MCP_SERVER_KEY}' already in Claude Desktop config")
        response = input("     Overwrite? (y/N): ").strip().lower()
        if response != "y":
            ok("Kept existing config")
            return True

    mcp_servers[MCP_SERVER_KEY] = _mcp_server_config(use_full_path=True)
    CLAUDE_DESKTOP_CONFIG.write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )
    ok(f"Updated {CLAUDE_DESKTOP_CONFIG}")
    return True


def print_summary(results: dict[str, bool], client: str) -> None:
    """Print final summary."""
    header("Summary")

    required_keys = ["python", "uv", "azure_cli", "azure_auth", "uv_sync"]
    if client in ("code", "both"):
        required_keys += ["mcp_json", "claude_settings"]
    if client in ("desktop", "both"):
        required_keys += ["claude_desktop"]

    all_required_ok = all(results.get(k, False) for k in required_keys)

    for name, passed in results.items():
        status = f"{GREEN}OK{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name}")

    if all_required_ok:
        print(f"\n{GREEN}{BOLD}Setup complete!{RESET}\n")
        print("  Next steps:")
        if client in ("code", "both"):
            print("  - Restart VS Code (or reload window)")
            print("  - Approve the MCP server when prompted")
        if client in ("desktop", "both"):
            print("  - Restart Claude Desktop")
        print("  - Test: ask Claude \"List my Fabric workspaces\"")
    else:
        print(f"\n{RED}{BOLD}Setup incomplete.{RESET} Fix issues above and re-run: python setup.py")


def main() -> None:
    print(f"\n{BOLD}ms-fabric-core-tools-mcp Setup{RESET}")
    print(f"  Project: {PROJECT_DIR}\n")

    # Enable ANSI on Windows
    if platform.system() == "Windows":
        os.system("")

    results: dict[str, bool] = {}

    # Required checks - stop if critical ones fail
    results["python"] = check_python()
    if not results["python"]:
        print_summary(results, "code")
        sys.exit(1)

    results["uv"] = check_uv()
    if not results["uv"]:
        print_summary(results, "code")
        sys.exit(1)

    results["azure_cli"] = check_azure_cli()
    if not results["azure_cli"]:
        print_summary(results, "code")
        sys.exit(1)

    results["azure_auth"] = check_azure_auth()
    # Don't exit - can still install deps and generate configs

    results["odbc"] = check_odbc()
    # Optional - just warn

    results["uv_sync"] = run_uv_sync()

    client = ask_client()

    if client in ("code", "both"):
        results["mcp_json"] = generate_mcp_json()
        results["claude_settings"] = update_claude_settings()

    if client in ("desktop", "both"):
        results["claude_desktop"] = update_claude_desktop_config()

    print_summary(results, client)


if __name__ == "__main__":
    main()
