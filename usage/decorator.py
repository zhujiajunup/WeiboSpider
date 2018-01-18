from time import sleep


def process_exception(func):
    def process(*args, **keyargs):
        try:
            return func(*args, **keyargs)
        except:
            print('catch exception')
            sleep(2)
    return process


@process_exception
def loop():
    while True:
        raise Exception("123")


loop()
