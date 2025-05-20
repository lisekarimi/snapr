"""Initializes a thread-safe global log queue.

Used to manage log messages across threads.
"""

import queue

log_queue = queue.Queue()
