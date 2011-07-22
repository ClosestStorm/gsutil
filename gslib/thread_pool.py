# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Basic thread pool with exception handler."""

import logging
import Queue
import threading


def _DefaultExceptionHandler(e):
  logging.exception(e)


class Worker(threading.Thread):
  """Thread executing tasks from a given task's queue."""

  def __init__(self, tasks, exception_handler):
    threading.Thread.__init__(self)
    self.tasks = tasks
    self.daemon = True
    self.exception_handler = exception_handler
    self.start()

  def run(self):
    while True:
      func, args, kargs = self.tasks.get()
      try:
        func(*args, **kargs)
      except Exception, e:
        self.exception_handler(e)
      self.tasks.task_done()


class ThreadPool(object):
  """Pool of threads consuming tasks from a queue."""

  def __init__(self, num_threads, exception_handler=_DefaultExceptionHandler):
    self.tasks = Queue.Queue(num_threads)
    for _ in range(num_threads):
      Worker(self.tasks, exception_handler)

  def AddTask(self, func, *args, **kargs):
    """Add a task to the queue."""
    self.tasks.put((func, args, kargs))

  def WaitCompletion(self):
    """Wait for completion of all the tasks in the queue."""
    self.tasks.join()
