# Saleae Logic Analyzer Lab Setup

This guide covers how to set up the **Saleae Logic 2** software and run the automated capture scripts for this lab.

---

## 1. Install the Software

The Python scripts require the official Saleae application to be installed and running on your computer.

1. **Download Logic 2:**
    * [Download for Windows / macOS / Linux](https://www.saleae.com/downloads/)
2. **Install:**
    * **Windows/Mac:** Run the installer/DMG as usual.
    * **Linux:** Download the `.AppImage`, make it executable (`chmod +x Logic*.AppImage`), and run it.
      * This has been tricky for more recent versions of Ubuntu flavors. Check the downloads documentation for guidance on your specific distribution.

---

## 2. IMPORTANT: Enable Automation

**The script will fail if you skip this step.**
By default, the Saleae software blocks external control. You must enable it manually.

1. Open the **Logic 2** application.
2. On the right-hand sidebar, click the **Settings** icon (Device Settings).
3. Locate the **"Automation"** section (or look for a `< >` icon in the sidebar).
4. Toggle **"Enable Automation Server"** to **ON**.
    * *Default Port:* `10430` (Leave this as is).
5. **Windows Users:** If a Firewall prompt appears, click **"Allow Access"**.

---

## 3. Wiring the Device

1. Connect the Saleae Logic Analyzer to your USB port.
2. Connect your probes:
    * **Channel 0 (Digital):** Connect to your trigger signal (e.g., GPIO).
    * **Channel 1 (Analog):** Connect to your test point (e.g., Shunt Resistor).
    * **Ground:** Connect a ground wire (black) from the Saleae to the GND of your device under test.

---

## 4. Environment Setup

We have provided a script to automatically install the required Python libraries (`saleae`, `pandas`, `numpy`).

**Run in your terminal (Git Bash on Windows):**

```bash
# 1. Navigate to the dir containing the saleae boilerplate
cd src/logic_analyzer

# 2. Run the Setup Script
source setup.sh
