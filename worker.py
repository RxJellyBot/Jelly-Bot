from external.discord_ import run_server
from JellyBotAPI.sysconfig import System
from extutils import activate_ping_spam

if __name__ == '__main__':
    run_server()
    activate_ping_spam(System.PingSpamWaitSeconds)
