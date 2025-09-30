
import json
import re


class Config:
    def __init__(self, server_url, keyword, users, city, date, price, price_index, if_commit_order, time=None):
        self.server_url = server_url
        self.keyword = keyword
        self.users = users
        self.city = city
        self.date = date
        self.time = time
        self.price = price
        self.price_index = price_index
        self.if_commit_order = if_commit_order

    @staticmethod
    def load_config():
        try:
            # 使用相对路径，确保在任何目录下都能找到配置文件
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
                print(json.dumps(config, ensure_ascii=False, indent=2))
            return Config(config['server_url'],
                        config['keyword'],
                        config['users'],
                        config['city'],
                        config['date'],
                        config['price'],
                        config['price_index'],
                        config['if_commit_order'],
                        config['time']
                        )
                        
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise
