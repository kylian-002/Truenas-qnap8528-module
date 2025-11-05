#!/usr/bin/env python3
import os
import time
import datetime

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

CPU_HWMON = "/sys/class/hwmon/hwmon2"   # Intel coretemp (CPU sensors)
QNAP_HWMON = "/sys/class/hwmon/hwmon6"  # QNAP EC (fans + system sensors)

PWM_CHANNELS = ["pwm1", "pwm7"]          # Fan group 1 (1–2), group 2 (7–8)
SYS_TEMP_SENSORS = ["temp1_input", "temp6_input", "temp7_input", "temp8_input"]
FAN_INPUTS = ["fan1_input", "fan2_input", "fan7_input", "fan8_input"]


FAN_MIN_TEMP = float(os.environ.get("TEMP_LOW", 35.0))
FAN_MAX_TEMP = float(os.environ.get("TEMP_HIGH", 60.0))
FAN_MIN_PWM  = int(os.environ.get("PWM_MIN", 40))
FAN_MAX_PWM  = int(os.environ.get("PWM_MAX", 255))
UPDATE_INTERVAL = int(os.environ.get("SLEEP_INTERVAL", 5))




# ----------------------------------------------------------------------
# SENSOR FUNCTIONS
# ----------------------------------------------------------------------

def read_temps(hwmon_path, sensors):
    temps = []
    for f in sensors:
        fpath = os.path.join(hwmon_path, f)
        if os.path.exists(fpath):
            try:
                val = int(open(fpath).read().strip()) / 1000.0
                if 0 < val < 128:  # valid temp
                    temps.append(val)
            except Exception:
                pass
    return temps

def read_cpu_temp():
    sensors = [f for f in os.listdir(CPU_HWMON) if f.startswith("temp") and f.endswith("_input")]
    temps = read_temps(CPU_HWMON, sensors)
    return max(temps) if temps else 0.0

def read_sys_temp():
    temps = read_temps(QNAP_HWMON, SYS_TEMP_SENSORS)
    return sum(temps) / len(temps) if temps else 0.0

def read_fan_rpms():
    rpms = {}
    for f in FAN_INPUTS:
        fpath = os.path.join(QNAP_HWMON, f)
        if os.path.exists(fpath):
            try:
                rpms[f] = int(open(fpath).read().strip())
            except Exception:
                rpms[f] = 0
    return rpms

# ----------------------------------------------------------------------
# CONTROL FUNCTIONS
# ----------------------------------------------------------------------

def calc_pwm(temp):
    """Map temperature to PWM using linear scaling with limits."""
    if temp <= FAN_MIN_TEMP:
        return FAN_MIN_PWM
    elif temp >= FAN_MAX_TEMP:
        return FAN_MAX_PWM
    else:
        scale = (temp - FAN_MIN_TEMP) / (FAN_MAX_TEMP - FAN_MIN_TEMP)
        return int(FAN_MIN_PWM + scale * (FAN_MAX_PWM - FAN_MIN_PWM))

def set_pwm(value):
    """Write PWM value to all fan groups."""
    for pwm in PWM_CHANNELS:
        fpath = os.path.join(QNAP_HWMON, pwm)
        try:
            with open(fpath, "w") as f:
                f.write(str(value))
        except Exception as e:
            print(f"Failed to write {pwm}: {e}")

# ----------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------

def main():
    if not (os.path.exists(CPU_HWMON) and os.path.exists(QNAP_HWMON)):
        print("Error: hwmon paths not found. Ensure container is privileged and /sys mounted.")
        return

    pwm_val = 0
    print("Starting QNAP Fan Controller (manual PWM mode)...")
    print(f"CPU sensors: {CPU_HWMON}")
    print(f"QNAP sensors: {QNAP_HWMON}")
    print(f"Fan channels: {PWM_CHANNELS}")
    print("-" * 60)

    while True:
        cpu_temp = read_cpu_temp()
        sys_temp = read_sys_temp()
        blended_temp = 0.7 * cpu_temp + 0.3 * sys_temp

        new_pwm = calc_pwm(blended_temp)
        if new_pwm != pwm_val:
            set_pwm(new_pwm)
            pwm_val = new_pwm

        rpms = read_fan_rpms()
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] CPU={cpu_temp:.1f}°C SYS={sys_temp:.1f}°C → PWM={pwm_val}  {rpms}")

        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()

