import xml.etree.ElementTree as ET
import json


class JMeterIntegration:
    @staticmethod
    def generate_jmx_file(test_plan, output_path):
        """生成JMX压测文件"""
        root = ET.Element("jmeterTestPlan")

        # 创建测试计划
        test_plan_element = ET.SubElement(root, "hashTree", {"enabled": "true"})

        # 创建线程组
        thread_group = ET.SubElement(test_plan_element, "elementProp", {
            "name": "ThreadGroup.main_controller",
            "elementType": "ThreadGroup"
        })

        # 设置线程数、循环次数等参数
        JMeterIntegration._add_thread_group_config(thread_group, test_plan)

        # 添加HTTP请求
        for request in test_plan['requests']:
            http_sampler = ET.SubElement(test_plan_element, "HTTPSamplerProxy", {
                "guiclass": "HttpTestSampleGui",
                "testclass": "HTTPSamplerProxy",
                "testname": request['name'],
                "enabled": "true"
            })
            JMeterIntegration._add_request_config(http_sampler, request)

        # 保存为JMX文件
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def execute_jmx(jmx_path):
        """执行JMX文件"""
        import subprocess
        cmd = f"jmeter -n -t {jmx_path} -l results.jtl -j jmeter.log"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0

    @staticmethod
    def parse_results(jtl_path):
        """解析JTL结果文件"""
        results = []
        with open(jtl_path, 'r') as f:
            # 解析JTL文件内容
            pass
        return results