set -e
echo 清理全部python进程
{ 
    kill -9 $(ps -ef|grep -E "celery|main.py"|grep -v grep|awk '{print $2}') 
} || echo 'pass'

echo 启动celery异步消费者
nohup python -m celery -A task worker -l info >> logs/celery_common.info 2>&1 &
nohup python -m celery -A scheduler worker -l info >> logs/celery_worker.info 2>&1 &

echo 启动celery定时任务
nohup python -m celery -A scheduler beat -l info >> logs/celery_beat.info 2>&1 &