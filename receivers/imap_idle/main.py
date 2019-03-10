from imapclient import IMAPClient
from datetime import datetime
from .last_fetched_uid_mock import get_last_fetched_uid, set_last_fetched_uid
from ..utils import MessageData


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
                        server.idle_done()
                        messages = server.search(
                            ['UID',
                             str(get_last_fetched_uid() + 1) + ':*'])
                        if len(messages) == 0:
                            server.idle()
                            continue
                        set_last_fetched_uid(messages[-1])
                        res_dict = server.fetch(
                            messages,
                            ['BODY.PEEK[TEXT]', 'ENVELOPE', 'INTERNALDATE'])
                        for res in res_dict.values():
                            on_receive(
                                MessageData({
                                    'internal_date':
                                    res[b'INTERNALDATE'],
                                    'subject':
                                    res[b'ENVELOPE'].subject.decode(),
                                    'body':
                                    res[b'BODY[TEXT]'].decode(),
                                    'from': [
                                        self.convert_address(x)
                                        for x in res[b'ENVELOPE'].from_
                                    ],
                                    'to': [
                                        self.convert_address(x)
                                        for x in res[b'ENVELOPE'].to
                                    ]
                                }))
                        server.idle()  # TODO: Reset refresh counter here
            except KeyboardInterrupt:
                break
            server.idle_done()
        print("\nTerminating...")
        server.logout()

    def stop(self):
        self.should_loop_continue = False

    def convert_address(self, addr_obj):
        """
        Converts `Address` object returned by imapclient into decoded email address string.
        """
        return addr_obj.mailbox.decode() + '@' + addr_obj.host.decode()
