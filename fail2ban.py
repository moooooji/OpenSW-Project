import re

failed_ssh_login = r"Failed password for root from "

def check_log():
    with open("/var/log/auth.log") as auth_log:
        for line in auth_log:
            print(line)

def main():
    check_log()


if __name__ == "__main__":
    main()