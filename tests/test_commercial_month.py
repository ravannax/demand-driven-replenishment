from datetime import date

import pandas as pd

from src.commercial_month import commercial_month_label, commercial_month_start


def test_before_cutoff_stays_current_month():
    assert commercial_month_start(date(2025, 5, 10)) == pd.Timestamp("2025-05-01")


def test_on_cutoff_enters_next_month():
    assert commercial_month_start(date(2025, 5, 21)) == pd.Timestamp("2025-06-01")


def test_label():
    assert commercial_month_label(date(2025, 4, 21)) == "2025-05"
