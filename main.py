from config_parser import ConfigParser, ConfigSyntaxError

if __name__ == "__main__":
    try:
        config = ConfigParser().parse()
    except FileNotFoundError as e:
        print(f"[ERROR]: File not found — {e.filename}")
        exit(1)
    except PermissionError as e:
        print(f"[ERROR]: Permission denied reading '{e.filename}'")
        exit(1)
    except ConfigSyntaxError as e:
        print(f"[ERROR]: {e}")
        exit(1)

    print(config)
