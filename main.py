"""
NETWATCH PRO - Network Device Monitor
Author: I JAGADESH CSE
Cisco Python Essentials 1 & 2 Certified
"""

from core.device import Device
from datetime import datetime
from core.logger import Logger
import time
import os
import sys

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:  
    COLORS_AVAILABLE = False
    # Define dummy color classes
    class Fore:
        GREEN = CYAN = RED = YELLOW = WHITE = MAGENTA = ""
    class Style:
        RESET_ALL = ""

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
print(f"{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN}🌐 NETWATCH PRO - Network Device Monitor")
print(f"{Fore.CYAN}{'='*60}")
print(f"{Fore.WHITE}Intelligent Network Monitoring System")
print(f"{Fore.CYAN}{'='*60}\n")

def load_devices(filename="devices.txt"):
    """Load devices from file with error handling"""
    devices = []
    skipped_lines = 0
    
    try:
        with open(filename, "r") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    # Handle both comma and space separation
                    if ',' in line:
                        name, ip = line.split(",", 1)
                    else:
                        parts = line.split()
                        if len(parts) >= 2:
                            name, ip = parts[0], parts[1]
                        else:
                            raise ValueError("Invalid format")
                    
                    name = name.strip()
                    ip = ip.strip()
                    
                    # Basic IP validation
                    if ip and not ip.startswith('#'):
                        device = Device(name, ip)
                        devices.append(device)
                        print(f"{Fore.GREEN}✅ Loaded: {name} ({ip})")
                    else:
                        skipped_lines += 1
                        
                except ValueError as e:
                    print(f"{Fore.YELLOW}⚠️ Line {line_num}: Skipped - {e}")
                    skipped_lines += 1
                    
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Error: {filename} not found!")
        print(f"{Fore.YELLOW}💡 Creating sample devices.txt...")
        
        # Create sample file
        with open(filename, "w") as f:
            f.write("# NETWATCH PRO - Device List\n")
            f.write("# Format: Device Name,IP Address\n\n")
            f.write("Google DNS,8.8.8.8\n")
            f.write("Cloudflare,1.1.1.1\n")
            f.write("OpenDNS,208.67.222.222\n")
            f.write("# Router,192.168.1.1\n")
        
        print(f"{Fore.GREEN}✅ Created sample {filename}")
        print(f"{Fore.CYAN}💡 Edit the file and run again\n")
        return []
    
    if skipped_lines > 0:
        print(f"{Fore.YELLOW}⚠️ Skipped {skipped_lines} invalid lines")
    
    return devices

def ping_all_devices(devices):
    """Ping all devices and collect results"""
    results = {"UP": 0, "DOWN": 0, "UNKNOWN": 0}
    
    for device in devices:
        device.ping_device()
        
        Logger.write_log(device)
        results[device.status] += 1
        
    
    return results

def print_results(devices, results, check_number):
    """Display ping results in formatted table"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{Fore.WHITE}📊 Check #{check_number} at {current_time}")
    print(f"{Fore.WHITE}{'─'*55}")
    
    # Header
    print(f"{Fore.MAGENTA}{'ICON':<4} {'NAME':<18} {'IP':<16} {'STATUS':<8} {'LATENCY':<10}")
    print(f"{Fore.WHITE}{'─'*55}")
    
    # Device rows
    for device in devices:
        icon = device.get_status_icon()
        color = Fore.GREEN if device.status == "UP" else Fore.RED if device.status == "DOWN" else Fore.YELLOW
        latency_display = f"{device.latency}ms" if device.latency else "---"
        print(f"{color}{icon:<4} {device.name:<18} {device.ip:<16} {device.status:<8} {latency_display:<10}{Style.RESET_ALL}")
    
    print(f"{Fore.WHITE}{'─'*55}")
    
    # Summary
    up_count = results["UP"]
    down_count = results["DOWN"]
    total = len(devices)
    
    up_percent = (up_count / total * 100) if total > 0 else 0
    
    print(f"\n{Fore.GREEN}🟢 UP: {up_count}")
    print(f"{Fore.RED}🔴 DOWN: {down_count}")
    print(f"{Fore.CYAN}📊 Uptime: {up_percent:.1f}%")
    
    # Show devices with high failure rate (if any)
    failing_devices = [d for d in devices if d.fail_count > 3]
    if failing_devices:
        print(f"\n{Fore.YELLOW}⚠️ Devices with repeated failures:")
        for device in failing_devices:
            print(f"   {device.name}: {device.fail_count} consecutive failures")

def print_statistics(devices):
    """Print detailed statistics for all devices"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}📈 DETAILED STATISTICS")
    print(f"{Fore.CYAN}{'='*60}")
    
    for device in devices:
        if device.total_checks > 0:
            uptime = device.get_uptime_percent()
            status_color = Fore.GREEN if uptime > 95 else Fore.YELLOW if uptime > 70 else Fore.RED
            
            print(f"\n{Fore.WHITE}📡 {device.name} ({device.ip})")
            print(f"   Status: {device.get_status_icon()} {device.status}")
            print(f"   Checks performed: {device.total_checks}")
            print(f"   Successful: {device.success_count}")
            print(f"   Failed: {device.fail_count}")
            print(f"   {status_color}Uptime: {uptime}%{Style.RESET_ALL}")
            if device.latency:
                print(f"   Current latency: {device.latency}ms")

def export_report(devices):
    """Export monitoring report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"report_{timestamp}.txt"
    
    try:
        with open(report_file, 'w') as f:
            f.write("NETWATCH PRO - Monitoring Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            
            for device in devices:
                f.write(f"Device: {device.name}\n")
                f.write(f"IP: {device.ip}\n")
                f.write(f"Status: {device.status}\n")
                f.write(f"Latency: {device.get_latency_display()}\n")
                f.write(f"Uptime: {device.get_uptime_percent()}%\n")
                f.write(f"Total Checks: {device.total_checks}\n")
                f.write("-"*30 + "\n")
        
        print(f"{Fore.GREEN}✅ Report exported to {report_file}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to export report: {e}")
        return False

def interactive_menu(devices):
    """Show interactive menu for user choices"""
    while True:
        print(f"\n{Fore.CYAN}{'─'*40}")
        print(f"{Fore.CYAN}🎮 OPTIONS MENU")
        print(f"{Fore.CYAN}{'─'*40}")
        print(f"{Fore.WHITE}1. {Fore.GREEN}Start Monitoring")
        print(f"{Fore.WHITE}2. {Fore.CYAN}View Statistics")
        print(f"{Fore.WHITE}3. {Fore.YELLOW}Export Report")
        print(f"{Fore.WHITE}4. {Fore.MAGENTA}Re-ping All Devices")
        print(f"{Fore.WHITE}5. {Fore.RED}Exit")
        print(f"{Fore.CYAN}{'─'*40}")
        
        choice = input(f"{Fore.WHITE}Enter choice (1-5): ").strip()
        
        if choice == '1':
            return True
        elif choice == '2':
            print_statistics(devices)
        elif choice == '3':
            export_report(devices)
        elif choice == '4':
            print(f"\n{Fore.YELLOW}🔄 Re-pinging all devices...")
            for device in devices:
                device.ping_device()
            print(f"{Fore.GREEN}✅ Done!")
            print_results(devices, ping_all_devices(devices), "Manual")
        elif choice == '5':
            print(f"\n{Fore.GREEN}👋 Goodbye from NETWATCH PRO!")
            return False
        else:
            print(f"{Fore.RED}❌ Invalid choice. Try again.")
def check_alerts(devices):

    for device in devices:

        if device.previous_status == "UNKNOWN":
            continue

        if (
            device.previous_status == "UP"
            and device.status == "DOWN"
        ):

            print(
                f"\n🚨 ALERT: "
                f"{device.name} "
                f"has gone DOWN!"
            )

        elif (
            device.previous_status == "DOWN"
            and device.status == "UP"
        ):

            print(
                f"\n✅ RECOVERED: "
                f"{device.name} "
                f"is back ONLINE!"
            )

def run_monitoring(devices, interval=60):
    """Run continuous monitoring"""
    check_number = 0
    
    try:
        while True:
            check_number += 1
            clear_screen()
            print_header()
            
            # Ping all devices
            results = ping_all_devices(devices)
            check_alerts(devices)
            
            # Display results
            print_results(devices, results, check_number)
            Logger.write_summary(
    devices,
    results,
    check_number
)
            
            # Show next check time
            next_time = datetime.now().timestamp() + interval
            next_time_str = datetime.fromtimestamp(next_time).strftime("%H:%M:%S")
            print(f"\n{Fore.YELLOW}⏰ Next check at {next_time_str}")
            print(f"{Fore.CYAN}💡 Press Ctrl+C to stop and return to menu")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}🛑 Monitoring paused")
        return True  # Return to menu
    

def main():
    """Main entry point"""
    clear_screen()
    print_header()
    
    # Load devices
    print(f"{Fore.CYAN}📂 Loading devices...\n")
    devices = load_devices()
    
    if not devices:
        print(f"{Fore.RED}❌ No devices loaded. Exiting.")
        return
    
    print(f"\n{Fore.GREEN}✅ Loaded {len(devices)} devices successfully")
    
    # Run interactive menu
    while True:
        should_monitor = interactive_menu(devices)
        if not should_monitor:
            break
        
        # Start monitoring
        continue_monitoring = run_monitoring(devices, interval=60)
        if not continue_monitoring:
            break
    
    # Final statistics on exit
    print_statistics(devices)
    export_report(devices)
    

if __name__ == "__main__":
    main()
    