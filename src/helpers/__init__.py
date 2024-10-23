def dark_mode(data, cookies):
    if 'dark-mode' in cookies:
        data["dark-mode"] = True

    return data
