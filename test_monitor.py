import csv

from monitor import check_limits, summarize, save_to_csv

LIMITS = {"cpu": 85, "memory": 90, "disk": 90}


# helper: builds a fake reading so tests don't depend on the real machine
def reading(cpu, memory, disk, time="12:00:00"):
    return {"time": time, "cpu": cpu, "memory": memory, "disk": disk}


# ----- check_limits -----

def test_no_warnings_when_everything_is_normal():
    assert check_limits(reading(20, 40, 50), LIMITS) == []

def test_warns_when_cpu_is_high():
    assert check_limits(reading(95, 40, 50), LIMITS) == ["CPU high: 95% (limit 85%)"]

def test_warns_for_every_value_that_is_high():
    assert len(check_limits(reading(99, 99, 99), LIMITS)) == 3

def test_value_exactly_at_limit_does_not_warn():
    # boundary case: rule is "above the limit", so 85 is fine
    assert check_limits(reading(85, 40, 50), LIMITS) == []


# ----- summarize -----

def test_summary_average_and_peak():
    result = summarize([reading(10, 50, 60), reading(30, 70, 60)])
    assert result["cpu"] == {"avg": 20.0, "peak": 30}
    assert result["memory"] == {"avg": 60.0, "peak": 70}

def test_summary_of_no_readings_is_empty():
    assert summarize([]) == {}


# ----- save_to_csv -----

def test_csv_has_header_and_one_row_per_reading(tmp_path):
    path = tmp_path / "log.csv"
    save_to_csv([reading(10, 20, 30), reading(40, 50, 60)], path)
    with open(path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[1]["cpu"] == "40"