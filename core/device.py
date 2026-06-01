"""
Device module for NETWATCH PRO
Handles individual network device operations
"""

from ping3 import ping
from datetime import datetime
import time

class Device:
    """Represents a network device with ping capabilities"""
    
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.status = "UNKNOWN"
        self.previous_status = "UNKNOWN"
        self.latency = None
        self.last_check = None
        self.fail_count = 0
        self.success_count = 0
        self.total_checks = 0
    
    def ping_device(self, timeout=2, retry=1):
        """
        Ping the device and update status
        Returns: True if UP, False if DOWN
        """
        self.last_check = datetime.now()
        self.total_checks += 1
        
        try:
            # Try primary ping
            response = ping(self.ip, timeout=timeout)
            
            # Optional retry logic
            if response is None and retry > 0:
                time.sleep(0.5)
                response = ping(self.ip, timeout=timeout)

                self.previous_status = self.status
            
            if response is not None:
                self.status = "UP"
                self.latency = round(response * 1000, 2)  # Convert to ms
                self.success_count += 1
                self.fail_count = 0  # Reset fail count on success
                return True
            else:
                self.status = "DOWN"
                self.latency = None
                self.fail_count += 1
                return False
                
        except Exception as e:
            self.status = "DOWN"
            self.latency = None
            self.fail_count += 1
            return False
    
    def get_uptime_percent(self):
        """Calculate uptime percentage"""
        if self.total_checks == 0:
            return 100.0
        return round((self.success_count / self.total_checks) * 100, 2)
    
    def get_status_icon(self):
        """Return emoji icon for status"""
        icons = {
            "UP": "🟢",
            "DOWN": "🔴",
            "UNKNOWN": "⚪"
        }
        return icons.get(self.status, "❓")
    
    def get_latency_display(self):
        """Format latency for display"""
        if self.latency is None:
            return "---"
        return f"{self.latency}ms"
    
    def __str__(self):
        """String representation of device"""
        icon = self.get_status_icon()
        latency_str = self.get_latency_display()
        return f"{icon} {self.name:<15} | {self.ip:<15} | {self.status:<6} | {latency_str}"
    
    def to_dict(self):
        """Convert device to dictionary for JSON export"""
        return {
            "name": self.name,
            "ip": self.ip,
            "status": self.status,
            "latency": self.latency,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "uptime_percent": self.get_uptime_percent(),
            "total_checks": self.total_checks
        }