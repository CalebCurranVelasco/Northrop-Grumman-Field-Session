"""
Scenario Configuration for Multi-Trial Testing

Edit these variables before each test run:
- SCENARIO_BASE: Which Unity scenario (BL-TC, TC-BL, etc.)
- TRIAL_NUMBER: Which trial (1, 2, or 3)

The scripts will automatically generate names like: "BL-TC-sort-trial1"
"""

# ============================================================================
# EDIT THESE FOR EACH TEST RUN
# ============================================================================

SCENARIO_BASE = "TR-BL"  # Options: BL-TC, BL-TL, BL-TR, TC-BL, TL-BL, TR-BL
TRIAL_NUMBER = 3  # Options: 1, 2, 3

# ============================================================================
# DON'T EDIT BELOW THIS LINE
# ============================================================================

def get_scenario_name(tracker_type):
    """
    Generate full scenario name

    Args:
        tracker_type: "sort" or "centroid"

    Returns:
        str: Full scenario name like "TC-BL-sort-trial1"
    """
    return f"{SCENARIO_BASE}-{tracker_type}-trial{TRIAL_NUMBER}"


def print_current_config():
    """Print current configuration"""
    print("\n" + "="*70)
    print("📋 CURRENT TEST CONFIGURATION")
    print("="*70)
    print(f"  Scenario: {SCENARIO_BASE}")
    print(f"  Trial:    {TRIAL_NUMBER}")
    print(f"  SORT name:     {get_scenario_name('sort')}")
    print(f"  Centroid name: {get_scenario_name('centroid')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    print_current_config()
