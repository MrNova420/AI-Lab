#!/usr/bin/env python3
"""
Comprehensive Live Status Monitor for NovaForge
Real-time monitoring of ALL system components
"""

import psutil
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import subprocess

class ComprehensiveStatusMonitor:
    """Monitor everything in real-time"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.last_net_io = None
        self.last_disk_io = None
        self.last_check_time = time.time()
        
    def get_all_status(self) -> Dict[str, Any]:
        """Get comprehensive status of everything"""
        current_time = time.time()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "uptime": self._get_uptime(),
            "system": self._get_system_status(),
            "hardware": self._get_hardware_status(),
            "processes": self._get_process_status(),
            "ai_model": self._get_model_status(),
            "sessions": self._get_session_status(),
            "storage": self._get_storage_status(),
            "network": self._get_network_status(current_time),
            "performance": self._get_performance_metrics(),
            "health": self._get_health_status()
        }
        
        self.last_check_time = current_time
        return status
    
    def _get_uptime(self) -> Dict[str, Any]:
        """System uptime"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            "seconds": uptime_seconds,
            "formatted": f"{days}d {hours}h {minutes}m",
            "boot_time": datetime.fromtimestamp(boot_time).isoformat()
        }
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Core system info"""
        return {
            "platform": psutil.LINUX if hasattr(psutil, 'LINUX') else "unknown",
            "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
            "pid": psutil.Process().pid,
            "cwd": str(Path.cwd())
        }
    
    def _get_hardware_status(self) -> Dict[str, Any]:
        """CPU, GPU, Memory, Disk - detailed with WSL detection"""
        
        # Detect if running in WSL
        is_wsl = False
        wsl_version = None
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    is_wsl = True
                    if 'wsl2' in version_info:
                        wsl_version = 2
                    else:
                        wsl_version = 1
        except:
            pass
        
        # CPU - detailed
        cpu_freq = psutil.cpu_freq()
        cpu_stats = psutil.cpu_stats()
        cpu_times = psutil.cpu_times()
        
        # Get WSL allocated cores
        allocated_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False)
        
        # Try to get Windows host total cores if WSL
        host_cores = None
        host_cores_physical = None
        if is_wsl:
            try:
                import subprocess
                result = subprocess.run(
                    ['cmd.exe', '/c', 'wmic cpu get NumberOfCores,NumberOfLogicalProcessors /format:list'],
                    capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'NumberOfLogicalProcessors=' in line:
                            host_cores = int(line.split('=')[1].strip())
                        if 'NumberOfCores=' in line:
                            host_cores_physical = int(line.split('=')[1].strip())
            except:
                pass
        
        cpu = {
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "per_core": psutil.cpu_percent(interval=0.1, percpu=True),
            "count_logical": allocated_cores,
            "count_physical": physical_cores,
            "frequency_mhz": cpu_freq.current if cpu_freq else 0,
            "frequency_min_mhz": cpu_freq.min if cpu_freq else 0,
            "frequency_max_mhz": cpu_freq.max if cpu_freq else 0,
            "ctx_switches": cpu_stats.ctx_switches if cpu_stats else 0,
            "interrupts": cpu_stats.interrupts if cpu_stats else 0,
            "user_time": cpu_times.user if cpu_times else 0,
            "system_time": cpu_times.system if cpu_times else 0,
            "idle_time": cpu_times.idle if cpu_times else 0,
            # WSL info
            "is_wsl": is_wsl,
            "wsl_version": wsl_version,
            "wsl_allocated_cores": allocated_cores if is_wsl else None,
            "host_total_cores": host_cores,
            "host_physical_cores": host_cores_physical
        }
        
        # Temperature
        try:
            temps = psutil.sensors_temperatures()
            cpu_temp = 0
            if temps:
                for name, entries in temps.items():
                    if 'coretemp' in name.lower() or 'cpu' in name.lower():
                        if entries:
                            cpu_temp = entries[0].current
                            break
            cpu["temperature_c"] = cpu_temp
        except:
            cpu["temperature_c"] = 0
        
        # GPU - ultra detailed
        gpu = self._get_detailed_gpu()
        
        # Memory - detailed with WSL awareness
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Get WSL allocated memory
        allocated_memory_gb = mem.total / (1024**3)
        
        # Try to get Windows host total memory if WSL
        host_total_memory_gb = None
        if is_wsl:
            try:
                result = subprocess.run(
                    ['cmd.exe', '/c', 'wmic computersystem get TotalPhysicalMemory /format:list'],
                    capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'TotalPhysicalMemory=' in line:
                            bytes_val = int(line.split('=')[1].strip())
                            host_total_memory_gb = bytes_val / (1024**3)
                            break
            except:
                pass
        
        memory = {
            "used_gb": mem.used / (1024**3),
            "available_gb": mem.available / (1024**3),
            "total_gb": allocated_memory_gb,
            "percent": mem.percent,
            "cached_gb": mem.cached / (1024**3) if hasattr(mem, 'cached') else 0,
            "buffers_gb": mem.buffers / (1024**3) if hasattr(mem, 'buffers') else 0,
            "swap_used_gb": swap.used / (1024**3),
            "swap_total_gb": swap.total / (1024**3),
            "swap_percent": swap.percent,
            # WSL info
            "is_wsl": is_wsl,
            "wsl_allocated_gb": allocated_memory_gb if is_wsl else None,
            "host_total_gb": host_total_memory_gb
        }
        
        # Disk - detailed
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        storage = {
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "total_gb": disk.total / (1024**3),
            "percent": disk.percent,
            "read_mb": disk_io.read_bytes / (1024**2) if disk_io else 0,
            "write_mb": disk_io.write_bytes / (1024**2) if disk_io else 0,
            "read_count": disk_io.read_count if disk_io else 0,
            "write_count": disk_io.write_count if disk_io else 0
        }
        
        return {
            "cpu": cpu,
            "gpu": gpu,
            "memory": memory,
            "storage": storage,
            "environment": {
                "is_wsl": is_wsl,
                "wsl_version": wsl_version,
                "platform": "WSL" if is_wsl else "Native Linux"
            }
        }
    
    def _get_detailed_gpu(self) -> Dict[str, Any]:
        """Get ultra-detailed GPU info"""
        gpu = {
            "available": False,
            "count": 0,
            "devices": []
        }
        
        # Try GPUtil first
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu["available"] = True
                gpu["count"] = len(gpus)
                for g in gpus:
                    gpu["devices"].append({
                        "id": g.id,
                        "name": g.name,
                        "usage_percent": g.load * 100,
                        "memory_used_mb": g.memoryUsed,
                        "memory_total_mb": g.memoryTotal,
                        "memory_percent": (g.memoryUsed / g.memoryTotal * 100) if g.memoryTotal > 0 else 0,
                        "temperature_c": g.temperature,
                        "driver": g.driver
                    })
                return gpu
        except:
            pass
        
        # Try nvidia-smi
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,driver_version,power.draw,power.limit', 
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                gpu["available"] = True
                lines = result.stdout.strip().split('\n')
                gpu["count"] = len(lines)
                
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 6:
                        gpu["devices"].append({
                            "id": int(parts[0]),
                            "name": parts[1],
                            "usage_percent": float(parts[2]),
                            "memory_used_mb": float(parts[3]),
                            "memory_total_mb": float(parts[4]),
                            "memory_percent": (float(parts[3]) / float(parts[4]) * 100) if float(parts[4]) > 0 else 0,
                            "temperature_c": float(parts[5]),
                            "driver": parts[6] if len(parts) > 6 else "unknown",
                            "power_draw_w": float(parts[7]) if len(parts) > 7 else 0,
                            "power_limit_w": float(parts[8]) if len(parts) > 8 else 0
                        })
        except:
            pass
        
        return gpu
    
    def _get_process_status(self) -> Dict[str, Any]:
        """Running processes status"""
        processes = {
            "total_count": len(list(psutil.process_iter())),
            "novaforge": [],
            "system_load": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
        
        # Find NovaForge processes
        keywords = ['forge', 'ollama', 'python', 'node', 'vite', 'electron']
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                name = proc.info['name'].lower()
                if any(kw in name for kw in keywords):
                    processes["novaforge"].append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent'],
                        "status": proc.info['status']
                    })
            except:
                pass
        
        return processes
    
    def _get_model_status(self) -> Dict[str, Any]:
        """AI model status"""
        status = {
            "loaded": False,
            "name": "none",
            "provider": "unknown",
            "ready": False,
            "last_inference_time": 0
        }
        
        # Check Ollama
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    status["loaded"] = True
                    status["provider"] = "ollama"
                    status["ready"] = True
                    # Parse model name from first data line
                    model_line = lines[1].split()
                    if model_line:
                        status["name"] = model_line[0]
        except:
            pass
        
        return status
    
    def _get_session_status(self) -> Dict[str, Any]:
        """Chat session status"""
        sessions_dir = self.base_path / "logs" / "sessions"
        
        status = {
            "active": False,
            "total_sessions": 0,
            "today_sessions": 0,
            "total_messages": 0,
            "current_session_id": None,
            "current_session_messages": 0
        }
        
        if sessions_dir.exists():
            # Count all sessions
            session_files = list(sessions_dir.rglob("*.json"))
            status["total_sessions"] = len(session_files)
            
            # Count today's sessions
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = 0
            total_messages = 0
            
            for session_file in session_files:
                try:
                    data = json.loads(session_file.read_text())
                    if data.get('start_time', '').startswith(today):
                        today_count += 1
                    total_messages += len(data.get('messages', []))
                except:
                    pass
            
            status["today_sessions"] = today_count
            status["total_messages"] = total_messages
        
        return status
    
    def _get_storage_status(self) -> Dict[str, Any]:
        """Storage locations status"""
        locations = {
            "models": self._get_dir_size(self.base_path / "models"),
            "logs": self._get_dir_size(self.base_path / "logs"),
            "exports": self._get_dir_size(self.base_path / "exports"),
            "memory": self._get_dir_size(self.base_path / "memory")
        }
        
        return locations
    
    def _get_dir_size(self, path: Path) -> Dict[str, Any]:
        """Get directory size and file count"""
        if not path.exists():
            return {"exists": False, "size_mb": 0, "files": 0}
        
        total_size = 0
        file_count = 0
        
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
        except:
            pass
        
        return {
            "exists": True,
            "size_mb": total_size / (1024**2),
            "files": file_count,
            "path": str(path)
        }
    
    def _get_network_status(self, current_time: float) -> Dict[str, Any]:
        """Network statistics"""
        net_io = psutil.net_io_counters()
        
        # Calculate rates
        time_delta = current_time - self.last_check_time
        
        if self.last_net_io and time_delta > 0:
            upload_rate = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta / 1024  # KB/s
            download_rate = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta / 1024  # KB/s
        else:
            upload_rate = 0
            download_rate = 0
        
        self.last_net_io = net_io
        
        status = {
            "bytes_sent_mb": net_io.bytes_sent / (1024**2),
            "bytes_recv_mb": net_io.bytes_recv / (1024**2),
            "upload_rate_kbs": upload_rate,
            "download_rate_kbs": download_rate,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout
        }
        
        return status
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Performance indicators"""
        return {
            "response_time_ms": (time.time() - self.last_check_time) * 1000,
            "cpu_load_1min": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            "cpu_load_5min": psutil.getloadavg()[1] if hasattr(psutil, 'getloadavg') else 0,
            "cpu_load_15min": psutil.getloadavg()[2] if hasattr(psutil, 'getloadavg') else 0,
            "memory_pressure": "low" if psutil.virtual_memory().percent < 70 else "medium" if psutil.virtual_memory().percent < 90 else "high",
            "disk_pressure": "low" if psutil.disk_usage('/').percent < 80 else "medium" if psutil.disk_usage('/').percent < 95 else "high"
        }
    
    def _get_health_status(self) -> Dict[str, Any]:
        """Overall system health"""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=0.1)
        
        issues = []
        if mem.percent > 90:
            issues.append("high_memory_usage")
        if disk.percent > 95:
            issues.append("disk_space_critical")
        if cpu > 95:
            issues.append("cpu_overload")
        
        status = "healthy" if not issues else "warning" if len(issues) < 2 else "critical"
        
        return {
            "status": status,
            "issues": issues,
            "score": 100 - (len(issues) * 20)
        }


# Create global instance
status_monitor = ComprehensiveStatusMonitor()


if __name__ == "__main__":
    # Test the monitor
    print("🔍 Comprehensive Status Monitor Test\n")
    
    status = status_monitor.get_all_status()
    
    print(json.dumps(status, indent=2))
