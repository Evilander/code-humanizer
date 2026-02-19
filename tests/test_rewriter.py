from humanize_code.rewriter import rewrite_text


def test_rewriter_removes_low_signal_comment() -> None:
    original = "# This function returns x\nx = 1\n"
    rewritten, changes = rewrite_text(original, suffix=".py")
    assert "This function returns x" not in rewritten
    assert "x = 1" in rewritten
    assert changes >= 1


def test_rewriter_limits_blank_line_runs() -> None:
    original = "a = 1\n\n\n\nb = 2\n"
    rewritten, _ = rewrite_text(original, suffix=".py")
    assert "\n\n\n\n" not in rewritten
    assert "a = 1" in rewritten
    assert "b = 2" in rewritten


def test_rewriter_keeps_hash_inside_python_string_literal() -> None:
    original = 'sample = """\\n# This function returns x\\nvalue\\n"""\\n'
    rewritten, _ = rewrite_text(original, suffix=".py")
    assert "# This function returns x" in rewritten
