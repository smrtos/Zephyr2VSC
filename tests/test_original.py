"""Test that the refactored module produces the same output as the original script."""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_DIRECTORY = os.getcwd()
ORIGINAL_SCRIPT_PATH = os.path.join(REPO_DIRECTORY, "tests", "original", "zephyr2vsc.py")
assert os.path.isfile(ORIGINAL_SCRIPT_PATH)

ZEPHYR_ARM_GCC_PATH = os.path.join(
    Path.home(), "zephyr-sdk-0.15.2", "arm-zephyr-eabi", "bin", "arm-zephyr-eabi-gcc.exe"
)
assert os.path.isfile(ZEPHYR_ARM_GCC_PATH)

ZEPHYR_PATH = os.path.join("tests", "fixtures", "zephyrproject", "zephyr")
assert os.path.isdir(ZEPHYR_PATH)

BUILD_PATH = os.path.join(ZEPHYR_PATH, "build")
assert os.path.isdir(BUILD_PATH)

BLINKY_PATH = os.path.join("samples", "basic", "blinky")


@pytest.fixture
def blinky():
    process = subprocess.run(
        f"west build -p always -b stm32g081b_eval {BLINKY_PATH}", cwd=ZEPHYR_PATH
    )
    assert process.returncode == 0
    yield


def test_blinky(blinky: None):
    command = f"python {ORIGINAL_SCRIPT_PATH} {ZEPHYR_ARM_GCC_PATH} {ZEPHYR_PATH} {BUILD_PATH}"
    subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    with open(os.path.join(BUILD_PATH, "zephyr_compile_db.json"), "r") as f:
        compile_db_original = json.load(f)
    with open(os.path.join(ZEPHYR_PATH, ".vscode", "settings.json"), "r") as f:
        settings_original = json.load(f)
    with open(os.path.join(ZEPHYR_PATH, ".vscode", "c_cpp_properties.json"), "r") as f:
        c_properties_original = json.load(f)

    command = f"python -m zephyr2vsc {ZEPHYR_ARM_GCC_PATH} {ZEPHYR_PATH} {BUILD_PATH}"
    subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    with open(os.path.join(BUILD_PATH, "zephyr_compile_db.json"), "r") as f:
        compile_db = json.load(f)
    with open(os.path.join(ZEPHYR_PATH, ".vscode", "settings.json"), "r") as f:
        settings = json.load(f)
    with open(os.path.join(ZEPHYR_PATH, ".vscode", "c_cpp_properties.json"), "r") as f:
        c_properties = json.load(f)

    assert compile_db_original == compile_db
    assert set(settings_original["files.exclude"]) == set(settings["files.exclude"])
    assert set(c_properties_original["configurations"][0]["browse"]["path"]) == set(
        c_properties["configurations"][0]["browse"]["path"]
    )
