import psutil
import time
import csv
import sys

# Limits: anything ABOVE these gets a warning
LIMITS = {"cpu": 85, "memory": 90, "disk": 90}


def take_reading():
    # get each value and store it in a variable
    current_time = time.strftime("%H:%M:%S")
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    # put them all into one dictionary
    reading = {
        "time": current_time,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
    }
    return reading


def check_limits(reading, limits):
    warnings = []

    for name in limits:
        value = reading[name]        # e.g. reading["cpu"] -> 95
        limit = limits[name]         # e.g. limits["cpu"]  -> 85

        if value > limit:
            message = f"{name.upper()} high: {value}% (limit {limit}%)"
            warnings.append(message)

    return warnings


def summarize(readings):
    if len(readings) == 0:
        return {}

    summary = {}

    for name in ["cpu", "memory", "disk"]:
        values = []
        for r in readings:
            values.append(r[name])

        average = round(sum(values) / len(values), 1)
        peak = max(values)

        summary[name] = {"avg": average, "peak": peak}

    return summary


def save_to_csv(readings, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "cpu", "memory", "disk"])
        writer.writeheader()
        for r in readings:
            writer.writerow(r)


def main():
    # optional: python3 monitor.py <interval> <count>
    interval = 2
    count = 10
    if len(sys.argv) >= 3:
        interval = int(sys.argv[1])
        count = int(sys.argv[2])

    readings = []
    print(f"Taking {count} readings every {interval}s (Ctrl+C to stop)")

    try:
        for i in range(count):
            reading = take_reading()
            readings.append(reading)
            print(reading)

            warnings = check_limits(reading, LIMITS)
            for w in warnings:
                print("WARNING:", w)

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped early.")

    save_to_csv(readings, "health_log.csv")
    print("Saved to health_log.csv")
    print("Summary:", summarize(readings))


if __name__ == "__main__":
    main()