from JellyBot.systemconfig import System

from extutils import activate_ping_spam


if __name__ == '__main__':
    activate_ping_spam(System.PingSpamWaitSeconds)
