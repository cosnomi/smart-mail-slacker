from imapclient import IMAPClient
from last_fetched_uid_mock import get_last_fetched_uid, set_last_fetched_uid


class ImapIdleReceiver:
    def __init__(self, host, username, password, mail_folder='INBOX'):
        self.should_loop_continue = True
        self.host = host
        self.username = username
        self.password = password
        self.mail_folder = mail_folder

    def start(self, on_receive):
        server = IMAPClient(self.host, use_uid=True)
        server.login(self.username, self.password)
        server.select_folder(self.mail_folder)

        timeout = 30
        connection_refresh_sec = 60 * 10
        while self.should_loop_continue:
            # Start IDLE mode
            server.idle()
            try:
                for _ in range(connection_refresh_sec // timeout):
                    responses = server.idle_check(timeout=timeout)
                    if responses:
                        print("Server sent:",
                              responses if responses else "nothing")
                        server.idle_done()
                        print('last uid: {}'.format(get_last_fetched_uid()))
                        messages = server.search(
                            ['UID',
                             str(get_last_fetched_uid() + 1) + ':*'])
                        print('mes: {}'.format(messages))
                        if len(messages) == 0:
                            continue
                        set_last_fetched_uid(messages[-1])
                        res = server.fetch(messages, ['BODY.PEEK[TEXT]'])
                        print(res)
                        on_receive(res)  # TODO
                        server.idle()
            except KeyboardInterrupt:
                break
            server.idle_done()
        print("\nTerminating...")
        server.logout()

    def stop(self):
        self.should_loop_continue = False
