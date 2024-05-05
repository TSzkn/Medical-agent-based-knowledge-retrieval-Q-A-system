
import random
import asyncio
import datetime
import os
import re
import uuid
 #修改需要的卡，可以占用的卡
os.environ["CUDA_VISIBLE_DEVICES"] = "3"
import argparse
import json
from typing import AsyncGenerator

import logging
from datetime import datetime

class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
        return s

# 创建一个名为 "my_logger" 的日志记录器
logger = logging.getLogger("my_logger")

# 创建一个文件处理器，将日志记录到指定的文件中
file_handler = logging.FileHandler("app.log", mode="w")

# 创建一个自定义的日志格式化器
formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S.%f")

# 设置文件处理器的格式化器
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)

# 设置日志记录器的级别为 INFO
logger.setLevel(logging.INFO)

# 记录应用程序设置完成的日志
logger.info("Application setup complete.")



class Fraction:
    def __init__(self, text, title=""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.text = text
        
class KnowledgeAgent:
    def __init__(self,id_input, title="",description="",):
        self.id = id_input
        self.description = description
        self.title = title
        self.fractions = []
        self.agents = []
    def get_id(self):
        return self.id
    
    def set_fraction(self, fractionStr):
        arr = []
        arr.append(fractionStr)
        self.fractions = arr
        
    def add_fractionStr(self, fractionStr):
        fraction = Fraction(fractionStr)
        self.fractions.append(fraction)
    
    def add_fractionStr_full(self, title, fractionStr):
        fraction = Fraction(title = title, text = fractionStr)
        
        self.fractions.append(fraction)
        
    def add_fraction(self, fraction):
        self.fractions.append(fraction)

    def add_agent(self, agent):
        self.agents.append(agent)
    
    def set_description(self, description):
        self.description = description
    
    def get_description(self):
        return self.description
        
    def get_title(self):
        return self.title
    
    def set_title(self, title):
        self.title = title
        
    def get_agent_nodes(self):
        return self.agents
    
    def isFractionNode(self):
        return len(self.fractions)!=0
    
    def get_fraction_nodes(self):
        return self.fractions
    
    def get_nodes(self):
        return self.fractions, self.agents

    async def search_fractions(self, query, question):
        fractions, agents = self.get_nodes()
        availableFractions = []
        for fraction in fractions:
            result, fraction = await self.check_fraction_available(fraction, question)
            if result:
                availableFractions.append(fraction)
                # return fraction
        for fraction in availableFractions:
            query.relatedFraction.append(fraction)
        return availableFractions
    
    async def seasrchSelect_strategy(self, SearchAttempt, usedList):
        logger.info(f"search strategy!!!{self.id}")
        question = SearchAttempt.question
        description = f"##任务：路径选取\n#这个是你需要去解决的问题：{question},\n 这些是你可以搜索到的知识:\n"
        index = 0
        logger.info(f"selected!!!!{len(self.get_agent_nodes())}")
        
        if(len(self.get_agent_nodes())>1):
            for agent in self.get_agent_nodes():
                if float(agent.id) not in usedList:
                    # print("usedList!!!!!!!!!!!!!!!!!!!!!!")
                    # print(usedList)
                    # print(float(agent.id))
                    index+=1
                    description +=  f"/**\n【({index})】"+"标题:"+agent.get_title()+" || 描述: "+ agent.get_description() + "\n**/\n"
            
            description+=f"#要求：以【(?)】的格式输出，在这些问题当中最有可能包含与问题相关的知识的节点是哪一个"
                
            # logger.info(f"description!!!{description}" )
            output = await generate_result(description)
        else:
            if len(self.get_agent_nodes())==1:
                output = "【(1)】"
            else:
                output = "【(-1)】"
        logger.info(f"{output}Node search output!!!!!")
        
        
        gotResult, nodeIndex = extract_result_node_index(output)
        if not gotResult:
            return None
        
        fractions, allNodes = self.get_nodes()
        
        if 0 <= nodeIndex < len(allNodes):
            selectedNode = allNodes[nodeIndex]
            return selectedNode
        else:
            logger.warning(f"Invalid nodeIndex: {nodeIndex}")
            return None
    


class SearchAttempt:
    def __init__(self, text, query, starterNode:KnowledgeAgent):
        self.startNode = starterNode
        self.id = str(uuid.uuid4())
        self.question = text
        self.history_path = []
        self.relatedFraction = []
        self.query = query
            
    def add_history_path(self, agentID):
        self.history_path.append(agentID)
    
    async def attempt_search(self):
        result = await self.search_agent_nodes(currentNode = self.startNode)
        # self.query.add_relatedFraction()
        # fractionTexts = self.relatedFraction
    
    async def search_agent_nodes(self, currentNode, top_k=1):
        logger.info(f"searched!!!!! id:{self.id}")
        fractions, agents = currentNode.get_nodes()
        selectedNode = []
        if currentNode.isFractionNode():
            logger.info(f"fraction node found!!!!\n")
            # await self.search_fractions(query, question)
            for element in fractions:
                logger.info(f"&&&{element.text}&&&")
                self.query.add_relatedFraction(element)
                return
        else:
            hasNode1 = True
            tryCount = 0
            node1 = await currentNode.seasrchSelect_strategy(self)
            if node1!=None:
                currentNode = node1
                # await node1.search_agent_nodes(currentNode)
                await self.search_agent_nodes(currentNode)
                tryCount+=1
            else:
                
                logger.info("hit dead end$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                logger.info(currentNode.get_title())
                logger.info(currentNode.get_id())
                logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                hasNode1 = True
        
import re
# def extract_result_node_index(string):
#     nodeIndex = 0
#     match = re.search(r'\((\d+)\)', string)
#     if match:
#         nodeIndex = int(match.group(1)) - 1
#     logger.info("nodeIndex:", nodeIndex)
#     return True, nodeIndex
def extract_result_node_index(string):
    if not isinstance(string, (str, bytes)):
        # Log the type and value of the input that caused the issue
        # logger.info(f"Invalid input type: {type(string)} value:{string}")
        # Handle the error as appropriate
        return False, -1

    if string:
        nodeIndex = 0
        match = re.search(r'\((\d+)\)', string)
        
        if match:
            logger.info(f"match!!!!{match.group(1)}")
            nodeIndex = int(match.group(1)) - 1
        else:
            # logger.info(f"nodeIndex:{nodeIndex}")
            logger.info("no node dead end222222 &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        logger.info(f"nodeIndex:{nodeIndex}")
        return True, nodeIndex
    else:
        logger.info("no node dead end &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        return False, nodeIndex
        
       
import re
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
# url = "http://36.212.25.245:5000/generate"
def extract_result_bool(string):
    return True

import csv
def add_node_by_path(start_node, path, target_node, file_path):
    with open(file_path, 'r',encoding="utf-8-sig") as file:
        
        csv_reader = csv.DictReader(file)
        
        index= 0
        current_node = start_node
        # mock_id = 12084908129083490
        mockcontent = ""
        last_element_id = 12389712894798
        if(len(path)<4):
            if path:  # 检查path是否不为空
                last_element = path[-1]  # 获取列表的最后一个元素
                last_element_id = last_element 
        for node_id in path:
            index+=1
            found = False
            for agent in current_node.get_agent_nodes():
                if agent.get_id() == node_id:
                    current_node = agent
                    found = True
                    break
            if float(current_node.get_id()) == float(node_id):
                found = True
            if not found:
                # 查找CSV文件中对应的节点信息
                file.seek(0)  # 将文件指针移回文件开头
                next(csv_reader)
                for row in csv_reader:
                    if float(row['id']) == node_id:
                        if float(row['id']) == float(last_element_id):
                            title = row['title']
                            description = row['description']
                            logger.info(f"title!!!!!{title}")
                            content = row['content']
                            logger.info(f"content!!!!!{title}")
                            level = float(row['level'])
                            new_node = KnowledgeAgent(id_input=float(node_id), title=title, description=description)
                            current_node.add_agent(new_node)
                            if content !="" and content!=None:
                                mock_node = KnowledgeAgent(id_input=float(node_id)+1000000, title=title+"的详细内容", description=description)
                                mock_node.add_fractionStr_full(title, content)
                                new_node.add_agent(mock_node)
                            current_node = new_node
                            break
                        title = row['title']
                        description = row['description']
                        logger.info(f"title!!!!!{title}")
                        content = row['content']
                        logger.info(f"content!!!!!{title}")
                        level = float(row['level'])
                        new_node = KnowledgeAgent(id_input=float(node_id), title=title, description=description)
                        new_node.add_fractionStr_full(title, content)
                        current_node.add_agent(new_node)
                        current_node = new_node
                        break
        # current_node.add_agent(target_node)
def build_knowledge_tree_from_csv(file_path, start_node):
    with open(file_path, 'r', encoding="utf-8-sig") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            node_id = float(row['id'])
            title = row['title']
            description = row['description']
            content = row['content']
            parent_data = row['parent_data']
            level = float(row['level'])  # 将level转换为浮点数
            path = json.loads(parent_data) if parent_data else []
            target_node = KnowledgeAgent(id_input = node_id, title=title, description=description)
            add_node_by_path(start_node, path, target_node,file_path)
    return start_node

startNode = KnowledgeAgent(id_input = -1)
# csv_file_path = '/root/sdb1/Yixuan/search-agent/health_1 (1).csv'
# csv_file_path = "/root/sdb1/Yixuan/search-agent/health_complete.csv"
# csv_file_path = "/root/sdb1/Yixuan/search-agent/health_all(1).csv"
csv_file_path = "health_database_final.csv"
knowledge_tree = build_knowledge_tree_from_csv(csv_file_path, startNode)

import json
def traverse_tree(node):
    node_info = {
        'id': node.get_id(),
        'title': node.get_title(),
        'description': node.get_description(),
        'fractions':[],
        'agents': []
    }
    # 这个地方 fraction需要重新变成json
    arr = node.get_fraction_nodes()
    for element in arr:
        fraction_json = {
            'id' : element.id,
            'text' : element.text
        }
        node_info['fractions'].append(fraction_json)

    for agent in node.get_agent_nodes():
        node_info['agents'].append(traverse_tree(agent))
    return node_info

def write_tree_to_json(start_node, output_file):
    tree_info = traverse_tree(start_node)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(tree_info, file, indent=4, ensure_ascii=False)

        
# 使用示例
output_file = 'knowledge_tree2.json'
write_tree_to_json(startNode, output_file)

rawDatas=[]
json_file_path = "training_raw_data_final.json"
with open(json_file_path, 'r', newline='',encoding='utf-8-sig', errors='replace') as file:
    rawDatas = json.load(file)
    # print(rawData)

def find_node_by_id(root_agent, target_id):
    # print("find_node_by_id!!!!!!!!!!")
    # print(root_agent.id, target_id, root_agent.get_agent_nodes())
    target_id = float(target_id)
    # root_agent = startNode
    if float(root_agent.get_id()) == float(target_id):
        # print("equal!!!!!!!!!!")
        # print(root_agent.id, target_id, len(root_agent.get_agent_nodes()))
        return root_agent.get_agent_nodes()
    
    for agent in root_agent.get_agent_nodes():
        result = find_node_by_id(agent, target_id)
        
        
        
        if result is not None:
            return result
    
    return None


def training_formatter_route(qa_pair,root_node, current_id, target_id, previous):
    # print("start!!!!!!!!1",current_id, "  ", next_id)
    json_data = qa_pair
    # print(qa_pair)
    # print("start!!!!!!!!2",current_id, "  ", next_id)
    question = json_data["问题"]
    answer = json_data["回答"]
    agents = find_node_by_id(root_node,current_id)
    
    input = f"##任务：路径选取\n#这个是你需要去解决的问题：{question},\n {previous} \n这些是你现在可以搜索到的知识节点:\n"
    index = 0
    # logger.info(f"selected!!!!{len(self.get_agent_nodes())}")
    target_index = None
    if(len(agents)>0):
        for agent in agents:
            index+=1
            if float(agent.id) == float(target_id):
                target_index = index
            input += f"【({index})】/**\n"+"标题:"+agent.get_title()+" || 描述: "+ agent.get_description() + "\n**/\n"
        input+=f"#要求：以【(?)】的格式输出，在这些问题当中最有可能包含与问题相关的知识节点是哪一个"
    else:
        return
    output = f"【({target_index})】"
    
    if len(input) <= 2000:
        json_obj = {
                'input': input,
                'output':output,
                'instruction': ''
            }
            
            # 将JSON对象添加到结果列表
        # result.append(json_obj)

        # 将结果列表写入JSON文件
        # print("!!!!!!!!route_finding",current_id, "  ", next_id)
        with open('search_agent_sum4.json', 'a', encoding='utf-8') as file:
                json.dump(json_obj, file, ensure_ascii=False)
                file.write('\n')
            
            
            
def training_tree_selector(qa_pair,target_title, piece, target_id, selected_contents_for_tree):
    fractionList = []
    usedList = []
    for element in selected_contents_for_tree:
        title = element["title"]
        content = element["content"]
        fraction = Fraction(content, title)
        fractionList.append(fraction)
        
        
    targetFraction = Fraction(piece, target_title)
    fractionList.append(targetFraction)
    random.shuffle(fractionList)
    target_index = fractionList.index(targetFraction)
    target_index+=1
    
    # print("start!!!!!!!!1",current_id, "  ", next_id)
    json_data = qa_pair
    # print(qa_pair)
    # print("start!!!!!!!!2",current_id, "  ", next_id)
    question = json_data["问题"]
    answer = json_data["回答"]
    input = f"##任务：文本选取\n#这个是你需要去解决的问题：{question},\n 这些是你搜索出来的信息:\n"
    index = 0
        
    if(len(fractionList)>1):
        for fraction in fractionList:
            index+=1
            input +=  f"【({index})】/**\n"+"标题:"+fraction.title+" || 内容: "+ fraction.text + "\n**/\n"
        input+=f"#要求：以【(?)】的格式输出，在这些问题当中最有可能包含与问题相关的知识的节点是哪一个"
        
    output = f"【({target_index})】"
    
    
    if len(input) <= 2000:

        json_obj = {
                'input': input,
                'output':output,
                'instruction': ''
            }
            
        with open('search_agent_sum4.json', 'a', encoding='utf-8') as file:
                json.dump(json_obj, file, ensure_ascii=False)
                file.write('\n')


def training_TF(qa_pair, piece, tf_judge):
    json_data = qa_pair
    question = json_data["问题"]
    answer = json_data["回答"]
    input = f"##任务：内容筛选\n#问题：{question}\n#文字：{piece}\n#要求：回答文字是否对于回答问题有帮助？只能使用TRUE或者FALSE作为答案"
    output = tf_judge

    if len(input) <= 2000:
        json_obj = {
                'input': input,
                'output':output,
                'instruction': ''
            }
            
            # 将JSON对象添加到结果列表
        # result.append(json_obj)

        # 将结果列表写入JSON文件
        # print("!!!!!!!!route_finding",current_id, "  ", next_id)
        with open('search_agent_sum4.json', 'a', encoding='utf-8') as file:
                json.dump(json_obj, file, ensure_ascii=False)
                file.write('\n')



def training_summarization(qa_pair, piece):
    json_data = qa_pair
    question = json_data["问题"]
    answer = json_data["回答"]
    input = f"##任务：回答问题\n#问题：{question}\n#查找到的相关知识：{piece}\n#要求：根据问题和查找到的相关知识，回答问题"

    if len(input) <= 2000:
        json_obj = {
                'input': input,
                'output':answer,
                'instruction': ''
            }
            
            # 将JSON对象添加到结果列表
        # result.append(json_obj)

        # 将结果列表写入JSON文件
        # print("!!!!!!!!route_finding",current_id, "  ", next_id)
        with open('search_agent_sum4.json', 'a', encoding='utf-8') as file:
                json.dump(json_obj, file, ensure_ascii=False)
                file.write('\n')

data_dict_for_title = {}

with open(csv_file_path, 'r', encoding="utf-8-sig") as file:

    # 创建CSV读取器
    reader = csv.DictReader(file)

    # 将ID转换为字符串形式


    # 使用字典存储数据，以ID作为键
    data_dict_for_title = {str(row['id']): row for row in reader}

# 直接通过ID查询对应的行数据

def get_title(id):
    id_str = str(id)
    if id_str in data_dict_for_title:
        return data_dict_for_title[id_str]['title']
    elif id_str=="-1":
        return "根节点"
    
    else:
        return "无标题"



allContentList = []
mockFractionList = []
for element in rawDatas:
    json_data = element
    id = float(json_data["id"])
    original_content = json_data["origin"]
    title = get_title(id)
    mockfraction ={
        "title": title,
        "content": original_content
    }
    allContentList.append(original_content)
    mockFractionList.append(mockfraction)

for element in rawDatas:
    json_data = element
    id = float(json_data["id"])
    total_path = json_data["total_path"]
    qalist  = json_data["qa_pairs"]
    original_content = json_data["origin"]
    title = get_title(id)
    
    integer_list = json.loads(total_path)
    # Convert integers to floats
    routeList = [float(i) for i in integer_list]
    routeList.insert(0, -1)
    
    arrlist = []
    
    fullList = qalist
    
    for qa in fullList:
        qa_pair = qa
        training_summarization(qa_pair, original_content)
        previous = "\n#之前按顺序选取过的结点有："
        for index in range(len(routeList) - 1):  # 减1以避免最后一个元素
            # print("index", index)
            current_id = routeList[index]
            next_id = routeList[index + 1]  # 获取下一个ID
            
            training_formatter_route(qa_pair, startNode, current_id, next_id, previous)  #
            previousTitle = get_title(current_id)
            previous += f"【{previousTitle}】"
    
    if len(qalist)>6:
        qalist = random.sample(qalist, 6)

    for qa in qalist:
        # qa_pair = qa
        # training_summarization(qa_pair, original_content)
        
        training_TF(qa_pair, original_content, "TRUE")
        selected_contents = random.sample(allContentList, 3)
            # 循环使用这10个随机内容
        for original_content in selected_contents:
            training_TF(qa_pair, original_content, "FALSE")
            
        for index in range(3):
            num_samples = random.randint(2, 4)
            selected_contents_for_tree = random.sample(mockFractionList, num_samples)
            training_tree_selector(qa_pair,title,original_content, id, selected_contents_for_tree)
            

            
            
            
            
    # for qa in qalist:
    #     for index, id in enumerate(routeList):
    #         agents = find_node_by_id(startNode, id)
    #         qa_pair = qalist[index]
    #         training_formatter_route(qa, agents, id)
            
        
        
        
        
        # arrlist.append(agents)
        
    # for id, index in enumerate(arrlist):
    #     training_input = training_formatter_route()