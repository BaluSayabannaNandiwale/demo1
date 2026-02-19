import os
import re
import sys
import time
import ctypes
import platform
import subprocess
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
from typing import List, Set, Dict
import psutil

__VERSION__ = "0.0.6"

class VPDError(Exception):
    """Base class for exceptions in VirtualPyDetector."""
    def __init__(self, message):
        super().__init__(message)

class Detector:
    """
    Comprehensive detection system for virtual environments, sandboxes, and debuggers.
    Combines multiple detection techniques across different platforms with multiprocessing.
    """

    class VMChecks:
        """Virtual machine detection methods using hardware and system artifacts."""
        
        @staticmethod
        def check_vm_hardware() -> bool:
            """Detect VM through system hardware information."""
            system = platform.system()
            
            if system == "Windows":
                try:
                    output = subprocess.check_output(
                        ["wmic", "computersystem", "get", "model"],
                        encoding="utf-8",
                        timeout=3
                        )
                    
                    vm_indicators = ("Virtual", "VMware", "VirtualBox", "Hyper-V", "QEMU")
                    
                    return any(indicator in output for indicator in vm_indicators)
                except subprocess.CalledProcessError as e: raise VPDError(f"Error checking VM hardware: {e}")
                except subprocess.TimeoutExpired: return False

            elif system == "Darwin":  # macOS
                try:
                    output = subprocess.check_output(
                        ["sysctl", "hw.model"], 
                        encoding="utf-8", 
                        timeout=3
                    )
                    
                    return any(vm in output for vm in ("VMware", "VirtualBox"))
                
                except subprocess.CalledProcessError as e: raise VPDError(f"Error checking VM hardware: {e}")
                except subprocess.TimeoutExpired: return False

            elif system == "Linux":
                try:
                    output = subprocess.check_output(
                        ["systemd-detect-virt"], 
                        encoding="utf-8", 
                        timeout=3
                    )
                    return output.strip() != "none"
                except subprocess.CalledProcessError as e: raise VPDError(f"Error checking VM hardware: {e}")
                except subprocess.TimeoutExpired: return False
                
            return False

        @staticmethod
        def check_mac_address() -> bool:
            """Check for virtualization-related MAC address prefixes."""
            try:
                command = "getmac" if platform.system() == "Windows" else "ifconfig"
                output = subprocess.check_output(
                    [command], 
                    encoding="utf-8", 
                    timeout=3
                )
                
                mac_pattern = r"(00:05:69|00:0C:29|00:50:56|00:1C:14|00:03:FF|00:05:00)"
                
                return re.search(mac_pattern, output) is not None
            
            except subprocess.CalledProcessError as e: raise VPDError(f"Error checking MAC address: {e}")
            except subprocess.TimeoutExpired: return False

        @staticmethod
        def check_vm_artifacts() -> bool:
            """Check for existence of known virtualization software artifacts."""
            if platform.system() == "Windows":
                vm_paths = [
                    "C:\\Program Files\\VMware\\VMware Tools",
                    "C:\\Program Files\\Oracle\\VirtualBox Guest Additions"
                ]
                return Detector.HelperFunctions.check_paths_exist(vm_paths)
            elif platform.system() == "Darwin":
                vm_paths = [
                    "/Applications/VMware Tools",
                    "/Applications/VirtualBox.app"
                ]
                return Detector.HelperFunctions.check_paths_exist(vm_paths)
            return False

        @staticmethod
        def check_virtualbox_drivers() -> bool:
            """Detect VirtualBox drivers on Windows systems."""
            if platform.system() != "Windows": return False # not windows to be return false

            drivers = [
                "VBoxGuest.sys",
                "VBoxMouse.sys",
                "VBoxSF.sys",
                "VBoxVideo.sys",
                "VBoxNetLwf.sys",
                "VBoxNetAdp.sys",
                "VBoxDrv.sys",
                "VBoxUSBMon.sys",
                "VBoxUSB.sys",
                "VBoxWddm.sys",
                "VBoxMRXNP.sys",
                "VBoxCdd.sys",
                "VBoxEhciR0.sys"
            ]
            
            driver_paths = [f"C:\\Windows\\System32\\drivers\\{driver}" for driver in drivers]
            return Detector.HelperFunctions.check_paths_exist(driver_paths)

        @staticmethod
        def check_cpu_features() -> bool:
            """Detect CPU features indicating virtualization environment."""
            if platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as cpuinfo:
                        return any("hypervisor" in line for line in cpuinfo)
                    
                except FileNotFoundError: return False
                
            elif platform.system() == "Darwin":
                try:
                    output = subprocess.check_output(
                        ["sysctl", "machdep.cpu.features"],
                        encoding="utf-8",
                        timeout=3
                    )
                    return "VMM" in output  # Virtual Machine Monitor flag
                
                except subprocess.CalledProcessError as e: raise VPDError(f"Error checking CPU features: {e}")
                except subprocess.TimeoutExpired: return False
                
            return False

    class DebuggerChecks:
        """Debugger and sandbox detection methods."""
        
        @staticmethod
        def check_hypervisor() -> bool:
            """Detect hypervisor presence using platform-specific APIs."""
            if platform.system() == "Windows":
                try: return bool(ctypes.windll.kernel32.IsHypervisorPresent())
                except (AttributeError, OSError): return False
                
            elif platform.system() == "Darwin":
                try:
                    output = subprocess.check_output(
                        ["sysctl", "kern.hv_support"], 
                        encoding="utf-8", 
                        timeout=3
                    )
                    return "1" in output
                
                except subprocess.CalledProcessError as e: raise VPDError(f"Error checking hypervisor: {e}")
                except subprocess.TimeoutExpired: return False
                
            return False

        @staticmethod
        def check_sandbox_files() -> bool:
            """Check for files/directories indicative of sandbox environments."""
            sandbox_paths = [
                "/Applications/WindowsSandbox.app",  # Hypothetical macOS path
                "C:\\Program Files\\WindowsApps\\Microsoft.WindowsSandbox_"
            ]
            return Detector.HelperFunctions.check_paths_exist(sandbox_paths)

        @staticmethod
        def detect_debugger() -> bool:
            """Detect debugger presence through platform-specific methods."""
            if platform.system() == "Windows":
                try:
                    return bool(ctypes.windll.kernel32.IsDebuggerPresent())
                except (AttributeError, OSError):
                    return False

            elif platform.system() in {"Darwin", "Linux"}:
                try:
                    parent_process = psutil.Process(os.getppid()).name().lower()
                    return parent_process in {"lldb", "gdb"}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return False

            return False

        @staticmethod
        def anti_timing_check(threshold: float = 0.5) -> bool:
            """
            Detect timing anomalies suggestive of virtualization/debugging.
            
            Args:
                threshold: Maximum expected execution time for empty loop (seconds)
            """
            start_time = time.perf_counter()
            for _ in range(1_000_000):
                pass  # Intentional no-op for timing measurement
            elapsed = time.perf_counter() - start_time
            return elapsed > threshold

    class ProcessChecks:
        """Detection of suspicious processes associated with analysis environments."""
        
        @staticmethod
        def detect_suspicious_processes() -> bool:
            """Threaded detection of known sandbox/VM-related processes."""
            suspicious_processes: Set[str] = {
                "vmtoolsd", "vboxservice", "wireshark",
                "fiddler", "sandboxie", "processhacker"
            }

            def process_check(proc: psutil.Process) -> bool:
                try: return proc.info["name"].lower() in suspicious_processes
                except (psutil.NoSuchProcess, psutil.AccessDenied): return False

            with ThreadPoolExecutor() as executor:
                return any(f.result() for f in as_completed([executor.submit(process_check, p) for p in psutil.process_iter(["name"])]))

    class HelperFunctions:
        """Enhanced utility methods with error handling."""
        
        @staticmethod
        def check_paths_exist(paths: List[str]) -> bool:
            """Safely check multiple paths with error handling."""
            for path in paths:
                try:
                    if os.path.exists(path):
                        return True
                except PermissionError:
                    continue
                except OSError:
                    continue
            return False

    @property
    def venv_active(self) -> bool:
        """
        Optimized multiprocess check with batch processing and improved cancellation.
        """
        check_groups = [
            # Group related checks to minimize process creation
            [
                self.VMChecks.check_vm_hardware,
                self.VMChecks.check_mac_address,
                self.VMChecks.check_vm_artifacts,
            ],
            [
                self.VMChecks.check_cpu_features,
                self.DebuggerChecks.check_hypervisor,
                self.DebuggerChecks.check_sandbox_files,
            ],
            [
                self.DebuggerChecks.detect_debugger,
                partial(self.DebuggerChecks.anti_timing_check),
                self.ProcessChecks.detect_suspicious_processes,
            ]
        ]

        try:
            with ProcessPoolExecutor(max_workers=3) as executor:
                futures = []
                for group in check_groups:
                    futures.append(executor.submit(self._run_check_group, group))
                for future in as_completed(futures):
                    if future.result():
                        # Cancel remaining checks
                        for f in futures: f.cancel()
                        return True
            return False
        except Exception as e:
            raise VPDError(f"Multiprocess check failed: {e}")

    def _run_check_group(self, checks: List[callable]) -> bool:
        """Run a group of checks in the current process."""
        return any(check() for check in checks)

    @property
    def is_virtualized(self) -> bool:
        """Check if the environment is virtualized."""
        return any((
            self.VMChecks.check_vm_hardware(),
            self.VMChecks.check_mac_address(),
            self.VMChecks.check_vm_artifacts(),
            self.VMChecks.check_cpu_features(),
        ))

    @property
    def is_debugged(self) -> bool:
        """Check if a debugger is attached."""
        return any((
            self.DebuggerChecks.detect_debugger(),
            self.DebuggerChecks.anti_timing_check(),
        ))

    @property
    def is_sandboxed(self) -> bool:
        """Check if in a sandbox environment."""
        return any((
            self.DebuggerChecks.check_sandbox_files(),
            self.ProcessChecks.detect_suspicious_processes(),
        ))
    
    @property
    def is_analyzed(self) -> bool:
        """
        Check if the environment is under analysis.

        Returns:
            bool: True if an analysis environment is detected, False otherwise.
        """
        return any((
            self.is_virtualized,
            self.is_debugged,
            self.is_sandboxed,
        ))
    
    @property
    def is_safe(self) -> bool:
        """
        Check if the environment is safe.

        Returns:
            bool: True if no analysis environment is detected, False otherwise.
        """
        return not self.is_analyzed
    
    @property
    def is_unsafe(self) -> bool:
        """
        Check if the environment is unsafe.

        Returns:
            bool: True if an analysis environment is detected, False otherwise.
        """
        return self.is_analyzed
    
    @property
    def is_virtual(self) -> bool:
        """
        Check if the environment is virtual.

        Returns:
            bool: True if a virtual environment is detected, False otherwise.
        """
        return self.is_virtualized
    
    @property
    def is_debug(self) -> bool:
        """
        Check if a debugger is attached to the process.

        Returns:
            bool: True if a debugger is detected, False otherwise.
        """
        return self.is_debugged
    
    @property
    def is_sandbox(self) -> bool:
        """
        Check if the environment is a sandbox.

        Returns:
            bool: True if a sandbox environment is detected, False otherwise.
        """
        return self.is_sandboxed
    
    @property
    def is_analysis(self) -> bool:
        """
        Check if the environment is under analysis.

        Returns:
            bool: True if an analysis environment is detected, False otherwise.
        """
        return self.is_analyzed
    
    @property
    def get_all_checks(self) -> Dict[str, bool]:
        """Return comprehensive check results."""
        return {
            "is_virtualized": self.is_virtualized,
            "is_debugged": self.is_debugged,
            "is_sandboxed": self.is_sandboxed,
            "venv_active": self.venv_active,
            "detailed": {
                "vm_hardware": self.VMChecks.check_vm_hardware(),
                "vm_mac": self.VMChecks.check_mac_address(),
                "vm_artifacts": self.VMChecks.check_vm_artifacts(),
                "cpu_features": self.VMChecks.check_cpu_features(),
                "hypervisor": self.DebuggerChecks.check_hypervisor(),
                "sandbox_files": self.DebuggerChecks.check_sandbox_files(),
                "debugger_present": self.DebuggerChecks.detect_debugger(),
                "suspicious_processes": self.ProcessChecks.detect_suspicious_processes(),
                "timing_anomaly": self.DebuggerChecks.anti_timing_check(),
            }
        }
