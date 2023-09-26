# csci_utils.luigi.task
from functools import partial

from luigi.local_target import LocalTarget
from luigi.target import Target
from luigi.task import Task


class Requirement:
    def __init__(self, task_class, **params):
        self.task_class = task_class
        self.params = params

    def __get__(self, task: Task, cls) -> Task:
        if task is None:
            return
        return task.clone(self.task_class, **self.params)


class Requires:
    """Composition to replace :meth:`luigi.task.Task.requires`

    Example::

        class MyTask(Task):
            # Replace task.requires()
            requires = Requires()
            other = Requirement(OtherTask)

            def run(self):
                # Convenient access here...
                with self.other.output().open('r') as f:
                    ...

        >>> MyTask().requires()
        {'other': OtherTask()}

    """

    def __get__(self, task, cls):
        # Bind self/task in a closure
        return partial(self.__call__, task)

    def __call__(self, task) -> dict:
        """Returns the requirements of a task

        Assumes the task class has :class:`.Requirement` descriptors, which
        can clone the appropriate dependences from the task instance.

        :returns: requirements compatible with `task.requires()`
        :rtype: dict
        """
        # Search task.__class__ for Requirement instances

        return {k: v for k, v in task.__dict__.items() if isinstance(v, Requirement)}


class TargetOutput:
    def __init__(self, file_name="", target_class=LocalTarget, **target_kwargs):
        self.file_name = file_name
        self.target_class = target_class
        self.target_kwargs = target_kwargs

    def __get__(self, task: Task, cls):
        return partial(self.__call__, task)

    def __call__(self, task: Task) -> Target:
        return self.target_class(self.file_name, **self.target_kwargs)
