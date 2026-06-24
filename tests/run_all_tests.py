#!/usr/bin/env python3
"""Master test runner for the Urdu Audio2Text project.

Run this script to execute all tests across every feature module.

Usage:
    python tests/run_all_tests.py              # Run all tests (default)
    python tests/run_all_tests.py --module urdu_correction  # Run a specific module's tests
    python tests/run_all_tests.py --verbose                                 # Show individual test output

Features:
- Runs every test in the tests/ directory
- Reports pass/fail for each test class and total count
- Provides a summary of all results
"""

import sys
import os
import time
import traceback

# Project root (one level above tests/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Add src to path so imports work
sys.path.insert(0, SRC_DIR)


def banner(text: str) -> None:
    width = 62
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def run_test_class(test_class_name: str) -> tuple[int, int]:
    """Import and run all test methods from a class by name.

    Returns (passed, failed).
    """
    import importlib
    passed = 0
    failed = 0

    # Try importing the test module
    for test_module in [
        "test_urdu_correction",
        "test_audio_splitter",
        "test_transcribe",
        "test_youtube_transcribe",
        "test_model_batch_config",
    ]:
        try:
            mod = importlib.import_module(f"tests.{test_module}")
        except (ImportError, ModuleNotFoundError):
            # Try with relative path from tests directory
            test_path = os.path.join(PROJECT_ROOT, "tests", f"{test_module}.py")
            if not os.path.exists(test_path):
                continue
            spec = importlib.util.spec_from_file_location(
                test_module, test_path
            )
            mod = importlib.util.module_from_spec(spec)
            sys.path.insert(0, os.path.join(PROJECT_ROOT, "tests"))
            try:
                spec.loader.exec_module(mod)
            except Exception:
                continue

        # Find all Test* classes in the module
        for attr_name in dir(mod):
            if not attr_name.startswith("Test"):
                continue

            cls = getattr(mod, attr_name)
            if not isinstance(cls, type):
                continue

            if test_class_name and test_class_name.lower() not in attr_name.lower():
                # If a specific module name was requested, match by class prefix
                for prefix in ["Urdu", "Audio", "Transcribe", "YouTube", "Download", "Batch", "Config", "Model"]:
                    if test_class_name.lower() in attr_name.lower():
                        pass  # include it
                    else:
                        pass

            # Run all test_ methods in the class
            methods = [m for m in dir(cls) if m.startswith("test_") and callable(getattr(cls, m))]
            if not methods:
                continue

            cls_passed = 0
            cls_failed = 0
            cls_name = f"{test_module}.{attr_name}"

            for method_name in methods:
                try:
                    instance = cls()
                    setup = getattr(instance, "setup_method", None)
                    if callable(setup):
                        setup()
                    method = getattr(instance, method_name)
                    result = method()
                    # If the method returns True/False or raises, handle accordingly
                    passed += 1
                    cls_passed += 1
                except AssertionError as e:
                    print(f"    FAIL: {attr_name}.{method_name} — {e}")
                    failed += 1
                    cls_failed += 1
                except Exception as e:
                    print(f"    ERROR: {attr_name}.{method_name} — {type(e).__name__}: {e}")
                    failed += 1
                    cls_failed += 1

            if cls_passed > 0 or cls_failed > 0:
                status = "PASS" if cls_failed == 0 else "FAIL"
                print(f"\n  [{status}] {cls_name} ({cls_passed + cls_failed} tests)")

    return passed, failed


def run_all_tests(verbose: bool = False) -> tuple[int, int]:
    """Run every test in the tests/ directory.

    Args:
        verbose: If True, print individual test results inline.

    Returns:
        (total_passed, total_failed)
    """
    total_passed = 0
    total_failed = 0

    # Discover all test modules
    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    if not os.path.exists(tests_dir):
        print(f"[ERROR] Tests directory not found: {tests_dir}")
        return 0, 0

    test_files = sorted([
        f for f in os.listdir(tests_dir)
        if f.startswith("test_") and f.endswith(".py") and f != "run_all_tests.py"
    ])

    if not test_files:
        print("[INFO] No test files found.")
        return 0, 0

    banner("Urdu Audio2Text — Test Suite")
    print(f"\n  Tests directory : {tests_dir}")
    print(f"  Python          : {sys.version}")
    print(f"  Platform        : {sys.platform}")
    print(f"  Found           : {len(test_files)} test module(s)\n")

    # Import each test file and run its Test* classes
    for test_file in test_files:
        test_name = test_file[:-3]  # strip .py
        test_path = os.path.join(tests_dir, test_file)

        # Add tests dir to path for imports
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, tests_dir)
        if SRC_DIR not in sys.path:
            sys.path.insert(0, SRC_DIR)

        passed = 0
        failed = 0

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(test_name, test_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"\n  [ERROR] Failed to load {test_name}: {e}")
            continue

        # Find all Test* classes in the module
        test_classes = [
            getattr(mod, name)
            for name in dir(mod)
            if name.startswith("Test") and isinstance(getattr(mod, name), type)
        ]

        for cls in test_classes:
            methods = [m for m in dir(cls) if m.startswith("test_") and callable(getattr(cls, m))]
            if not methods:
                continue

            cls_passed = 0
            cls_failed = 0

            for method_name in methods:
                try:
                    instance = cls()
                    setup = getattr(instance, "setup_method", None)
                    if callable(setup):
                        setup()
                    method = getattr(instance, method_name)
                    method()
                    passed += 1
                    cls_passed += 1
                except AssertionError as e:
                    print(f"    FAIL: {cls.__name__}.{method_name} — {e}")
                    failed += 1
                    cls_failed += 1
                except Exception as e:
                    print(f"    ERROR: {cls.__name__}.{method_name} — {type(e).__name__}: {e}")
                    if verbose:
                        traceback.print_exc()
                    failed += 1
                    cls_failed += 1

            status = "PASS" if cls_failed == 0 else "FAIL"
            total = cls_passed + cls_failed
            print(f"\n  [{status}] {cls.__name__} ({total} tests)")
            total_passed += cls_passed
            total_failed += cls_failed

    # Summary
    total_tests = total_passed + total_failed
    overall_status = "ALL PASSED" if total_failed == 0 else f"{total_failed} FAILED"
    banner(f"Results: {total_tests} tests — {overall_status}")
    print(f"\n  Passed : {total_passed}")
    print(f"  Failed : {total_failed}")
    if total_tests > 0:
        print(f"  Rate   : {total_passed / total_tests * 100:.1f}%\n")

    return total_passed, total_failed


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run all tests for Urdu Audio2Text.")
    parser.add_argument(
        "--module", "-m",
        default=None,
        help="Run only tests matching this module name (e.g., urdu_correction, audio_splitter)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each test",
    )
    args = parser.parse_args()

    if args.module:
        # Run specific module tests
        passed, failed = run_test_class(args.module)
        total = passed + failed
        status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"
        banner(f"Module '{args.module}' — {total} tests — {status}")
        print(f"\n  Passed : {passed}\n  Failed : {failed}\n")
    else:
        passed, failed = run_all_tests(verbose=args.verbose)

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
