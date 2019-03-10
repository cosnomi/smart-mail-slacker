from main import ImapIdleReceiver

import yaml


def on_receive(res):
    print(res)


def main():
    with open('config.yml') as f:
        data = yaml.load(f)
        HOST = data['HOST']
        USERNAME = data['USERNAME']
        PASSWORD = data['PASSWORD']
        MAIL_FOLDER = data['MAIL_FOLDER']

    receiver = ImapIdleReceiver(HOST, USERNAME, PASSWORD, MAIL_FOLDER)
    receiver.start(on_receive)


if __name__ == '__main__':
    main()