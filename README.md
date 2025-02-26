# PC Info Gatherer

This Python script gathers and displays detailed information about your PC's hardware and software configuration. It's designed to be cross-platform (Windows, macOS, and Linux) and relies only on built-in Python modules and system commands, **without requiring external dependencies like `psutil`**.

## Features

*   **Operating System Information:**  OS name, version, release, architecture.
*   **CPU Information:**
    *   CPU Name (e.g., "Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz")
    *   Number of Cores and Threads
    *   Clock Speeds (Current and Max)
    *   Cache Sizes (L2, L3)
    *   Architecture
    *   Manufacturer
    *   Device ID
    *   Context Switches and Total Interrupts (Linux)
*   **Memory Information:**
    *   Total Physical Memory
    *   Detailed information about each memory module:
        *   Capacity
        *   Speed
        *   Manufacturer
        *   Part Number
        *   Serial Number
        *   Form Factor
        *   Locator
    *   Virtual Memory (Page File) details (Windows)
    *   Virtual Memory stats (macOS)
    *   Free Memory, Swap Usage (Linux)
*   **Disk Information:**
    *   Disk Name, Size
    *   Interface Type
    *   Media Type
    *   Model
    *   Serial Number
    *   Partition Information
    *   SMART Status (Windows - Requires Admin)
    *   Firmware Revision
    *   Bytes per Sector
    *   Sectors per Track
    *   Total Cylinders, Sectors, Tracks
    *   Mount Point (Linux/macOS)
*   **Network Information:**
    *   Hostname, FQDN
    *   IP Address, MAC Address
    *   DNS Servers
    *   DHCP Information
    *   Default Gateway
    *   Network Adapter Details: Name, Connection-Specific DNS Suffix, DHCP Server, IP Address, Subnet Mask
    *   Network Interface information.
*   **GPU Information:**
    *   GPU Name
    *   Dedicated RAM
    *   Driver Version and Date
    *   Status
    *   DAC Type
    *   Refresh Rates
    *   Video Mode Description, Video Processor
    *   Revision (Linux)
*   **Motherboard Information:**
    *   Manufacturer
    *   Product Name
    *   Serial Number
    *   Version
    *   Hosting Board
    *   Powered On, Removable, Replaceable

## Requirements

*   Python 3.6 or higher
*   No external Python packages are required (uses only built-in modules).

## Usage

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/pc-info-gatherer.git
    cd pc-info-gatherer
    ```

2.  **Run the script:**

    ```bash
    python pc_info.py
    ```

    **Note:**  On Linux and macOS, some information (especially disk serial numbers and memory details) requires root privileges.  Run the script with `sudo`:

    ```bash
    sudo python pc_info.py
    ```

    On Windows, run the command prompt or PowerShell as an administrator.

3.  **Output:**

    The script will print the gathered PC information to the console. The output can be lengthy, consider redirecting it to a file for easier examination:

    ```bash
    python pc_info.py > system_report.txt
    ```

## Important Notes

*   **Permissions:** Running the script with administrator or root privileges is highly recommended to obtain all possible information.
*   **WMI Errors (Windows):** Some WMI queries may fail due to WMI repository issues.
*   **dmidecode (Linux):** The `dmidecode` command is used on Linux to retrieve memory and motherboard details. It usually requires root privileges.
*   **Cross-Platform Limitations:**  The level of detail available varies depending on the operating system.

## Contributing

Feel free to contribute by submitting issues or pull requests to improve the script!

## License

This project is licensed under the [MIT License](LICENSE).  (Optional:  Create a LICENSE file in your repository with the MIT license text).
