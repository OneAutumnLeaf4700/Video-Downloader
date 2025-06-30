# tests/test_config.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import config


class TestConfig:
    """Test class for configuration settings"""

    def test_default_download_dir_exists(self):
        """Test that default download directory constant is defined"""
        assert hasattr(config, "DEFAULT_DOWNLOAD_DIR")
        assert isinstance(config.DEFAULT_DOWNLOAD_DIR, str)
        assert config.DEFAULT_DOWNLOAD_DIR == "downloaded_content"

    def test_default_download_dir_not_empty(self):
        """Test that default download directory is not empty"""
        assert config.DEFAULT_DOWNLOAD_DIR.strip() != ""

    def test_config_values_are_strings(self):
        """Test that all config values are strings for consistency"""
        for attr_name in dir(config):
            if not attr_name.startswith("_"):  # Skip private attributes
                attr_value = getattr(config, attr_name)
                if not callable(attr_value):  # Skip functions/methods
                    assert isinstance(
                        attr_value, str
                    ), f"{attr_name} should be a string"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
