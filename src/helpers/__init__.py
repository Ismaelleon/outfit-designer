def dark_mode(data, cookies):
    if "dark-mode" in cookies and cookies["dark-mode"] == "true":
        data["dark-mode"] = True

    return data
