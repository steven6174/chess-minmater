import logging


def get_app_logger() -> logging.Logger:
    log_filename = 'mm.log'
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s',
                                      datefmt='%d/%m/%Y %H:%M:%S')

    # set up file handler
    file_handler = logging.FileHandler(log_filename, 'w')  # 'w' deletes the file first, 'a' will append
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)

    # set up stream/console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    # get our logger
    app_logger = logging.getLogger('root')
    app_logger.setLevel(logging.INFO)

    # add both handlers
    app_logger.addHandler(file_handler)
    app_logger.addHandler(stream_handler)
    return app_logger
