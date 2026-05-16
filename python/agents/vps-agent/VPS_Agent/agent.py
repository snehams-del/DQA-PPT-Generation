from google.adk.agents.llm_agent import Agent
import requests
import os
import paramiko
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================
# SSH CONNECTION HELPER
# ============================================

@contextmanager
def ssh_connection():
    """
    Context manager for SSH connections.
    Automatically handles connection setup and teardown.
    
    Usage:
        with ssh_connection() as client:
            stdin, stdout, stderr = client.exec_command("ls")
    """
    hostname = os.getenv("SSH_HOSTNAME", "")
    port = int(os.getenv("SSH_PORT", 22))
    username = os.getenv("SSH_USERNAME", "")
    password = os.getenv("SSH_PASSWORD", "")
    
    if not all([hostname, username, password]):
        raise ValueError("SSH credentials not configured. Required: SSH_HOSTNAME, SSH_USERNAME, SSH_PASSWORD")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=hostname, port=port, username=username, password=password)
        yield client
    finally:
        client.close()


@contextmanager
def sftp_connection():
    """
    Context manager for SFTP connections.
    Automatically handles connection setup and teardown.
    
    Usage:
        with sftp_connection() as sftp:
            sftp.put(local_path, remote_path)
    """
    with ssh_connection() as client:
        sftp = client.open_sftp()
        try:
            yield sftp
        finally:
            sftp.close()


# ============================================
# SSH COMMAND EXECUTION
# ============================================

def execute_command(command: str) -> dict:
    """
    Executes a command on the remote server via SSH.
    
    Args:
        command: The full command string to execute on the remote server.
    
    Returns:
        dict with status, command executed, output, and any errors.
    """
    try:
        with ssh_connection() as client:
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            return {
                "status": "success",
                "command": command,
                "output": output if output else "(no output)",
                "error": error if error else None
            }
    
    except ValueError as e:
        return {"status": "error", "command": command, "message": str(e)}
    except paramiko.AuthenticationException:
        return {"status": "error", "command": command, "message": "Authentication failed. Check SSH credentials."}
    except paramiko.SSHException as e:
        return {"status": "error", "command": command, "message": f"SSH connection error: {e}"}
    except Exception as e:
        return {"status": "error", "command": command, "message": f"Error: {e}"}


# ============================================
# SFTP FILE TRANSFER FUNCTIONS
# ============================================

def upload_file(local_path: str, remote_path: str) -> dict:
    """
    Upload a file from local machine to remote server via SFTP.
    """
    if not os.path.exists(local_path):
        return {"status": "error", "message": f"Local file not found: {local_path}"}
    
    try:
        with sftp_connection() as sftp:
            sftp.put(local_path, remote_path)
            file_size = os.path.getsize(local_path)
            return {
                "status": "success",
                "message": f"✓ Uploaded {local_path} → {remote_path}",
                "file_size": f"{file_size / 1024:.2f} KB"
            }
    except FileNotFoundError:
        return {"status": "error", "message": f"Remote path not accessible: {remote_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Upload failed: {e}"}


def download_file(remote_path: str, local_path: str) -> dict:
    """
    Download a file from remote server to local machine via SFTP.
    """
    try:
        with sftp_connection() as sftp:
            sftp.get(remote_path, local_path)
            file_size = os.path.getsize(local_path)
            return {
                "status": "success",
                "message": f"✓ Downloaded {remote_path} → {local_path}",
                "file_size": f"{file_size / 1024:.2f} KB"
            }
    except FileNotFoundError:
        return {"status": "error", "message": f"Remote file not found: {remote_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Download failed: {e}"}


def list_remote_directory(remote_path: str = ".") -> dict:
    """
    List files and directories at a remote path.
    """
    try:
        with sftp_connection() as sftp:
            files = sftp.listdir_attr(remote_path)
            file_list = []
            for f in files:
                file_type = "DIR" if f.st_mode & 0o40000 else "FILE"
                file_list.append({
                    "name": f.filename,
                    "type": file_type,
                    "size": f"{f.st_size / 1024:.2f} KB" if file_type == "FILE" else "-"
                })
            return {
                "status": "success",
                "path": remote_path,
                "files": file_list,
                "count": len(file_list)
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to list directory: {e}"}


# ============================================
# SYSTEM MONITORING FUNCTIONS
# ============================================

def get_system_stats() -> dict:
    """
    Get CPU, memory, and disk usage from the remote server.
    """
    try:
        with ssh_connection() as client:
            stats = {}
            
            # CPU usage
            stdin, stdout, stderr = client.exec_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
            stats["cpu_usage"] = f"{stdout.read().decode().strip()}%"
            
            # Memory usage
            stdin, stdout, stderr = client.exec_command("free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2}'")
            stats["memory_usage"] = stdout.read().decode().strip()
            
            # Disk usage
            stdin, stdout, stderr = client.exec_command("df -h / | awk 'NR==2{print $5}'")
            stats["disk_usage"] = stdout.read().decode().strip()
            
            # Uptime
            stdin, stdout, stderr = client.exec_command("uptime -p")
            stats["uptime"] = stdout.read().decode().strip()
            
            return {"status": "success", "stats": stats}
    except Exception as e:
        return {"status": "error", "message": f"Failed to get stats: {e}"}


# ============================================
# WEBSITE MONITORING FUNCTION
# ============================================

def ping_website() -> dict:
    """
    Strict HTTP check for the configured URL.
    """
    url = os.getenv("MONITOR_URLS", "")
    
    if not url:
        return {"status": "error", "message": "No MONITOR_URLS configured in .env file"}
    
    try:
        resp = requests.get(url, timeout=5, allow_redirects=True)
        code = resp.status_code

        if 200 <= code < 400:
            return {"status": "up", "url": url, "status_code": code, "message": f"✓ {url} is UP ({code})"}

        return {"status": "down", "url": url, "status_code": code, "message": f"✗ {url} is DOWN ({code})"}

    except requests.exceptions.RequestException as e:
        return {"status": "down", "url": url, "error": str(e), "message": f"✗ {url} is DOWN"}


# ============================================
# SUB-AGENTS
# ============================================

docker_manager_agent = Agent(
    model='gemini-2.5-flash',
    name='docker_manager',
    description='Docker management agent for container operations.',
    instruction='''You are a Docker Manager agent. Construct Docker commands and execute them using execute_command.

## ALLOWED COMMANDS ONLY:
1. `docker ps -a` - List containers
2. `docker start <name>` - Start container
3. `docker stop <name>` - Stop container
4. `docker logs --tail <n> <name>` - View logs
5. `docker network ls` - List networks
6. `docker volume ls` - List volumes

## REJECTED (DO NOT EXECUTE):
❌ docker exec, rm, rmi, run, build, pull, push
❌ Any non-Docker commands

Explain what command you're running before executing.''',
    tools=[execute_command],
)

file_transfer_agent = Agent(
    model='gemini-2.5-flash',
    name='file_transfer',
    description='File transfer agent for SFTP operations.',
    instruction='''You are a File Transfer agent for SFTP operations.

## AVAILABLE OPERATIONS:
1. upload_file(local_path, remote_path) - Upload file to server
2. download_file(remote_path, local_path) - Download file from server
3. list_remote_directory(remote_path) - List remote files

## CRITICAL PATH RULES - CHECK BEFORE EVERY OPERATION:

### For UPLOAD (local → remote):
✓ local_path: Full path including filename (e.g., "C:\\Users\\name\\file.txt")
✓ remote_path: MUST include the filename, NOT just directory!
  - ❌ WRONG: "/root/" or "/home/user/"
  - ✓ CORRECT: "/root/file.txt" or "/home/user/file.txt"

### For DOWNLOAD (remote → local):
✓ remote_path: Full path to file on server (e.g., "/var/log/app.log")
✓ local_path: Full path including filename where to save

### Common Errors to Avoid:
1. If user says "upload to /root", ask or auto-append the filename
2. Always extract filename from local_path and append to remote directory
3. /root/ directory may have permission issues - suggest /tmp/ or user home if fails

### PATH VALIDATION STEPS:
1. Check if local file exists (for uploads)
2. Ensure remote_path ends with filename, not just "/"
3. If path ends with "/", append the source filename automatically
4. Confirm both paths before executing

### Example Corrections:
- User: "upload demo.txt to /root"
- You: Use upload_file("C:\\path\\demo.txt", "/root/demo.txt")

Report success with file size or explain exact error if failed.''',
    tools=[upload_file, download_file, list_remote_directory],
)

system_monitor_agent = Agent(
    model='gemini-2.5-flash',
    name='system_monitor',
    description='System monitoring agent for server health metrics.',
    instruction='''You are a System Monitor agent for server health.

## AVAILABLE:
get_system_stats() - Returns CPU, memory, disk usage, and uptime

Present metrics clearly and highlight concerning values (>80%).''',
    tools=[get_system_stats],
)


# ============================================
# ROOT AGENT
# ============================================

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='VPS management assistant for monitoring and operations.',
    instruction='''You are a VPS Management Assistant.

## ROUTING:
| Request | Action |
|---------|--------|
| Website status | Use ping_website() |
| Docker operations | → docker_manager |
| File upload/download | → file_transfer |
| Server health/CPU/memory | → system_monitor |

Be helpful and provide clear status updates.''',
    tools=[ping_website],
    sub_agents=[docker_manager_agent, file_transfer_agent, system_monitor_agent],
)
