"""Network diagnostic and information tools."""

import subprocess
import platform
import socket
import json
from typing import Dict, Any


def ping(host: str = "8.8.8.8", count: int = 4) -> Dict[str, Any]:
    """
    Ping a host to check connectivity.
    
    Args:
        host: The hostname or IP address to ping (default: 8.8.8.8)
        count: Number of ping packets to send (default: 4)
        
    Returns:
        Dictionary with ping results including success, latency, packet loss
    """
    try:
        # Determine ping command based on platform
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", str(count), host]
        else:  # Linux, Darwin (macOS), etc.
            cmd = ["ping", "-c", str(count), host]
        
        # Execute ping command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        success = result.returncode == 0
        
        # Parse output for statistics
        stats = {
            "success": success,
            "host": host,
            "packets_sent": count,
            "output": output[:500]  # Limit output size
        }
        
        # Try to extract latency info
        if success:
            lines = output.split('\n')
            for line in lines:
                if 'time=' in line.lower() or 'time<' in line.lower():
                    # Extract first time value found
                    import re
                    match = re.search(r'time[=<](\d+\.?\d*)\s*ms', line, re.IGNORECASE)
                    if match:
                        stats["latency_ms"] = float(match.group(1))
                        break
        
        return stats
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "host": host,
            "error": "Ping timeout - host may be unreachable"
        }
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "error": f"Ping failed: {str(e)}"
        }


def network_info() -> Dict[str, Any]:
    """
    Get network interface information.
    
    Returns:
        Dictionary with network interface details, IP addresses, hostname
    """
    try:
        info = {
            "hostname": socket.gethostname(),
            "interfaces": {}
        }
        
        # Get local IP address
        try:
            # Connect to external IP to find local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            info["local_ip"] = local_ip
        except:
            info["local_ip"] = "Unable to determine"
        
        # Get fully qualified domain name
        try:
            info["fqdn"] = socket.getfqdn()
        except:
            info["fqdn"] = info["hostname"]
        
        # Try to get more detailed network info using system commands
        system = platform.system().lower()
        
        if system == "linux":
            try:
                # Use ip addr on Linux
                result = subprocess.run(
                    ["ip", "addr", "show"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    info["detailed_output"] = result.stdout[:1000]
            except:
                pass
                
        elif system == "darwin":
            try:
                # Use ifconfig on macOS
                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    info["detailed_output"] = result.stdout[:1000]
            except:
                pass
                
        elif system == "windows":
            try:
                # Use ipconfig on Windows
                result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    info["detailed_output"] = result.stdout[:1000]
            except:
                pass
        
        return info
        
    except Exception as e:
        return {
            "error": f"Failed to get network info: {str(e)}"
        }


def traceroute(host: str, max_hops: int = 15) -> Dict[str, Any]:
    """
    Trace the route to a host.
    
    Args:
        host: The hostname or IP address to trace
        max_hops: Maximum number of hops to trace (default: 15)
        
    Returns:
        Dictionary with traceroute results
    """
    try:
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["tracert", "-h", str(max_hops), host]
        else:  # Linux, Darwin (macOS)
            cmd = ["traceroute", "-m", str(max_hops), host]
        
        # Execute traceroute command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # Traceroute can take longer
        )
        
        output = result.stdout
        
        return {
            "success": result.returncode == 0,
            "host": host,
            "max_hops": max_hops,
            "output": output[:2000]  # Limit output size
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "host": host,
            "error": "Traceroute timeout - operation took too long"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "host": host,
            "error": "Traceroute command not found - may need to be installed"
        }
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "error": f"Traceroute failed: {str(e)}"
        }


def dns_lookup(hostname: str) -> Dict[str, Any]:
    """
    Perform DNS lookup for a hostname.
    
    Args:
        hostname: The hostname to lookup
        
    Returns:
        Dictionary with DNS resolution results
    """
    try:
        # Get IP address(es)
        ip_addresses = socket.gethostbyname_ex(hostname)
        
        return {
            "success": True,
            "hostname": hostname,
            "canonical_name": ip_addresses[0],
            "aliases": ip_addresses[1],
            "ip_addresses": ip_addresses[2]
        }
        
    except socket.gaierror as e:
        return {
            "success": False,
            "hostname": hostname,
            "error": f"DNS lookup failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "hostname": hostname,
            "error": f"Unexpected error: {str(e)}"
        }


def check_port(host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
    """
    Check if a port is open on a host.
    
    Args:
        host: The hostname or IP address
        port: The port number to check
        timeout: Connection timeout in seconds (default: 5)
        
    Returns:
        Dictionary with port status
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        is_open = (result == 0)
        
        return {
            "success": True,
            "host": host,
            "port": port,
            "is_open": is_open,
            "status": "open" if is_open else "closed"
        }
        
    except socket.gaierror:
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": "Hostname could not be resolved"
        }
    except socket.timeout:
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": "Connection timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": f"Port check failed: {str(e)}"
        }
