# config.py (Flask version)
import os
from flask import Flask

class Config:
    """
    Flask configuration class with similar structure to your original
    """
    # General Settings
    DEBUG = True
    LOG_LEVEL = 'info'
    
    # Excel-Styles Settings
    TITLE_COLOR = 'D8BFD8'
    TITLE_SIZE = 14
    TITLE_BOLD = True
    TITLE_FILL = "solid"
    HEADER_COLORS = ["ADD8E6", "90EE90", "ADD8E6", "FFFF99", "FFFF99", 
                    "FFFF99", "FFFF99", "FA8072", "D8BFD8"]
    HEADER_SIZE = 11
    HEADER_BOLD = True
    HEADER_FILL = 'solid'
    HEADERS = ["ID", "Name", "Photo", "Medium", "Width", 
              "Height", "Depth", "Value", "NFS"]

    @classmethod
    def init_app(cls, app):
        """Initialize Flask application with this configuration"""
        app.config.from_object(cls)
        cls.create_config_file()
        
    @classmethod
    def create_config_file(cls):
        """Create config.ini file if it doesn't exist (for compatibility)"""
        if not os.path.exists('config.ini'):
            import configparser
            config = configparser.ConfigParser()
            
            config['General'] = {
                'debug': str(cls.DEBUG),
                'log_level': cls.LOG_LEVEL
            }
            
            config['Excel-Styles'] = {
                'title_color': cls.TITLE_COLOR,
                'title_size': str(cls.TITLE_SIZE),
                'title_bold': str(cls.TITLE_BOLD),
                'title_fill': cls.TITLE_FILL,
                'header_colors': str(cls.HEADER_COLORS),
                'header_size': str(cls.HEADER_SIZE),
                'header_bold': str(cls.HEADER_BOLD),
                'header_fill': cls.HEADER_FILL,
                'headers': str(cls.HEADERS)
            }
            
            with open('config.ini', 'w') as configfile:
                config.write(configfile)