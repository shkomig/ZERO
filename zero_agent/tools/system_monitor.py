"""
System monitoring for Zero Agent
CPU, memory, disk, and process monitoring
"""

import psutil
import platform
from typing import Dict, List, Optional
from datetime import datetime


class SystemMonitor:
    """System monitoring operations"""
    
    @staticmethod
    def get_cpu_usage(interval: float = 1.0) -> Dict:
        """Get CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=interval)
            cpu_per_core = psutil.cpu_percent(interval=interval, percpu=True)
            cpu_freq = psutil.cpu_freq()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            return {
                "success": True,
                "overall": cpu_percent,
                "per_core": cpu_per_core,
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else 0,
                    "min": cpu_freq.min if cpu_freq else 0,
                    "max": cpu_freq.max if cpu_freq else 0
                },
                "cores": {
                    "logical": cpu_count_logical,
                    "physical": cpu_count_physical
                },
                "status": "high" if cpu_percent > 80 else "normal"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_memory_usage() -> Dict:
        """Get memory usage"""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            return {
                "success": True,
                "ram": {
                    "total": virtual_mem.total,
                    "available": virtual_mem.available,
                    "used": virtual_mem.used,
                    "percent": virtual_mem.percent,
                    "total_gb": round(virtual_mem.total / (1024**3), 2),
                    "available_gb": round(virtual_mem.available / (1024**3), 2),
                    "used_gb": round(virtual_mem.used / (1024**3), 2)
                },
                "swap": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "percent": swap_mem.percent,
                    "total_gb": round(swap_mem.total / (1024**3), 2),
                    "used_gb": round(swap_mem.used / (1024**3), 2)
                },
                "status": "high" if virtual_mem.percent > 85 else "normal"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_disk_usage(path: str = "/") -> Dict:
        """Get disk usage"""
        try:
            disk = psutil.disk_usage(path)
            
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent
                    })
                except PermissionError:
                    continue
            
            return {
                "success": True,
                "main_disk": {
                    "path": path,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2)
                },
                "partitions": partitions,
                "status": "low" if disk.percent > 90 else "normal"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_process_list(sort_by: str = "memory") -> Dict:
        """Get running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "user": pinfo['username'],
                        "memory_percent": round(pinfo['memory_percent'], 2),
                        "cpu_percent": round(pinfo['cpu_percent'], 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            top_processes = processes[:10]
            
            return {
                "success": True,
                "total_processes": len(processes),
                "top_processes": top_processes,
                "sorted_by": sort_by
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get general system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            return {
                "success": True,
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": (datetime.now() - boot_time).total_seconds()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_full_report(cls) -> Dict:
        """Get complete system report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": cls.get_system_info(),
            "cpu": cls.get_cpu_usage(),
            "memory": cls.get_memory_usage(),
            "disk": cls.get_disk_usage("C:\\" if platform.system() == "Windows" else "/"),
            "processes": cls.get_process_list()
        }

