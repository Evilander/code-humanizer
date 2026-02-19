from humanize_code.analyzer import analyze_text


def test_detects_generic_name_and_broad_except() -> None:
    sample = """
def process_data(value):
    try:
        return value + 1
    except Exception:
        return 0
""".strip()
    issues = analyze_text(sample, suffix=".py")
    codes = {issue.code for issue in issues}
    assert "GENERIC_NAME" in codes
    assert "BROAD_EXCEPTION" in codes


def test_detects_low_signal_comment_and_todo() -> None:
    sample = """
# This function returns the value
def compute():
    # TODO: tune later
    return 1
""".strip()
    issues = analyze_text(sample, suffix=".py")
    codes = {issue.code for issue in issues}
    assert "LOW_SIGNAL_COMMENT" in codes
    assert "TODO_MARKER" in codes

