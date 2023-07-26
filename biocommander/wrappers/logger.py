import logging


def set_logger(name, verbosity):
    logger = logging.getLogger(name)
    logger.setLevel(verbosity)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(verbosity)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger