from celery import Celery
import redis
import json

# Celery配置
celery_app = Celery(
    'hermes_worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)


@celery_app.task
def execute_test_case(case_id, env_config):
    """执行单个测试用例"""
    try:
        # 获取测试用例详情
        case = get_test_case_by_id(case_id)

        # 执行接口请求
        response = execute_api_request(case, env_config)

        # 验证结果
        result = validate_response(response, case['expected'])

        # 记录执行结果
        save_execution_result(case_id, result)

        return {
            'case_id': case_id,
            'status': 'success' if result['passed'] else 'failed',
            'response_time': result['response_time'],
            'details': result
        }
    except Exception as e:
        return {
            'case_id': case_id,
            'status': 'error',
            'error': str(e)
        }


# 任务分发器
class TaskDistributor:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, db=1)

    def distribute_tasks(self, task_list):
        """分发任务到多个Worker"""
        for task in task_list:
            execute_test_case.delay(
                task['case_id'],
                task['env_config']
            )