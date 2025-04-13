from configparser import ConfigParser, NoSectionError, NoOptionError, Error
import os

class Config:
    """
    A class to handle configuration settings for the application.
    """
    def __init__(self):
        self.__config__ = ConfigParser()

        # Check if the config file exists, if not create it
        if not os.path.exists('config.ini'):
            self.write_config()

        # Read the configuration file
        try:
            self.__config__.read('config.ini')

            self.debug_mode = self.__config__.getboolean('General', 'debug')
            self.log_level = self.__config__.get('General', 'log_level')
            self.title_color = self.__config__.get('Excel-Styles', 'title_color')
            self.title_size = self.__config__.getfloat('Excel-Styles', 'title_size')
            self.title_bold = self.__config__.getboolean('Excel-Styles', 'title_bold')
            self.title_fill = self.__config__.get('Excel-Styles', 'title_fill')
            self.header_colors = eval(self.__config__.get('Excel-Styles', 'header_colors'))
            self.header_size = self.__config__.getfloat('Excel-Styles', 'header_size')
            self.header_bold = self.__config__.getboolean('Excel-Styles', 'header_bold')
            self.header_fill = self.__config__.get('Excel-Styles', 'header_fill')
            self.headers = eval(self.__config__.get('Excel-Styles', 'headers'))
        except NoSectionError as e:
            print(f"Error: Missing section in configuration file: {e}")
        except NoOptionError as e:
            print(f"Error: Missing option in configuration file: {e}")
        except Error as e:
            print(f"Error reading configuration file: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        print("Configuration loaded successfully.")
        if self.debug_mode:
            print("Debug mode is enabled.")
            self.print_config()

    def write_config(self):
        # If config is empty create a new one
        if self.__config__ is None:
            # Add sections and key-value pairs
            self.__config__['General'] = {'debug': True, 'log_level': 'info'}
            self.__config__['Excel-Styles'] = {'title_color' : 'D8BFD8', 'title_size' : 14, 'title_bold' : True, 'title_fill' : "solid",
                                    'header_colors' : ["ADD8E6", "90EE90", "ADD8E6", "FFFF99", "FFFF99", "FFFF99", "FFFF99", "FA8072", "D8BFD8"],
                                    'header_size' : 11, 'header_bold' : True, "header_fill" : 'solid',
                                    'headers' : ["ID", "Name", "Photo", "Medium", "Width", "Height", "Depth", "Value", "NFS"]}

        # Write the configuration to a file
        with open('config.ini', 'w') as config_file:
            self.__config__.write(config_file)

    def print_config(self):
        """
        Print the current configuration settings.
        """
        for section in self.__config__.sections():
            print(f"[{section}]")
            for key, value in self.__config__.items(section):
                print(f"{key} = {value}")
            print()