#!/usr/bin/env python3
"""
ANSI color codes for terminal output.
"""

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def print_ok(message):
    """
    Print a success message with green checkmark.

    Args:
        message (str): The success message to print
    """
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """
    Print an error message with red cross.

    Args:
        message (str): The error message to print
    """
    print(f"{RED}✗ {message}{RESET}")
