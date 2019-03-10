import yaml
import os.path
from .main import ImapIdleReceiver


def on_receive(res):
    print('in on_receive(): {}'.format(res))


def main():
    with open(os.path.join(os.path.dirname(__file__), 'config.yml')) as f:
        data = yaml.load(f)
        HOST = data['HOST']
        USERNAME = data['USERNAME']
        PASSWORD = data['PASSWORD']
        MAIL_FOLDER = data['MAIL_FOLDER']

    receiver = ImapIdleReceiver(HOST, USERNAME, PASSWORD, MAIL_FOLDER)
    receiver.start(on_receive)


if __name__ == '__main__':
    main()