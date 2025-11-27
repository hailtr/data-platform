"""
Check if Docker services are running and accessible
"""
import sys
import socket
from pathlib import Path

# Add foundation to path
project_root = Path(__file__).parent.parent
foundation_path = project_root / "foundation"
sys.path.insert(0, str(foundation_path))
sys.path.insert(0, str(project_root))

from shared.config import settings


def check_docker_running():
    """Check if Docker Desktop is running"""
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception:
        return False


def check_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open and accepting connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_postgres():
    """Check if PostgreSQL is accessible"""
    return check_port_open(settings.POSTGRES_HOST, settings.POSTGRES_PORT)


def check_redis():
    """Check if Redis is accessible"""
    return check_port_open(settings.REDIS_HOST, settings.REDIS_PORT)


def check_redpanda():
    """Check if Redpanda is accessible"""
    host, port = settings.KAFKA_BOOTSTRAP_SERVERS.split(':')
    return check_port_open(host, int(port))


def main():
    """Check all services"""
    print("=" * 60)
    print("SERVICE HEALTH CHECK")
    print("=" * 60)
    print()
    
    # Check Docker
    print("Checking Docker...")
    docker_running = check_docker_running()
    if docker_running:
        print("  [OK] Docker is running")
    else:
        print("  [ERROR] Docker is not running")
        print()
        print("  To start services:")
        print("    1. Start Docker Desktop")
        print("    2. Run: docker-compose up -d")
        print()
        return False
    
    print()
    
    # Check services
    all_ok = True
    
    print("Checking PostgreSQL...")
    if check_postgres():
        print(f"  [OK] PostgreSQL is accessible at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    else:
        print(f"  [ERROR] PostgreSQL is not accessible at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        print("    - Container may not be running")
        print("    - Run: docker-compose up -d postgres")
        all_ok = False
    
    print()
    print("Checking Redis...")
    if check_redis():
        print(f"  [OK] Redis is accessible at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    else:
        print(f"  [WARNING] Redis is not accessible at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        print("    - Container may not be running")
        print("    - Run: docker-compose up -d redis")
        # Redis is optional, so don't fail
    
    print()
    print("Checking Redpanda...")
    if check_redpanda():
        print(f"  [OK] Redpanda is accessible at {settings.KAFKA_BOOTSTRAP_SERVERS}")
    else:
        print(f"  [ERROR] Redpanda is not accessible at {settings.KAFKA_BOOTSTRAP_SERVERS}")
        print("    - Container may not be running")
        print("    - Run: docker-compose up -d redpanda")
        all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("[SUCCESS] All required services are running!")
        return True
    else:
        print("[FAILED] Some services are not available")
        print()
        print("To start all services:")
        print("  docker-compose up -d")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

