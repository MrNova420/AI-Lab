#!/usr/bin/env python3
"""
📊 Resource Monitor - Real-time CPU/GPU/Memory Monitoring
Live stats for AI performance tracking
"""

import psutil
import time
from typing import Dict, Optional
from datetime import datetime

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️ GPU monitoring not available (pip install gputil)")


class ResourceMonitor:
    """Monitor CPU, GPU, Memory, and Disk usage"""
    
    def __init__(self):
        self.gpu_available = GPU_AVAILABLE
        self.current_device = 'cpu'
        self.cpu_threads = psutil.cpu_count()
        self.memory_limit_gb = 8.0
        
        # Usage limiters
        self.usage_limiter_enabled = False
        self.safety_buffer_enabled = True
        self.max_gpu_usage_percent = 100
        self.max_cpu_usage_percent = 100
        self.gpu_safety_buffer = 10
        self.cpu_safety_buffer = 5
        
        print("📊 Resource Monitor initialized")
        if self.gpu_available:
            print("   ✅ GPU monitoring enabled")
        else:
            print("   ⚠️ GPU monitoring disabled (install gputil)")
    
    def get_cpu_usage(self) -> Dict:
        """Get CPU usage statistics"""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage_percent': cpu_percent,
            'cores': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else 0,
            'max_frequency_mhz': cpu_freq.max if cpu_freq else 0
        }
    
    def get_gpu_usage(self) -> Dict:
        """Get GPU usage statistics"""
        if not self.gpu_available:
            return {
                'available': False,
                'message': 'GPU monitoring not available'
            }
        
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {
                    'available': False,
                    'message': 'No GPUs detected'
                }
            
            gpu = gpus[0]  # Primary GPU
            return {
                'available': True,
                'name': gpu.name,
                'usage_percent': gpu.load * 100,
                'memory_used_mb': gpu.memoryUsed,
                'memory_total_mb': gpu.memoryTotal,
                'memory_percent': (gpu.memoryUsed / gpu.memoryTotal * 100) if gpu.memoryTotal > 0 else 0,
                'temperature_c': gpu.temperature
            }
        except Exception as e:
            return {
                'available': False,
                'message': f'GPU error: {str(e)}'
            }
    
    def get_memory_usage(self) -> Dict:
        """Get RAM usage statistics"""
        mem = psutil.virtual_memory()
        
        return {
            'total_gb': mem.total / (1024**3),
            'used_gb': mem.used / (1024**3),
            'available_gb': mem.available / (1024**3),
            'percent': mem.percent
        }
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage statistics"""
        disk = psutil.disk_usage('/')
        
        return {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': disk.percent
        }
    
    def get_all_stats(self) -> Dict:
        """Get all resource statistics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.get_cpu_usage(),
            'gpu': self.get_gpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage()
        }
    
    def get_live_stats(self) -> Dict:
        """Get formatted live stats for display"""
        stats = self.get_all_stats()
        
        return {
            'cpu': f"{stats['cpu']['usage_percent']:.1f}%",
            'gpu': f"{stats['gpu']['usage_percent']:.1f}%" if stats['gpu']['available'] else 'N/A',
            'memory': f"{stats['memory']['percent']:.1f}%",
            'disk': f"{stats['disk']['percent']:.1f}%"
        }


class PerformanceController:
    """Control AI performance and resource allocation"""
    
    def __init__(self):
        self.current_device = 'cpu'  # 'cpu' or 'gpu'
        self.cpu_threads = psutil.cpu_count()
        self.max_memory_gb = 8
        self.temperature_limit = 85
        
        # Usage limiters
        self.usage_limiter_enabled = False
        self.safety_buffer_enabled = True
        self.max_gpu_usage_percent = 100
        self.max_cpu_usage_percent = 100
        self.gpu_safety_buffer = 10
        self.cpu_safety_buffer = 5
        
        print("🎛️ Performance Controller initialized")
        print(f"   Device: {self.current_device.upper()}")
        print(f"   CPU Threads: {self.cpu_threads}")
    
    def switch_device(self, device: str) -> Dict:
        """Switch between CPU and GPU"""
        if device not in ['cpu', 'gpu']:
            return {
                'success': False,
                'message': 'Invalid device. Use "cpu" or "gpu"'
            }
        
        old_device = self.current_device
        self.current_device = device
        
        return {
            'success': True,
            'old_device': old_device,
            'new_device': device,
            'message': f'Switched from {old_device.upper()} to {device.upper()}'
        }
    
    def set_cpu_threads(self, threads: int) -> Dict:
        """Set number of CPU threads to use"""
        max_threads = psutil.cpu_count()
        
        if threads < 1 or threads > max_threads:
            return {
                'success': False,
                'message': f'Threads must be between 1 and {max_threads}'
            }
        
        old_threads = self.cpu_threads
        self.cpu_threads = threads
        
        return {
            'success': True,
            'old_threads': old_threads,
            'new_threads': threads,
            'message': f'CPU threads set to {threads}'
        }
    
    def set_memory_limit(self, memory_gb: int) -> Dict:
        """Set memory limit in GB"""
        total_memory = psutil.virtual_memory().total / (1024**3)
        
        if memory_gb < 1 or memory_gb > total_memory:
            return {
                'success': False,
                'message': f'Memory must be between 1 and {total_memory:.0f} GB'
            }
        
        old_limit = self.max_memory_gb
        self.max_memory_gb = memory_gb
        
        return {
            'success': True,
            'old_limit': old_limit,
            'new_limit': memory_gb,
            'message': f'Memory limit set to {memory_gb} GB'
        }
    
    def get_current_settings(self) -> Dict:
        """Get current performance settings"""
        total_memory = psutil.virtual_memory().total / (1024**3)
        
        # Calculate actual usage with safety buffer
        actual_gpu_usage = self.max_gpu_usage_percent
        actual_cpu_usage = self.max_cpu_usage_percent
        
        if self.safety_buffer_enabled:
            actual_gpu_usage = max(0, self.max_gpu_usage_percent - self.gpu_safety_buffer)
            actual_cpu_usage = max(0, self.max_cpu_usage_percent - self.cpu_safety_buffer)
        
        return {
            'device': self.current_device.upper(),
            'cpu_threads': self.cpu_threads,
            'max_threads': psutil.cpu_count(),
            'memory_limit_gb': self.max_memory_gb,
            'total_memory_gb': total_memory,
            'temperature_limit': self.temperature_limit,
            'use_gpu': self.current_device == 'gpu',
            'num_gpu': 1 if self.current_device == 'gpu' else 0,
            'num_threads': 8,
            'max_gpu_usage_percent': self.max_gpu_usage_percent,
            'max_cpu_usage_percent': self.max_cpu_usage_percent,
            'gpu_usage_percent': self.max_gpu_usage_percent,
            'cpu_usage_percent': self.max_cpu_usage_percent,
            'usage_limiter_enabled': self.usage_limiter_enabled,
            'safety_buffer_enabled': self.safety_buffer_enabled,
            'gpu_safety_buffer': self.gpu_safety_buffer,
            'cpu_safety_buffer': self.cpu_safety_buffer,
            'actual_gpu_usage': actual_gpu_usage,
            'actual_cpu_usage': actual_cpu_usage
        }
    
    def get_recommendations(self, stats: Dict) -> list:
        """Get performance recommendations"""
        recommendations = []
        
        cpu = stats.get('cpu', {})
        gpu = stats.get('gpu', {})
        memory = stats.get('memory', {})
        
        # CPU recommendations
        if cpu.get('usage_percent', 0) > 90:
            recommendations.append({
                'type': 'warning',
                'message': 'High CPU usage detected. Consider reducing load or upgrading hardware.'
            })
        
        # GPU recommendations
        if gpu.get('available') and gpu.get('usage_percent', 0) < 20 and self.current_device == 'gpu':
            recommendations.append({
                'type': 'info',
                'message': 'Low GPU usage. Ensure GPU acceleration is properly configured.'
            })
        
        if not gpu.get('available') and self.current_device == 'gpu':
            recommendations.append({
                'type': 'error',
                'message': 'GPU not available. Switching to CPU is recommended.'
            })
        
        # Memory recommendations
        if memory.get('percent', 0) > 85:
            recommendations.append({
                'type': 'warning',
                'message': 'High memory usage. Consider closing other applications.'
            })
        
        # Temperature warnings
        if gpu.get('temperature_c', 0) > self.temperature_limit:
            recommendations.append({
                'type': 'critical',
                'message': f'GPU temperature too high ({gpu["temperature_c"]}°C). Reduce load or improve cooling.'
            })
        
        return recommendations


# Global instances
_monitor = None
_controller = None

def get_monitor():
    """Get or create resource monitor"""
    global _monitor
    if _monitor is None:
        _monitor = ResourceMonitor()
    return _monitor

def get_controller():
    """Get or create performance controller"""
    global _controller
    if _controller is None:
        _controller = PerformanceController()
    return _controller


if __name__ == "__main__":
    print("🧪 Testing Resource Monitor\n")
    
    monitor = ResourceMonitor()
    controller = PerformanceController()
    
    # Get stats
    stats = monitor.get_all_stats()
    print("\n📊 Resource Statistics:")
    print(f"   CPU: {stats['cpu']['usage_percent']}%")
    print(f"   Memory: {stats['memory']['percent']}%")
    print(f"   GPU: {stats['gpu']}")
    
    # Test controller
    print("\n🎛️ Performance Settings:")
    settings = controller.get_current_settings()
    print(f"   Device: {settings['device']}")
    print(f"   CPU Threads: {settings['cpu_threads']}/{settings['max_threads']}")
    print(f"   Memory Limit: {settings['memory_limit_gb']} GB")
    
    # Get recommendations
    recs = controller.get_recommendations(stats)
    if recs:
        print("\n💡 Recommendations:")
        for rec in recs:
            print(f"   [{rec['type'].upper()}] {rec['message']}")
    
    print("\n✅ Test complete!")
