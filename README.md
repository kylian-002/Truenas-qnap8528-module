# QNAP8528 Driver Builder for TrueNAS SCALE

A simple Docker Compose setup for building the **QNAP8528 Embedded Controller (EC) driver** on TrueNAS SCALE.

This project was created to simplify rebuilding the driver for my **QNAP TS-H886**, but it can be used on other QNAP NAS models that use the IT8528 EC chip.

---

## Usage

1. Build the driver inside Docker:
   sudo docker compose up --build

2. Load the compiled kernel module
   sudo insmod ./output/qnap8528.ko


## Optional: Auto-load the driver at boot

If you want TrueNAS to automatically load the driver after startup:

1. Open the TrueNAS web UI.  
2. Go to **System Settings → Advanced → Init/Shutdown Scripts**.  
3. Add a new script with:
   - **Type:** Command  
   - **When:** Post Init  
   - **Command:**
     ```bash
     sudo insmod /mnt/path/to/your/repo/output/qnap8528.ko
     ```
4. Save and apply the configuration.

> **Note:**  
> Because the **TrueNAS SCALE root filesystem is mounted read-only**, you cannot permanently install the module under  
> `/lib/modules/` or modify system boot configuration files.  