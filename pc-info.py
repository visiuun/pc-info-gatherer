import platform
import os
import subprocess
import re
import socket
import winreg  # Import the Windows registry module (only for Windows)

def get_pc_info():
    """Gathers and organizes comprehensive information about the PC."""

    info = {}

    # 1. Operating System Information
    info['os'] = {}
    info['os']['system'] = platform.system()
    info['os']['version'] = platform.version()
    info['os']['release'] = platform.release()
    info['os']['architecture'] = platform.machine()
    info['os']['processor'] = platform.processor()
    info['os']['name'] = platform.node()

    # 2. CPU Information
    info['cpu'] = {}
    try:
        if info['os']['system'] == "Windows":
            # Get CPU name from the registry (more reliable)
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0")
                cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                winreg.CloseKey(key)
            except Exception as e:
                cpu_name = f"Error getting CPU name from registry: {e}"

            output = subprocess.check_output("wmic cpu get CurrentClockSpeed, L2CacheSize, L3CacheSize, MaxClockSpeed, DataWidth, NumberOfCores, NumberOfLogicalProcessors, SocketDesignation, Manufacturer, Family, DeviceID /Value", shell=True).decode()

            speeds = re.findall(r"CurrentClockSpeed=(.+)", output)
            l2s = re.findall(r"L2CacheSize=(.+)", output)
            l3s = re.findall(r"L3CacheSize=(.+)", output)
            max_speeds = re.findall(r"MaxClockSpeed=(.+)", output)
            data_widths = re.findall(r"DataWidth=(.+)", output)
            num_cores = re.findall(r"NumberOfCores=(.+)", output)
            num_logical = re.findall(r"NumberOfLogicalProcessors=(.+)", output)
            socket_designations = re.findall(r"SocketDesignation=(.+)", output)
            manufacturer = re.findall(r"Manufacturer=(.+)", output)
            family = re.findall(r"Family=(.+)", output)
            device_id = re.findall(r"DeviceID=(.+)", output) #cpu name

            info['cpu']['name'] = cpu_name
            info['cpu']['current_clock_speed'] = int(speeds[0].strip()) if speeds else "N/A"
            info['cpu']['l2_cache_size'] = int(l2s[0].strip()) if l2s else "N/A"
            info['cpu']['l3_cache_size'] = int(l3s[0].strip()) if l3s else "N/A"
            info['cpu']['max_clock_speed'] = int(max_speeds[0].strip()) if max_speeds else "N/A"
            info['cpu']['architecture'] = data_widths[0].strip() if data_widths else "N/A"
            info['cpu']['cores'] = int(num_cores[0].strip()) if num_cores else "N/A"
            info['cpu']['threads'] = int(num_logical[0].strip()) if num_logical else "N/A" # added logical processors (threads)
            info['cpu']['socket'] = socket_designations[0].strip() if socket_designations else "N/A"  # Socket information
            info['cpu']['manufacturer'] = manufacturer[0].strip() if manufacturer else "N/A" #Added manufacturer (e.g. Intel, AMD)
            info['cpu']['family'] = family[0].strip() if family else "N/A"
            info['cpu']['device_id'] = device_id[0].strip() if device_id else "N/A" #Alternate cpu name

        elif info['os']['system'] == "Darwin":
             cpu_name = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode().strip()
             info['cpu']['name'] = cpu_name

             info['cpu']['current_clock_speed'] = subprocess.check_output("sysctl -n hw.cpufrequency", shell=True).decode().strip()
             info['cpu']['architecture'] = platform.machine()
             info['cpu']['cores'] = int(subprocess.check_output("sysctl -n hw.ncpu", shell=True).decode().strip())
             info['cpu']['threads'] = int(subprocess.check_output("sysctl -n hw.logicalcpu", shell=True).decode().strip())
             info['cpu']['l1d_cache_size'] = subprocess.check_output("sysctl -n hw.l1dcachesize", shell=True).decode().strip()
             info['cpu']['l1i_cache_size'] = subprocess.check_output("sysctl -n hw.l1icachesize", shell=True).decode().strip()
             info['cpu']['l2_cache_size'] = subprocess.check_output("sysctl -n hw.l2cachesize", shell=True).decode().strip()
             info['cpu']['l3_cache_size'] = subprocess.check_output("sysctl -n hw.l3cachesize", shell=True).decode().strip()

        else:
            with open("/proc/cpuinfo") as f:
                cpuinfo = f.read()
                cpu_name = re.search(r"model name\s*:\s*(.+)", cpuinfo).group(1).strip() if re.search(r"model name\s*:\s*(.+)", cpuinfo) else "Unknown"

                speed_match = re.search(r"cpu MHz\s*:\s*(.+)", cpuinfo)
                info['cpu']['current_clock_speed'] = float(speed_match.group(1).strip()) if speed_match else "N/A"
                cache_size_match = re.search(r"cache size\s*:\s*(.+)", cpuinfo)
                info['cpu']['cache_size'] = cache_size_match.group(1).strip() if cache_size_match else "N/A"

                try:
                    scaling_max_freq = subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", shell=True, executable="/bin/bash").decode().strip()
                    info['cpu']['max_clock_speed'] = round(int(scaling_max_freq) / 1000, 2)
                except:
                    info['cpu']['max_clock_speed'] = "N/A"

                info['cpu']['architecture'] = platform.machine()
                #get core count
                try:
                    info['cpu']['cores'] = os.cpu_count()
                except Exception as e:
                    info['cpu']['cores'] = f"Error getting CPU core count: {e}"
                try:
                    with open("/proc/stat") as f:
                        stat_info = f.read()
                        ctxt_match = re.search(r"ctxt\s*(\d+)", stat_info)
                        info['cpu']['context_switches'] = int(ctxt_match.group(1)) if ctxt_match else "N/A" #get num context switches.
                except:
                    info['cpu']['context_switches'] = "N/A"

                try:
                    with open("/proc/interrupts") as f:
                        interrupt_info = f.read()
                        irq_count = 0
                        for line in interrupt_info.splitlines():
                            if not line.startswith("CPU"):
                                try:
                                    irq_count += sum([int(x) for x in line.split()[1:]])
                                except ValueError:
                                    pass #ignore errors
                        info['cpu']['total_interrupts'] = irq_count #total interrupts since boot
                except:
                    info['cpu']['total_interrupts'] = "N/A"
                info['cpu']['name'] = cpu_name


    except Exception as e:
        info['cpu']['name'] = f"Error getting CPU info: {e}"

    # 3. Memory Information
    info['memory'] = {}
    try:
        if info['os']['system'] == "Windows":
            output = subprocess.check_output("wmic computersystem get TotalPhysicalMemory", shell=True).decode()
            mem_bytes = int(output.split('\n')[1].strip())
            info['memory']['total_gb'] = round(mem_bytes / (1024 ** 3), 2)

            output = subprocess.check_output("wmic memorychip get Capacity, Speed, Manufacturer, PartNumber, SerialNumber, FormFactor, MemoryType, ConfiguredClockSpeed /Value", shell=True).decode()

            memory_modules = []
            capacities = re.findall(r"Capacity=(.+)", output)
            speeds = re.findall(r"Speed=(.+)", output)
            manufacturers = re.findall(r"Manufacturer=(.+)", output)
            part_numbers = re.findall(r"PartNumber=(.+)", output)
            serial_numbers = re.findall(r"SerialNumber=(.+)", output)
            form_factors = re.findall(r"FormFactor=(.+)", output)
            memory_types = re.findall(r"MemoryType=(.+)", output)
            configured_speeds = re.findall(r"ConfiguredClockSpeed=(.+)", output)

            for i in range(len(capacities)):
                try:
                    cap_gb = round(int(capacities[i].strip()) / (1024 ** 3), 2)
                except ValueError:
                     cap_gb = "Unknown"

                memory_modules.append({
                    'capacity_gb': cap_gb,
                    'speed_mhz': speeds[i].strip() if i < len(speeds) else "Unknown",
                    'manufacturer': manufacturers[i].strip() if i < len(manufacturers) else "Unknown",
                    'part_number': part_numbers[i].strip() if i < len(part_numbers) else "Unknown",
                    'serial_number': serial_numbers[i].strip() if i < len(serial_numbers) else "Unknown",
                    'form_factor': form_factors[i].strip() if i < len(form_factors) else "Unknown",
                    'memory_type': memory_types[i].strip() if i < len(memory_types) else "Unknown",
                    'configured_speed_mhz': configured_speeds[i].strip() if i < len(configured_speeds) else "Unknown",
                })

            info['memory']['modules'] = memory_modules

            try: #get virtual memory info (page file)
                pagefile_output = subprocess.check_output("wmic pagefile get AllocatedBaseSize, CurrentUsage, Name /Value", shell=True).decode()
                allocated_sizes = re.findall(r"AllocatedBaseSize=(.+)", pagefile_output)
                current_usages = re.findall(r"CurrentUsage=(.+)", pagefile_output)
                pagefile_names = re.findall(r"Name=(.+)", pagefile_output)
                pagefiles = []
                for i in range(len(allocated_sizes)):
                    allocated_mb = int(allocated_sizes[i].strip()) if allocated_sizes else "Unknown"
                    current_usage_mb = int(current_usages[i].strip()) if current_usages else "Unknown"
                    pagefiles.append({
                        'name': pagefile_names[i].strip(),
                        'allocated_mb': allocated_mb,
                        'current_usage_mb': current_usage_mb
                    })
                info['memory']['pagefiles'] = pagefiles

            except Exception as e:
                info['memory']['pagefiles'] = f"Error getting pagefile info: {e}"

        elif info['os']['system'] == "Darwin":
            output = subprocess.check_output("sysctl -n hw.memsize", shell=True).decode()
            mem_bytes = int(output.strip())
            info['memory']['total_gb'] = round(mem_bytes / (1024 ** 3), 2)
            #macOS doesn't give easily accessible details for each memory module.
            info['memory']['modules'] = "Details unavailable without 3rd-party tools."

            #get virtual memory details
            try:
                vm_stat = subprocess.check_output("vm_stat", shell=True).decode()
                pages_free = re.search(r"Pages free:\s*(\d+)\.", vm_stat)
                pages_active = re.search(r"Pages active:\s*(\d+)\.", vm_stat)
                pages_inactive = re.search(r"Pages inactive:\s*(\d+)\.", vm_stat)
                pages_wired = re.search(r"Pages wired down:\s*(\d+)\.", vm_stat)

                page_size = int(subprocess.check_output("pagesize", shell=True).decode().strip())

                info['memory']['vm_free_gb'] = round(int(pages_free.group(1)) * page_size / (1024**3), 2) if pages_free else "N/A"
                info['memory']['vm_active_gb'] = round(int(pages_active.group(1)) * page_size / (1024**3), 2) if pages_active else "N/A"
                info['memory']['vm_inactive_gb'] = round(int(pages_inactive.group(1)) * page_size / (1024**3), 2) if pages_inactive else "N/A"
                info['memory']['vm_wired_gb'] = round(int(pages_wired.group(1)) * page_size / (1024**3), 2) if pages_wired else "N/A"

            except Exception as e:
                info['memory']['virtual_memory'] = f"Error getting virtual memory stats: {e}"


        else:
            with open("/proc/meminfo") as f:
                meminfo = f.read()
                mem_total_match = re.search(r"MemTotal:\s*(\d+) kB", meminfo)
                mem_kb = int(mem_total_match.group(1)) if mem_total_match else 0
                info['memory']['total_gb'] = round(mem_kb / (1024 * 1024), 2)

                mem_free_match = re.search(r"MemFree:\s*(\d+) kB", meminfo)
                info['memory']['free_gb'] = round(int(mem_free_match.group(1)) / (1024*1024), 2) if mem_free_match else "N/A"
                swap_total_match = re.search(r"SwapTotal:\s*(\d+) kB", meminfo)
                info['memory']['swap_total_gb'] = round(int(swap_total_match.group(1)) / (1024*1024), 2) if swap_total_match else "N/A"
                swap_free_match = re.search(r"SwapFree:\s*(\d+) kB", meminfo)
                info['memory']['swap_free_gb'] = round(int(swap_free_match.group(1)) / (1024*1024), 2) if swap_free_match else "N/A"

            try:
                dmidecode_output = subprocess.check_output("dmidecode -t memory", shell=True, executable="/bin/bash").decode() #requires root
                memory_modules = []
                devices = dmidecode_output.split("Memory Device")
                for device in devices[1:]:  # Skip the first empty split
                    size_match = re.search(r"Size:\s*(.+)", device)
                    speed_match = re.search(r"Speed:\s*(.+)", device)
                    manufacturer_match = re.search(r"Manufacturer:\s*(.+)", device)
                    part_number_match = re.search(r"Part Number:\s*(.+)", device)
                    serial_number_match = re.search(r"Serial Number:\s*(.+)", device)
                    form_factor_match = re.search(r"Form Factor:\s*(.+)", device) #new dmi info
                    locator_match = re.search(r"Locator:\s*(.+)", device) # get location

                    size = size_match.group(1).strip() if size_match else "Unknown"

                    # Convert memory size to GB if it's in MB
                    if "MB" in size:
                        try:
                            size_mb = int(size.replace(" MB", ""))
                            size_gb = round(size_mb / 1024, 2)
                            size = f"{size_gb} GB"
                        except ValueError:
                            pass  # leave size as is

                    memory_modules.append({
                        'capacity': size, #using size, since GB and MB are accounted for here
                        'speed_mhz': speed_match.group(1).strip() if speed_match else "Unknown",
                        'manufacturer': manufacturer_match.group(1).strip() if manufacturer_match else "Unknown",
                        'part_number': part_number_match.group(1).strip() if part_number_match else "Unknown",
                        'serial_number': serial_number_match.group(1).strip() if serial_number_match else "Unknown",
                        'form_factor': form_factor_match.group(1).strip() if form_factor_match else "Unknown",
                        'locator': locator_match.group(1).strip() if locator_match else "Unknown"
                    })
                info['memory']['modules'] = memory_modules
            except Exception as e:
                info['memory']['modules'] = f"Unable to get memory details (dmidecode failed).  Root privileges required to use dmidecode. Error: {e}"
    except Exception as e:
        info['memory']['total_gb'] = f"Error getting memory info: {e}"

    # 4. Disk Information
    info['disks'] = []
    try:
        if info['os']['system'] == "Windows":
            output = subprocess.check_output("wmic diskdrive get Caption,Size, InterfaceType, MediaType, Model, SerialNumber, Partitions, Index, FirmwareRevision, BytesPerSector, SectorsPerTrack, TotalCylinders, TotalSectors, TotalTracks /Value", shell=True).decode() #Serial, partions, index

            captions = re.findall(r"Caption=(.+)", output)
            sizes = re.findall(r"Size=(.+)", output)
            interfaces = re.findall(r"InterfaceType=(.+)", output)
            media_types = re.findall(r"MediaType=(.+)", output)
            models = re.findall(r"Model=(.+)", output)
            serials = re.findall(r"SerialNumber=(.+)", output)
            partitions = re.findall(r"Partitions=(.+)", output)
            indices = re.findall(r"Index=(.+)", output)
            firmware_revisions = re.findall(r"FirmwareRevision=(.+)", output)
            bytes_per_sectors = re.findall(r"BytesPerSector=(.+)", output)
            sectors_per_tracks = re.findall(r"SectorsPerTrack=(.+)", output)
            total_cylinders = re.findall(r"TotalCylinders=(.+)", output)
            total_sectors = re.findall(r"TotalSectors=(.+)", output)
            total_tracks = re.findall(r"TotalTracks=(.+)", output)

            for i in range(len(captions)):
                try:
                     size_gb = round(int(sizes[i].strip()) / (1024 ** 3), 2)
                except ValueError:
                    size_gb = "Unknown" #Handle disks where size is invalid.
                disk_info = { #store disk details.
                    'name': captions[i].strip(),
                    'size_gb': size_gb,
                    'interface': interfaces[i].strip() if i < len(interfaces) else "Unknown",
                    'media_type': media_types[i].strip() if i < len(media_types) else "Unknown",
                    'model': models[i].strip() if i < len(models) else "Unknown",
                    'serial_number': serials[i].strip() if i < len(serials) else "Unknown",
                    'partitions': partitions[i].strip() if partitions else "Unknown",
                    'index': indices[i].strip() if indices else "Unknown",
                    'firmware_revision': firmware_revisions[i].strip() if i < len(firmware_revisions) else "Unknown",
                    'bytes_per_sector': bytes_per_sectors[i].strip() if i < len(bytes_per_sectors) else "Unknown",
                    'sectors_per_track': sectors_per_tracks[i].strip() if i < len(sectors_per_tracks) else "Unknown",
                    'total_cylinders': total_cylinders[i].strip() if i < len(total_cylinders) else "Unknown",
                    'total_sectors': total_sectors[i].strip() if i < len(total_sectors) else "Unknown",
                    'total_tracks': total_tracks[i].strip() if i < len(total_tracks) else "Unknown"
                }
                try: #get drive health, requires admin
                    smart_output = subprocess.check_output("wmic diskdrive get Status, Availability, ErrorDescription /Value", shell=True).decode()
                    statuses = re.findall(r"Status=(.+)", smart_output)
                    availabilities = re.findall(r"Availability=(.+)", smart_output)
                    error_descriptions = re.findall(r"ErrorDescription=(.+)", smart_output)

                    disk_info['status'] = statuses[i].strip() if i < len(statuses) else "Unknown"
                    disk_info['availability'] = availabilities[i].strip() if i < len(availabilities) else "Unknown"
                    disk_info['error_description'] = error_descriptions[i].strip() if i < len(error_descriptions) else "None"
                except Exception as e:
                    disk_info['health_info'] = f"Unable to get drive health. Admin required. Error: {e}"

                info['disks'].append(disk_info) #add dik info.

        else:
            output = subprocess.check_output("df -h", shell=True).decode()
            lines = output.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    filesystem = parts[0]
                    size = parts[1]
                    mounted_on = parts[5]  # Get the mount point
                    disk_info = {'name': filesystem, 'size': size, 'mount_point': mounted_on} #store in disk_info var

                    try: #get serial number, requires sudo
                        serial_output = subprocess.check_output(f"sudo udevadm info --name={filesystem} | grep ID_SERIAL=", shell=True, executable="/bin/bash").decode()
                        disk_info['serial_number'] = serial_output.split("ID_SERIAL=")[1].strip() if "ID_SERIAL=" in serial_output else "N/A"
                    except:
                        disk_info['serial_number'] = "N/A (requires sudo and correct disk name)" #if can't get disk info.

                    info['disks'].append(disk_info) #add serial to disks

    except Exception as e:
        info['disks'].append(f"Error getting disk info: {e}")


    # 5. Network Information
    info['network'] = {}
    try:
        info['network']['hostname'] = socket.gethostname()  # Use socket for a more reliable hostname
        try:
            info['network']['fqdn'] = socket.getfqdn()  # Fully qualified domain name if available
        except:
            info['network']['fqdn'] = 'N/A'

        if info['os']['system'] == "Windows":
            output = subprocess.check_output("ipconfig /all", shell=True).decode()
            ip_match = re.search(r"IPv4 Address\. . . . . . . . . . : ([0-9.]+)", output)
            info['network']['ip_address'] = ip_match.group(1) if ip_match else 'Not Found'

            mac_match = re.search(r"Physical Address\. . . . . . . . : ([0-9A-Fa-f-]+)", output)
            info['network']['mac_address'] = mac_match.group(1) if mac_match else "Not Found"

            dns_servers = re.findall(r"DNS Servers . . . . . . . . . . : (.+)", output)
            info['network']['dns_servers'] = [s.strip() for s in dns_servers] if dns_servers else "N/A"

            dhcp_enabled_match = re.search(r"DHCP Enabled\. . . . . . . . . . : (Yes|No)", output) #dhcp info
            info['network']['dhcp_enabled'] = dhcp_enabled_match.group(1) if dhcp_enabled_match else "N/A"
            gateway_match = re.search(r"Default Gateway . . . . . . . . . : (.+)", output) #added gateway
            info['network']['default_gateway'] = gateway_match.group(1).strip() if gateway_match else "N/A"

            adapters = [] #get adapters (ethernet)
            adapter_blocks = re.split(r"Ethernet adapter|Wireless LAN adapter", output)[1:] #split into adapters
            for adapter_block in adapter_blocks:
                adapter_name_match = re.search(r"Description . . . . . . . . . . : (.+)", adapter_block)
                adapter_name = adapter_name_match.group(1).strip() if adapter_name_match else "Unknown"
                connection_specific_dns_suffix_match = re.search(r"Connection-specific DNS Suffix  . : (.+)", adapter_block)
                connection_specific_dns_suffix = connection_specific_dns_suffix_match.group(1).strip() if connection_specific_dns_suffix_match else "N/A"
                dhcp_server_match = re.search(r"DHCP Server . . . . . . . . . . : (.+)", adapter_block)
                dhcp_server = dhcp_server_match.group(1).strip() if dhcp_server_match else "N/A"

                ip_address_match = re.search(r"IPv4 Address\. . . . . . . . . . : (.+)\s*\(Preferred", adapter_block) #get the preferred address
                ip_address = ip_address_match.group(1).strip() if ip_address_match else "N/A"
                subnet_mask_match = re.search(r"Subnet Mask . . . . . . . . . . : (.+)", adapter_block) #get the subnet
                subnet_mask = subnet_mask_match.group(1).strip() if subnet_mask_match else "N/A"
                adapters.append({
                    'name': adapter_name,
                    'connection_specific_dns_suffix': connection_specific_dns_suffix,
                    'dhcp_server': dhcp_server, #add dhcp info
                    'ip_address': ip_address,
                    'subnet_mask': subnet_mask
                })
            info['network']['adapters'] = adapters


        else: #Linux, MacOS
            ip_route_output = subprocess.check_output("ip route get 1", shell=True).decode()
            ip_match = re.search(r"src ([0-9.]+)", ip_route_output)
            info['network']['ip_address'] = ip_match.group(1) if ip_match else "Not Found" #get source IP

            #Get MAC address from ip addr show
            ip_addr_output = subprocess.check_output("ip addr show", shell=True).decode()
            mac_match = re.search(r"link/ether ([0-9A-Fa-f:]+)", ip_addr_output)
            info['network']['mac_address'] = mac_match.group(1) if mac_match else "Not Found"

            try: #get DNS from resolvectl (systemd)
                resolve_output = subprocess.check_output("resolvectl status", shell=True).decode()
                dns_match = re.search(r"Current DNS Server:\s*(.+)", resolve_output)
                if dns_match:
                    info['network']['dns_servers'] = [dns_match.group(1).strip()]
                else:
                    info['network']['dns_servers'] = "N/A"
            except:
                info['network']['dns_servers'] = "N/A" #If resolvectl isn't available

            try: #default gateway
                route_output = subprocess.check_output("ip route", shell=True).decode()
                default_gateway_match = re.search(r"default via (.+?) dev", route_output)
                info['network']['default_gateway'] = default_gateway_match.group(1).strip() if default_gateway_match else "N/A"
            except:
                info['network']['default_gateway'] = "N/A"
            try: # get interface names and details using ip command
                ip_output = subprocess.check_output("ip -o -4 a show", shell=True).decode()
                interfaces = []
                for line in ip_output.splitlines():
                    parts = line.split()
                    if len(parts) > 3:
                        interface_name = parts[1]
                        ip_address = parts[3].split('/')[0]  # Extract IP address without the subnet
                        interfaces.append({'name': interface_name, 'ip_address': ip_address})
                info['network']['interfaces'] = interfaces
            except Exception as e:
                info['network']['interfaces'] = f"Error getting network interfaces: {e}"
    except Exception as e:
        info['network']['hostname'] = f"Error getting hostname: {e}"
        info['network']['ip_address'] = f"Error getting IP address: {e}"
        info['network']['mac_address'] = f"Error getting MAC address: {e}"

    # 6. Graphics Card (GPU) Information
    info['gpu'] = {}
    try:
        if info['os']['system'] == "Windows":
             output = subprocess.check_output("wmic path win32_VideoController get Name, AdapterRAM, DriverVersion, DriverDate, Status, AdapterDACType, MaxRefreshRate, MinRefreshRate, InstalledDisplayDrivers, VideoModeDescription, VideoProcessor /Value", shell=True).decode() #added more fields

             gpu_names = re.findall(r"Name=(.+)", output)
             adapter_rams = re.findall(r"AdapterRAM=(.+)", output)
             driver_versions = re.findall(r"DriverVersion=(.+)", output)
             driver_dates = re.findall(r"DriverDate=(.+)", output)
             statuses = re.findall(r"Status=(.+)", output)
             dac_types = re.findall(r"AdapterDACType=(.+)", output)
             max_refresh_rates = re.findall(r"MaxRefreshRate=(.+)", output)
             min_refresh_rates = re.findall(r"MinRefreshRate=(.+)", output)
             installed_display_drivers = re.findall(r"InstalledDisplayDrivers=(.+)", output)
             video_mode_descriptions = re.findall(r"VideoModeDescription=(.+)", output)
             video_processors = re.findall(r"VideoProcessor=(.+)", output)

             gpus = []
             for i in range(len(gpu_names)):
                try:
                    ram_gb = round(int(adapter_rams[i].strip()) / (1024 ** 3), 2)
                except:
                    ram_gb = 'Unknown'
                gpus.append({
                     'name': gpu_names[i].strip(),
                     'ram_gb': ram_gb,
                     'driver_version': driver_versions[i].strip() if i < len(driver_versions) else "Unknown",
                     'driver_date': driver_dates[i].strip() if i < len(driver_dates) else "Unknown",
                     'status': statuses[i].strip() if i < len(statuses) else "Unknown",
                     'dac_type': dac_types[i].strip() if i < len(dac_types) else "Unknown",
                     'max_refresh_rate': max_refresh_rates[i].strip() if i < len(max_refresh_rates) else "Unknown",
                     'min_refresh_rate': min_refresh_rates[i].strip() if i < len(min_refresh_rates) else "Unknown",
                     'installed_display_drivers': installed_display_drivers[i].strip() if i < len(installed_display_drivers) else "Unknown",
                     'video_mode_description': video_mode_descriptions[i].strip() if i < len(video_mode_descriptions) else "Unknown",
                     'video_processor': video_processors[i].strip() if i < len(video_processors) else "Unknown"

                })
             info['gpu']['gpus'] = gpus #Changed from 'name' to 'gpus' since it will be a list

        elif info['os']['system'] == "Darwin": #MacOS
            output = subprocess.check_output("system_profiler SPDisplaysDataType", shell=True).decode()
            gpu_match = re.search(r"Chipset Model: (.*)", output)
            if gpu_match:
                info['gpu']['gpus'] = [gpu_match.group(1).strip()]
            else:
                info['gpu']['gpus'] = ["Not Found"]
        else:  # Linux (using lspci command)
            try:
                output = subprocess.check_output("lspci -v | grep -A 15 VGA", shell=True, executable="/bin/bash").decode() #more context
                gpu_names = []
                driver_versions = []
                memory_sizes = []
                gpu_entries = output.split("\n\n")  # Split into individual GPU entries

                for entry in gpu_entries:
                    name_match = re.search(r"VGA compatible controller:\s*(.+)", entry)
                    driver_match = re.search(r"Kernel driver in use:\s*(.+)", entry)
                    memory_match = re.search(r"Memory.*?size=(.+)", entry) #mem size
                    rev_match = re.search(r"Rev:\s*(.+)", entry) #revision

                    gpu_name = name_match.group(1).strip() if name_match else "Unknown"
                    driver_version = driver_match.group(1).strip() if driver_match else "Unknown"
                    memory_size = memory_match.group(1).strip() if memory_match else "Unknown"
                    revision = rev_match.group(1).strip() if rev_match else "Unknown"

                    gpus = []
                    gpus.append({
                        'name':gpu_name,
                        'driver_version':driver_version,
                        'memory_size':memory_size,
                        'revision': revision

                    })

                info['gpu']['gpus'] = gpus

            except Exception as e:
                info['gpu']['gpus'] = [f"Error getting GPU info: {e}"]


    except Exception as e:
        info['gpu']['gpus'] = [f"Error getting GPU info: {e}"]

    #7. Motherboard Information
    info['motherboard'] = {}
    try:
        if info['os']['system'] == "Windows":
            output = subprocess.check_output("wmic baseboard get Manufacturer, Product, SerialNumber, Version, HostingBoard, PoweredOn, Removable, Replaceable /Value", shell=True).decode()

            manufacturer = re.search(r"Manufacturer=(.+)", output)
            product = re.search(r"Product=(.+)", output)
            serial_number = re.search(r"SerialNumber=(.+)", output)
            version = re.search(r"Version=(.+)", output)
            hosting_board = re.search(r"HostingBoard=(.+)", output)
            powered_on = re.search(r"PoweredOn=(.+)", output)
            removable = re.search(r"Removable=(.+)", output)
            replaceable = re.search(r"Replaceable=(.+)", output)

            info['motherboard']['manufacturer'] = manufacturer.group(1).strip() if manufacturer else "Unknown"
            info['motherboard']['product'] = product.group(1).strip() if product else "Unknown"
            info['motherboard']['serial_number'] = serial_number.group(1).strip() if serial_number else "Unknown"
            info['motherboard']['version'] = version.group(1).strip() if version else "Unknown"
            info['motherboard']['hosting_board'] = hosting_board.group(1).strip() if hosting_board else "Unknown"
            info['motherboard']['powered_on'] = hosting_board.group(1).strip() if powered_on else "Unknown"
            info['motherboard']['removable'] = hosting_board.group(1).strip() if removable else "Unknown"
            info['motherboard']['replaceable'] = hosting_board.group(1).strip() if replaceable else "Unknown"


        elif info['os']['system'] == "Darwin":
            output = subprocess.check_output("system_profiler SPHardwareDataType", shell=True).decode()
            model_identifier = re.search(r"Model Identifier: (.+)", output)
            serial_number = re.search(r"Serial Number \(system\): (.+)", output)
            info['motherboard']['manufacturer'] = "Apple" #Hardcoded.
            info['motherboard']['product'] = model_identifier.group(1).strip() if model_identifier else "Unknown"
            info['motherboard']['serial_number'] = serial_number.group(1).strip() if serial_number else "Unknown"

            #get boot volume
            try:
                boot_volume = subprocess.check_output("diskutil info / | grep 'Volume Name'", shell=True).decode()
                info['motherboard']['boot_volume'] = boot_volume.split(":")[1].strip()
            except:
                info['motherboard']['boot_volume'] = "N/A"
        else: #Linux

            try:
                output = subprocess.check_output("dmidecode -t baseboard", shell=True, executable="/bin/bash").decode()
            except subprocess.CalledProcessError as e:
                output = "" #if failure, return empty string

            manufacturer = re.search(r"Manufacturer:\s*(.+)", output)
            product = re.search(r"Product Name:\s*(.+)", output)
            serial_number = re.search(r"Serial Number:\s*(.+)", output)
            version = re.search(r"Version:\s*(.+)", output) #get version

            info['motherboard']['manufacturer'] = manufacturer.group(1).strip() if manufacturer else "Unknown"
            info['motherboard']['product'] = product.group(1).strip() if product else "Unknown"
            info['motherboard']['serial_number'] = serial_number.group(1).strip() if serial_number else "Unknown"
            info['motherboard']['version'] = version.group(1).strip() if version else "Unknown"
    except Exception as e:
        info['motherboard'] = f"Error getting motherboard info: {e}"

    return info


def print_pc_info(info):
    """Prints the PC information in an organized manner."""
    print("----- System Information -----")
    print(f"  OS: {info['os']['system']} {info['os']['version']} ({info['os']['architecture']})")
    print(f"  Release: {info['os']['release']}")
    print(f"  Hostname: {info['os']['name']}")

    print("\n----- CPU Information -----")
    print(f"  Name: {info['cpu']['name']}")
    print(f"  Cores: {info['cpu'].get('cores', 'N/A')}")
    print(f"  Threads: {info['cpu'].get('threads', 'N/A')}")
    print(f"  Architecture: {info['cpu'].get('architecture', 'N/A')}")
    print(f"  Current Clock Speed: {info['cpu'].get('current_clock_speed', 'N/A')} MHz")
    print(f"  Max Clock Speed: {info['cpu'].get('max_clock_speed', 'N/A')} MHz")  # Print max clock speed
    print(f"  L2 Cache Size: {info['cpu'].get('l2_cache_size', 'N/A')}")
    print(f"  L3 Cache Size: {info['cpu'].get('l3_cache_size', 'N/A')}")
    print(f"  Manufacturer: {info['cpu'].get('manufacturer', 'N/A')}")
    print(f"  Family: {info['cpu'].get('family', 'N/A')}")
    print(f"  Device ID: {info['cpu'].get('device_id', 'N/A')}")
    if info['os']['system'] == "Linux":
      print(f" Context Switches: {info['cpu'].get('context_switches', 'N/A')}") #print linux specific info
      print(f" Total Interrupts: {info['cpu'].get('total_interrupts', 'N/A')}")

    print("\n----- Memory Information -----")
    print(f"  Total Memory: {info['memory']['total_gb']} GB")
    if isinstance(info['memory']['modules'], list):
        for i, module in enumerate(info['memory']['modules']):
            print(f"  Module {i+1}:")
            print(f"    Capacity: {module.get('capacity_gb', module.get('capacity', 'Unknown'))} GB")
            print(f"    Speed: {module.get('speed_mhz', 'Unknown')} MHz")
            print(f"    Manufacturer: {module.get('manufacturer', 'Unknown')}")
            print(f"    Part Number: {module.get('part_number', 'Unknown')}")
            print(f"    Serial Number: {module.get('serial_number', 'Unknown')}")
            print(f"    Form Factor: {module.get('form_factor', 'Unknown')}")
            print(f"   Location: {module.get('locator', 'Unknown')}")
            if 'memory_type' in module:
                 print(f"    Memory Type: {module['memory_type']}")
            if 'configured_speed_mhz' in module:
                print(f"  Configured Speed: {module['configured_speed_mhz']}")

    else:
        print(f"  Module Details: {info['memory']['modules']}")

    if 'pagefiles' in info['memory']:
        print("\n----- Page File Information -----")
        if isinstance(info['memory']['pagefiles'], str):
            print(f" {info['memory']['pagefiles']}")
        else:
            for pagefile in info['memory']['pagefiles']:
                print(f" Name: {pagefile['name']}")
                print(f"  Allocated: {pagefile['allocated_mb']} MB")
                print(f"  Current Usage: {pagefile['current_usage_mb']} MB")
    if info['os']['system'] == "Darwin":
        print("\n----- Virtual Memory (macOS) -----")
        print(f"  Free: {info['memory'].get('vm_free_gb', 'N/A')} GB")
        print(f"  Active: {info['memory'].get('vm_active_gb', 'N/A')} GB")
        print(f"  Inactive: {info['memory'].get('vm_inactive_gb', 'N/A')} GB")
        print(f"  Wired: {info['memory'].get('vm_wired_gb', 'N/A')} GB")

    if info['os']['system'] == "Linux": #Show linux memory details
        print("\n----- Memory (Linux) -----")
        print(f"  Free: {info['memory'].get('free_gb', 'N/A')} GB")
        print(f"  Swap Total: {info['memory'].get('swap_total_gb', 'N/A')} GB")
        print(f"  Swap Free: {info['memory'].get('swap_free_gb', 'N/A')} GB")

    print("\n----- Disk Information -----")
    if isinstance(info['disks'], str):
        print(f"  {info['disks']}")
    else:
        for disk in info['disks']:
            print(f"  Drive: {disk['name']}, Size: {disk.get('size_gb', disk.get('size', 'Unknown'))} GB")
            print(f"    Interface: {disk.get('interface', 'Unknown')}")
            print(f"    Media Type: {disk.get('media_type', 'Unknown')}")
            print(f"    Model: {disk.get('model', 'Unknown')}")
            print(f"    Serial Number: {disk.get('serial_number', 'Unknown')}")
            if 'status' in disk:
                print(f"    Status: {disk['status']}")
                print(f"    Availability: {disk['availability']}")
                print(f"    Error Description: {disk['error_description']}")
            if 'health_info' in disk:
                print(f" {disk['health_info']}")

            if 'partitions' in disk:
                print(f"  Partitions: {disk['partitions']}")
            if 'index' in disk:
                print(f" Index: {disk['index']}")
            if 'firmware_revision' in disk:
                print(f"  Firmware Revision: {disk['firmware_revision']}")
            if 'bytes_per_sector' in disk:
                print(f"  Bytes per Sector: {disk['bytes_per_sector']}")
            if 'sectors_per_track' in disk:
                print(f"  Sectors per Track: {disk['sectors_per_track']}")
            if 'total_cylinders' in disk:
                print(f"   Total Cylinders: {disk['total_cylinders']}")
            if 'total_sectors' in disk:
                print(f" Total Sectors: {disk['total_sectors']}")
            if 'total_tracks' in disk:
                print(f"   Total Tracks: {disk['total_tracks']}")

            if 'mount_point' in disk: #show mount
                print(f"  Mounted on: {disk['mount_point']}")

    print("\n----- Network Information -----")
    print(f"  Hostname: {info['network']['hostname']}")
    print(f"  FQDN: {info['network']['fqdn']}")
    print(f"  IP Address: {info['network']['ip_address']}")
    print(f"  MAC Address: {info['network']['mac_address']}")
    print(f"  DNS Servers: {info['network']['dns_servers']}")
    if 'dhcp_enabled' in info['network']: #show dhcp info
        print(f"  DHCP Enabled: {info['network']['dhcp_enabled']}")
    print(f"  Default Gateway: {info['network']['default_gateway']}")

    if 'adapters' in info['network']:
        print("\n----- Network Adapters -----")
        for adapter in info['network']['adapters']:
            print(f"  Name: {adapter['name']}")
            print(f"  Connection-specific DNS Suffix: {adapter['connection_specific_dns_suffix']}")
            if 'dhcp_server' in adapter:
                print(f" DHCP Server: {adapter['dhcp_server']}")
            if 'ip_address' in adapter:
                print(f"IP Address: {adapter['ip_address']}")
            if 'subnet_mask' in adapter:
                print(f"  Subnet Mask: {adapter['subnet_mask']}")

    if 'interfaces' in info['network']:
        print("\n----- Network Interfaces -----")
        if isinstance(info['network']['interfaces'], str): #Error handling
            print(f" Error: {info['network']['interfaces']}")
        else:
            for interface in info['network']['interfaces']:
                print(f"  Name: {interface['name']}, IP Address: {interface.get('ip_address', 'N/A')}")

    print("\n----- GPU Information -----")
    if isinstance(info['gpu']['gpus'], list):
        for gpu in info['gpu']['gpus']:
            print(f"  GPU: {gpu['name']}")
            if 'ram_gb' in gpu:
                print(f"    RAM: {gpu['ram_gb']} GB")
            if 'driver_version' in gpu:
                print(f"    Driver Version: {gpu['driver_version']}")
            if 'driver_date' in gpu:
                print(f" Driver Date: {gpu['driver_date']}")
            if 'status' in gpu:
                print(f"   Status: {gpu['status']}")
            if 'dac_type' in gpu:
                print(f"    DAC Type: {gpu['dac_type']}")
            if 'max_refresh_rate' in gpu:
                print(f" Max Refresh Rate: {gpu['max_refresh_rate']}")
            if 'min_refresh_rate' in gpu:
                print(f"   Min Refresh Rate: {gpu['min_refresh_rate']}")
            if 'installed_display_drivers' in gpu:
                print(f" Installed Display Drivers: {gpu['installed_display_drivers']}")
            if 'video_mode_description' in gpu:
                print(f" Video Mode Description: {gpu['video_mode_description']}")
            if 'video_processor' in gpu:
                print(f"  Video Processor: {gpu['video_processor']}")
            if 'memory_size' in gpu:
                print(f"  Memory Size: {gpu['memory_size']}")
            if 'revision' in gpu:
                print(f"  Revision: {gpu['revision']}")
    else:
        print(f"  GPU: {info['gpu']['gpus']}") #print error

    print("\n----- Motherboard Information -----")
    print(f"  Manufacturer: {info['motherboard'].get('manufacturer', 'Unknown')}")
    print(f"  Product: {info['motherboard'].get('product', 'Unknown')}")
    print(f"  Serial Number: {info['motherboard'].get('serial_number', 'Unknown')}")
    print(f"  Version: {info['motherboard'].get('version', 'Unknown')}")
    print(f"  Hosting Board: {info['motherboard'].get('hosting_board', 'Unknown')}")
    print(f"  Powered On: {info['motherboard'].get('powered_on', 'Unknown')}")
    print(f"  Removable: {info['motherboard'].get('removable', 'Unknown')}")
    print(f"  Replaceable: {info['motherboard'].get('replaceable', 'Unknown')}")

    if 'boot_volume' in info['motherboard']:
        print(f"  Boot Volume: {info['motherboard']['boot_volume']}")

if __name__ == "__main__":
    pc_info = get_pc_info()
    print_pc_info(pc_info)
