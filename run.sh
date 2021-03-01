set -e

echo 创建至虚拟环境
python3 -m venv venv
source venv/bin/activate

echo 安装依赖
python -m pip install -r requirements.txt

echo 代码整理
isort ./*.py
black ./*.py


echo 清理全部python进程
{ 
    kill -9 $(ps -ef|grep -E "celery|main.py"|grep -v grep|awk '{print $2}') 
} || echo 'pass'

echo 启动celery异步消费者
nohup python -m celery -A task worker -l info >> logs/celery_common.info 2>&1 &
nohup python -m celery -A scheduler worker -l info >> logs/celery_worker.info 2>&1 &

echo 启动celery定时任务
nohup python -m celery -A scheduler beat -l info >> logs/celery_beat.info 2>&1 &


#echo 启动爬虫
#python3 main.py debug
# nohup python3 main.py >> logs/main.log 2>&1 &

# echo 启动数据API接口
# python3 api.py
