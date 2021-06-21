import json
import logging
import os
import sys
from logging import StreamHandler

from flask import request


class GoogleCloudHandler(StreamHandler):
    """GoogleCloudHandler is a custom StreamHandler implementation to send logs to Google Cloud."""

    def __init__(self):
        StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        project = os.environ.get('GOOGLE_CLOUD_PROJECT')

        # Build structured log messages as an object.
        global_log_fields = {}
        trace_header = request.headers.get('X-Cloud-Trace-Context')

        if trace_header and project:
            trace = trace_header.split('/')
            global_log_fields['logging.googleapis.com/trace'] = (
                f"projects/{project}/traces/{trace[0]}")

        # Complete a structured log entry.
        entry = dict(severity=record.levelname,
                     message=msg)
        print(json.dumps(entry))
        sys.stdout.flush()


def get_logger(shell_handler=True, gcp_handler=True, file_handler=False):
    """Returns configured logger. Configures logger if called for the first time
    In production only gcp_handler will be added to the logger"""
    logger = logging.getLogger(__name__)

    if not logger.handlers:
        # Initialize shell handler
        if shell_handler:
            shell_format = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
            shell_handler = logging.StreamHandler()
            shell_handler.setLevel(logging.DEBUG)
            shell_formatter = logging.Formatter(shell_format)
            shell_handler.setFormatter(shell_formatter)
            logger.addHandler(shell_handler)

        # Initialize GCP handler
        if gcp_handler:
            gcp_format = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
            gcp_handler = GoogleCloudHandler()
            gcp_handler.setLevel(logging.DEBUG)
            gcp_formatter = logging.Formatter(gcp_format)
            gcp_handler.setFormatter(gcp_formatter)
            logger.addHandler(gcp_handler)

        # Initialize logfile handler
        if file_handler:
            file_format = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
            file_handler = logging.FileHandler("debug.log")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        logger.setLevel(logging.DEBUG)

    return logger
