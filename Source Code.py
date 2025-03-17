from colorama import Style, Fore, Back, init
from time import sleep
from os import system, path, chmod
import win32com.client
import re
import ctypes
import sys

init(autoreset=True)

vid_pattern = re.compile(r"HoodLoader2atmega16u2\.vid(\.\d+)?=0x[0-9A-F]+")
pid_pattern = re.compile(r"HoodLoader2atmega16u2\.pid(\.\d+)?=0x[0-9A-F]+")
name_pattern = re.compile(r"HoodLoader2atmega16u2\.name=.*")
usb_product_pattern = re.compile(r"HoodLoader2atmega16u2\.build\.usb_product=.*")
build_vid_pattern = re.compile(r"HoodLoader2atmega16u2\.build\.vid=0x[0-9A-F]+")
build_pid_pattern = re.compile(r"HoodLoader2atmega16u2\.build\.pid=0x[0-9A-F]+")
extra_flags_pattern = re.compile(r"HoodLoader2atmega16u2\.build\.extra_flags=\{build\.usb_flags\}")

def list_mice_devices():
    wmi = win32com.client.GetObject("winmgmts:")
    devices = wmi.InstancesOf("Win32_PointingDevice")
    return [(d.Name, *re.search(r'VID_(\w+)&PID_(\w+)', d.PNPDeviceID).groups() if re.search(r'VID_(\w+)&PID_(\w+)', d.PNPDeviceID) else (None, None)) for d in devices]

def spoofarduino():
    system("cls")
    print(Fore.CYAN + Back.BLACK + "[+] Obee's HoodLoader2 Spoofer [+]")
    print(Fore.YELLOW + "\nSelect your mouse...")
    print(Fore.GREEN + "[?] Check your mouse's VID and PID from Control Panel.")
    select_mouse_and_configure()

def select_mouse_and_configure():
    print(Fore.MAGENTA + "\nScanning for mice devices...")
    mice = list_mice_devices()
    if not mice:
        print(Fore.RED + "No mouse devices found. Exiting...")
        sleep(3)
        exit()
    
    for i, (name, vid, pid) in enumerate(mice, 1):
        print(Fore.BLUE + f"{i} → {Fore.WHITE}{name} {Fore.YELLOW}| VID: {vid or 'N/A'}, PID: {pid or 'N/A'}")
    
    choice = int(input(Fore.CYAN + "Select your mouse number: ")) - 1
    name, vid, pid = mice[choice]
    name = input(Fore.CYAN + "Enter your mouse's name: ")
    com_choice = input(Fore.YELLOW + "Disable COM port? (Y/N): ").strip().upper()
    replace_and_save_boards_txt("0x" + vid, "0x" + pid, name, com_choice)

def replace_and_save_boards_txt(mouse_vid, mouse_pid, mouse_name, com_choice):
    file_path = path.expandvars("%LOCALAPPDATA%/Arduino15/packages/HoodLoader2/hardware/avr/2.0.5/boards.txt")
    if not path.exists(file_path):
        print(Fore.RED + f"File not found: {file_path}")
        sleep(3)
        return
    
    try:
        chmod(file_path, 0o777)
        with open(file_path, 'r') as file:
            lines = file.readlines()
        with open(file_path, 'w') as file:
            for line in lines:
                if vid_pattern.match(line):
                    line = f"HoodLoader2atmega16u2.vid={mouse_vid}\n"
                elif pid_pattern.match(line):
                    line = f"HoodLoader2atmega16u2.pid={mouse_pid}\n"
                elif build_vid_pattern.match(line):
                    line = f"HoodLoader2atmega16u2.build.vid={mouse_vid}\n"
                elif build_pid_pattern.match(line):
                    line = f"HoodLoader2atmega16u2.build.pid={mouse_pid}\n"
                elif name_pattern.match(line) or usb_product_pattern.match(line):
                    line = f"HoodLoader2atmega16u2.name={mouse_name}\n" if 'name' in line else f'HoodLoader2atmega16u2.build.usb_product="{mouse_name}"\n'
                elif extra_flags_pattern.match(line):
                    line = 'HoodLoader2atmega16u2.build.extra_flags={build.usb_flags} -DCDC_DISABLED\n' if com_choice == 'Y' else 'HoodLoader2atmega16u2.build.extra_flags={build.usb_flags}\n'
                file.write(line)
        chmod(file_path, 0o444)
        print(Fore.GREEN + "\n[SUCCESS] HoodLoader2 spoofing applied!")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        sleep(3)
    sleep(3)

if __name__ == "__main__":
    spoofarduino()
