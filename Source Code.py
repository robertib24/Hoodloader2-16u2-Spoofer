from colorama import Style, Fore
from time import sleep
from os import system, path, chmod
import win32com.client
import re
import ctypes
import sys

# Update patterns for HoodLoader2 Uno 16u2
vid_pattern = re.compile(r"HoodLoader2atmega16u2\.vid(\.\d+)?=0x[0-9A-F]+")
pid_pattern = re.compile(r"HoodLoader2atmega16u2\.pid(\.\d+)?=0x[0-9A-F]+")
name_pattern = re.compile(r'HoodLoader2atmega16u2\.name=.*')
usb_product_pattern = re.compile(r'HoodLoader2atmega16u2\.build\.usb_product=.*')
build_vid_pattern = re.compile(r'HoodLoader2atmega16u2\.build\.vid=0x[0-9A-F]+')
build_pid_pattern = re.compile(r'HoodLoader2atmega16u2\.build\.pid=0x[0-9A-F]+')
extra_flags_pattern = re.compile(r'HoodLoader2atmega16u2\.build\.extra_flags=\{build\.usb_flags\}')

def list_mice_devices():
    wmi = win32com.client.GetObject("winmgmts:")
    devices = wmi.InstancesOf("Win32_PointingDevice")
    mice_list = []

    for device in devices:
        name = device.Name
        match = re.search(r'VID_(\w+)&PID_(\w+)', device.PNPDeviceID)

        vid, pid = match.groups() if match else (None, None)
        mice_list.append((name, vid, pid))

    return mice_list

def spoofarduino():
    system("cls")
    print(Style.BRIGHT + Fore.CYAN + "[+] obee's HoodLoader2 Spoofer (Special thx to Seconb) [+]")
    print(Style.BRIGHT + Fore.YELLOW + "\nSelect your mouse...")
    print(Style.BRIGHT + Fore.GREEN + "[?] Don't know which one's your mouse? Open Control Panel, click View devices and printers, right click your mouse, go to properties, hardware, properties again, details tab, and check the Device instance path to see the PID and VID")
    select_mouse_and_configure()

def select_mouse_and_configure():
    print(Fore.CYAN + "\nDetecting mice devices...")
    mice = list_mice_devices()

    if not mice:
        print(Fore.RED + "No mouse devices found. Exiting...")
        sleep(5)
        exit()

    for idx, (name, vid, pid) in enumerate(mice, 1):
        print(f"{Fore.CYAN}{idx} →{Fore.RESET} {name} | VID: {vid or 'Not found'}, PID: {pid or 'Not found'}")

    choice = int(input(Fore.CYAN + "Select your mouse number: ")) - 1
    name, vid, pid = mice[choice]
    name = input(Fore.CYAN + "What is your mouse's name?: ")
    com_choice = input(Fore.YELLOW + "Disable COM port? (Recommended) Y/N: ").strip().upper()
    replace_and_save_boards_txt("0x" + vid, "0x" + pid, name, com_choice)

def replace_and_save_boards_txt(mouse_vid, mouse_pid, mouse_name, com_choice):
    print(f"{Fore.BLUE}Configuring HoodLoader2 spoofing with VID: {mouse_vid}, PID: {mouse_pid}, Name: {mouse_name}")
    file_path = path.expandvars("%LOCALAPPDATA%/Arduino15/packages/HoodLoader2/hardware/avr/2.0.5/boards.txt")

    if not path.exists(file_path):
        print(Fore.RED + f"File not found: {file_path}")
        sleep(5)
        return

    try:
        chmod(file_path, 0o777)  # make sure the file isn't read-only before editing
        
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
                    if 'name' in line:
                        line = f"HoodLoader2atmega16u2.name={mouse_name}\n"
                    else:
                        line = f'HoodLoader2atmega16u2.build.usb_product="{mouse_name}"\n'
                elif com_choice.upper() == 'Y' and extra_flags_pattern.match(line):
                    line = 'HoodLoader2atmega16u2.build.extra_flags={build.usb_flags} -DCDC_DISABLED\n'
                elif com_choice.upper() == 'N' and extra_flags_pattern.match(line):
                    line = 'HoodLoader2atmega16u2.build.extra_flags={build.usb_flags}\n'
                file.write(line)

        chmod(file_path, 0o444)  # set it to read-only
        print(f"{Fore.GREEN}Successfully modified: {file_path}")
    except Exception as e:
        print(f"{Fore.RED}Error modifying {file_path}: {e}")
        sleep(5)
        return

    print(f"{Fore.BLUE}Spoofing complete.")
    sleep(5)

if __name__ == "__main__":
    spoofarduino()
