"""
Logger module for NETWATCH PRO
Handles logging of device status to files
"""

from datetime import datetime
import os
from typing import List

class Logger:
    @staticmethod
    def write_log(device):
       
       try:

        os.makedirs("logs", exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        latency = (
            f"{device.latency}ms"
            if device.latency is not None
            else "---"
        )

        with open(
            "logs/network_log.txt",
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"{timestamp} | "
                f"{device.name} | "
                f"{device.ip} | "
                f"{device.status} | "
                f"{latency}\n"
            )

       except Exception as e:
        
        print("LOGGER ERROR:", e)
    
    @staticmethod
    def write_batch_log(devices: List):
        """
        Write status of multiple devices to log file with header
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/network_log.txt", "a", encoding="utf-8") as file:
            # Write header for this batch
            file.write(f"\n{'='*60}\n")
            file.write(f"CHECK AT: {timestamp}\n")
            file.write(f"{'='*60}\n")
            
            # Write each device status
            for device in devices:
                log_line = (
                    f"{timestamp} | "
                    f"{device.name} | "
                    f"{device.ip} | "
                    f"{device.status} | "
                    f"{device.latency}\n"
                )
                file.write(log_line)
    
    @staticmethod
    def write_alert(device, message: str):
        """
        Write alert to separate alert log file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        alert_line = (
            f"{timestamp} | "
            f"⚠️ ALERT | "
            f"{device.name} | "
            f"{device.ip} | "
            f"{message}\n"
        )
        
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/alerts.txt", "a", encoding="utf-8") as file:
            file.write(alert_line)
        
        # Also print to console with alert formatting
        print(f"\n⚠️ ALERT LOGGED: {device.name} ({device.ip}) - {message}")
    
    @staticmethod
    def write_summary(devices: List, results: dict, check_number: int):
        """
        Write summary of monitoring check
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/summary.txt", "a", encoding="utf-8") as file:
            file.write(f"\n[{timestamp}] CHECK #{check_number}\n")
            file.write(f"  UP: {results['UP']}\n")
            file.write(f"  DOWN: {results['DOWN']}\n")
            file.write(f"  Total: {len(devices)}\n")
            
            # List down devices if any
            if results['DOWN'] > 0:
                file.write(f"  DOWN Devices:\n")
                for device in devices:
                    if device.status == "DOWN":
                        file.write(f"    - {device.name} ({device.ip})\n")
    
    @staticmethod
    def get_log_summary() -> dict:
        """
        Read log file and return summary statistics
        """
        log_file = "logs/network_log.txt"
        
        if not os.path.exists(log_file):
            return {"error": "No log file found"}
        
        stats = {
            "total_checks": 0,
            "up_events": 0,
            "down_events": 0,
            "devices": {}
        }
        
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                for line in file:
                    if " | " in line and not line.startswith("="):
                        parts = line.split(" | ")
                        if len(parts) >= 5:
                            device_name = parts[1].strip()
                            status = parts[3].strip()
                            
                            stats["total_checks"] += 1
                            
                            if status == "UP":
                                stats["up_events"] += 1
                            elif status == "DOWN":
                                stats["down_events"] += 1
                            
                            if device_name not in stats["devices"]:
                                stats["devices"][device_name] = {"up": 0, "down": 0}
                            
                            if status == "UP":
                                stats["devices"][device_name]["up"] += 1
                            elif status == "DOWN":
                                stats["devices"][device_name]["down"] += 1
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def rotate_logs(max_size_mb: int = 5):
        """
        Rotate log file if it exceeds max size
        """
        log_file = "logs/network_log.txt"
        
        if os.path.exists(log_file):
            size_mb = os.path.getsize(log_file) / (1024 * 1024)
            
            if size_mb > max_size_mb:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"logs/network_log_{timestamp}.txt"
                
                os.rename(log_file, backup_file)
                print(f"📦 Log rotated: {backup_file}")
                
                # Create new empty log file
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"# New log file created at {datetime.now()}\n")
                
                return True
        return False
    
    @staticmethod
    def clear_logs():
        """
        Clear all log files (with confirmation)
        """
        confirm = input("⚠️ Delete all logs? (yes/no): ")
        
        if confirm.lower() == "yes":
            log_files = ["logs/network_log.txt", "logs/alerts.txt", "logs/summary.txt"]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    os.remove(log_file)
                    print(f"✅ Deleted: {log_file}")
            
            print("🎯 All logs cleared!")
            return True
        
        print("❌ Cancelled")
        return False