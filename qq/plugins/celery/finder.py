from typing import List

from celery import Celery

from qq.finder import ObjectFinder


class TaskFinder(ObjectFinder):
    def __init__(
        self,
        parent: str,
        ignore_list: List[str] = None,
        cache_key: str = None,
        celery_app: Celery = None,
    ):
        super().__init__(parent, ignore_list, cache_key)
        self.celery_app = celery_app

    def is_collectable(self, element: object):
        return getattr(element, "_app", None) == self.celery_app
