import asyncore
from resources import utils

if __name__ == '__main__':
    utils.EmailRemoteProcessor(('0.0.0.0',8025),None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass