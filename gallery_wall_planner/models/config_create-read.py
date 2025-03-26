import configparser

def create_config():
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['General'] = {'debug': True, 'log_level': 'info'}
    config['Excel-Styles'] = {'title_color' : 'D8BFD8', 'title_size' : 14, 'title_bold' : True, 'title_fill' : "solid",
                              'header_colors' : ["ADD8E6", "90EE90", "ADD8E6", "FFFF99", "FFFF99", "FFFF99", "FFFF99", "FA8072", "D8BFD8"],
                              'header_size' : 11, 'header_bold' : True, "header_fill" : 'solid',
                              'headers' : ["ID", "Name", "Photo", "Medium", "Width", "Height", "Depth", "Value", "NFS"]}

    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')
    title_color = config.get('Excel-Styles', 'title_color')
    title_size = config.getfloat('Excel-Styles', 'title_size')
    title_bold = config.getboolean('Excel-Styles', 'title_bold')
    title_fill = config.get('Excel-Styles', 'title_fill')
    header_colors = eval(config.get('Excel-Styles', 'header_colors'))
    header_size = config.getfloat('Excel-Styles', 'header_size')
    header_bold = config.getboolean('Excel-Styles', 'header_bold')
    header_fill = config.get('Excel-Styles', 'header_fill')
    headers = eval(config.get('Excel-Styles', 'headers'))

    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'title_color': title_color,
        'title_size': title_size,
        'title_bold': title_bold,
        'title_fill': title_fill,
        'header_colors': header_colors,
        'header_size': header_size,
        'header_bold': header_bold,
        'header_fill': header_fill,
        'headers': headers
    }

    return config_values