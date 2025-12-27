"""
MySQL数据库连接
使用mysql-connector-python库连接MySQL数据库
"""

import mysql.connector
from mysql.connector import Error
import json
import os


class MySQLConnection:
    """MySQL数据库连接类"""
    
    def __init__(self, host='localhost', port=3306, database='', user='root', password=''):
        """
        初始化数据库连接参数
        
        参数:
            host: 数据库主机地址
            port: 数据库端口号
            database: 数据库名称
            user: 用户名
            password: 密码
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=True  # 启用自动提交，确保每次查询都能读取最新数据
            )

            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"成功连接到MySQL服务器，版本: {db_info}")
                self.cursor = self.connection.cursor()

                # 设置事务隔离级别为 READ COMMITTED，确保能读取到已提交的最新数据
                try:
                    self.cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
                    print("已设置事务隔离级别为 READ COMMITTED")
                except Error as e:
                    print(f"设置事务隔离级别失败: {e}")

                return True

        except Error as e:
            print(f"连接MySQL数据库时出错: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """
        执行查询语句（SELECT）
        
        参数:
            query: SQL查询语句
            params: 查询参数（可选）
        
        返回:
            查询结果列表
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            return results
            
        except Error as e:
            print(f"执行查询时出错: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        参数:
            query: SQL更新语句
            params: 更新参数（可选）
        
        返回:
            受影响的行数
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor.rowcount
            
        except Error as e:
            print(f"执行更新时出错: {e}")
            self.connection.rollback()
            return 0
    
    def execute_many(self, query, params_list):
        """
        批量执行更新语句
        
        参数:
            query: SQL更新语句
            params_list: 参数列表
        
        返回:
            受影响的行数
        """
        try:
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            return self.cursor.rowcount
            
        except Error as e:
            print(f"批量执行时出错: {e}")
            self.connection.rollback()
            return 0
    
    def get_column_names(self):
        """获取当前查询结果的列名"""
        if self.cursor:
            return [desc[0] for desc in self.cursor.description]
        return []
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL连接已关闭")


def load_config_from_file(config_file='config_example.json'):
    """从配置文件加载数据库连接信息"""
    if not os.path.isabs(config_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, config_file)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"成功加载配置文件: {config_file}")
        return config
    except FileNotFoundError:
        print(f"错误: 配置文件 {config_file} 不存在")
        return None
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件格式错误: {e}")
        return None
    except Exception as e:
        print(f"错误: 加载配置文件时出错: {e}")
        return None


def main():
    """测试数据库连接"""
    # 从配置文件加载配置
    config = load_config_from_file('config_example.json')
    if not config:
        print("无法加载配置文件")
        return
    
    # 打印配置信息（隐藏密码）
    config_display = config.copy()
    if 'password' in config_display:
        config_display['password'] = '***'
    print(f"连接配置: {config_display}")
    
    # 创建连接对象
    db = MySQLConnection(**config)
    
    # 连接到数据库
    if db.connect():
        try:
            # 测试查询：获取数据库版本
            print("\n测试查询...")
            version = db.execute_query("SELECT VERSION()")
            if version:
                print(f"数据库版本: {version[0][0]}")
            
            # 显示当前数据库
            current_db = db.execute_query("SELECT DATABASE()")
            if current_db:
                print(f"当前数据库: {current_db[0][0]}")
            
            print("\n数据库连接测试成功！")
        finally:
            db.close()
    else:
        print("数据库连接失败")


if __name__ == "__main__":
    main()

