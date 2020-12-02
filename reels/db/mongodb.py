# All functions interacting with the mongo database
import os
from django.conf import settings
from overrides import overrides
from pymongo import MongoClient

from reels.db.nosql_handler import NosqlHandlerInterface


class MongoDBHandler(NosqlHandlerInterface):

    mongo_db_conn = {
        'ENGINE': 'django_mongodb_engine',
        'NAME': os.environ['MONGO_INITDB_DATABASE'],
        'USER': os.environ['MONGO_INITDB_ROOT_USERNAME'],
        'PASSWORD': os.environ['MONGO_INITDB_ROOT_PASSWORD'],
        'HOST': 'localhost' if settings.DEV else os.getenv('REMOTE_IP', default='mongo'),
        'PORT': 27017,
    }

    def _mongo_client(self) -> MongoClient:
        return MongoClient(f'mongodb://'
                           f'{self.mongo_db_conn["USER"]}:'
                           f'{self.mongo_db_conn["PASSWORD"]}@'
                           f'{self.mongo_db_conn["HOST"]}:'
                           f'{self.mongo_db_conn["PORT"]}/')

    def _db(self):
        return self._mongo_client()[self.mongo_db_conn['NAME']]

    @overrides
    def insert_video_config(self, video_id: str, config: dict) -> None:
        self._db().videos.insert_one({'video_id': video_id, 'config': config})

    @overrides
    def get_video_config(self, video_id: str) -> dict:
        doc = self._db().videos.find_one({'video_id': video_id})
        if not doc:
            raise KeyError(f'This video_id {video_id} cannot be found in the videos mongo database')
        return doc['config']

    @overrides
    def delete_video_config(self, video_id: str) -> None:
        self._db().videos.find_one_and_delete({'video_id': video_id})
