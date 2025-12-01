from flask import Flask, request, jsonify
from hermes_core.scheduler import TaskScheduler
from hermes_core.executor import TestExecutor

app = Flask(__name__)


@app.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """获取测试用例列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    cases = TestExecutor.get_test_cases(page, limit)
    return jsonify({
        'status': 'success',
        'data': cases,
        'total': len(cases)
    })


@app.route('/api/test-cases', methods=['POST'])
def create_test_case():
    """创建测试用例"""
    case_data = request.json
    case_id = TestExecutor.create_test_case(case_data)
    return jsonify({
        'status': 'success',
        'case_id': case_id
    })


@app.route('/api/tasks/execute', methods=['POST'])
def execute_tests():
    """执行测试任务"""
    task_data = request.json
    task_id = TaskScheduler.submit_task(task_data)
    return jsonify({
        'status': 'success',
        'task_id': task_id
    })