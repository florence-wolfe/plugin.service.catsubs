# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == "__main__":
    import sys  # type: ignore
    from modules.router import Script

    Script(*sys.argv[1:]).router()
