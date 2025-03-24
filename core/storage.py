import csv
import pymysql
from pymongo import MongoClient


class Storage:
    def __init__(self, save_type):
        self.save_type = save_type

    def save(self, data):
        if self.save_type == "csv":
            self._save_to_csv(data)
        # elif self.save_type == "mysql":
        #     self._save_to_mysql(data)
        # elif self.save_type == "mongodb":
        #     self._save_to_mongodb(data)

    def _save_to_csv(self, data):
        with open('jobs.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writerow(data)

    # def _save_to_mysql(self, data):
    #     # 实现MySQL存储
    #     pass
    #
    # def _save_to_mongodb(self, data):
    #     # 实现MongoDB存储
    #     pass