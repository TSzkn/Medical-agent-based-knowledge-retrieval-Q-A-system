import asyncio
import datetime
import os
import re
 #修改需要的卡，可以占用的卡
os.environ["CUDA_VISIBLE_DEVICES"] = "3"
import argparse
import json
from typing import AsyncGenerator
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 记录应用程序设置完成的日志
logger.info("Application setup complete.")
import uuid

async def generate_result(prompt):        
        logger.info(f"prompt!!!!^^^^{prompt}^^^^")
        url = "http://36.212.25.245:5095/data"
        payload = {
                    "input": f"{prompt}",
                    "history": []
                }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # logger.info(f"response!!!!!{response}")
        if response.status_code == 200:
            response_data = response.json()
            # logger.info(f"response_data!!!!{response_data}")
            print(f"response_data!!!!{response_data}")
            chatbot_response = response_data["response"]
            
            print(f"response!!!^^^^{chatbot_response}^^^^")
            return chatbot_response
        else:
            # logger.info(f"请求失败,状态码: {response.status_code}")
            print(f"请求失败,状态码: {response.status_code}")
            return None

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
    
    async def seasrchSelect_strategy(self, SearchAttempt, usedList, previousInfo):
        logger.info(f"search strategy!!!{self.id}")
        question = SearchAttempt.question
        description = f"##任务：路径选取\n#这个是你需要去解决的问题：{question},\n{previousInfo} \n这些是你现在可以搜索到的知识节点:\n"
        index = 0
        logger.info(f"selected!!!!{len(self.get_agent_nodes())}")
        
        if(len(self.get_agent_nodes())>1):
            for agent in self.get_agent_nodes():
                if float(agent.id) not in usedList:
                    print(f"id mentioned{float(agent.id)}")
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
    
class Query:
    def __init__(self, text, starterNode:KnowledgeAgent):
        self.startNode = starterNode
        self.id = str(uuid.uuid4())
        self.question = text
        self.relatedFraction = []
        self.finalFraction = []
        self.routeList = []
    
    def add_relatedFraction(self, fraction):
        self.relatedFraction.append(fraction)

    async def check_fraction_available(self, fraction):
        logger.info(f"check_fraction_available!!!")
        question = self.question
        piece = fraction.text
        # prompt = f"任务：作为导诊助手小千帮助病人\n子任务：根据用户输入输出一个json格式的思考过程\n任务要求：先观察用户的意图，再思考如何进行下一步行动，最后给出一个指令\n/////\n对话记录：\n{first_input}"
        # sampling_params = SamplingParams(n=1, best_of=1, top_p=0.8, temperature=0.8, max_tokens=4096)
        input = f"##任务：内容筛选\n#问题：{question}\n#文字：{piece}\n要求：回答文字是否对于回答问题有帮助？只能使用TRUE或者FALSE作为答案"
        result = await generate_result(input)
        
        logger.info(f"{result}result_check!!!")
        findResult = True
        
        import re
        if re.search(r'(?i)true', result) :
            logger.info("判断环节，成功添加！！！！！！") 
            self.finalFraction.append(fraction)
            findResult = True
        if result == " FALSE" or result[0] == "FALSE":
            logger.info("判断环节，拒绝添加！！！！！！")
            findResult = False
        return findResult, piece
# # 运行主函数
# asyncio.run(main())

    async def chooseStrategy(self, question, fractionList, usedList):
        logger.info(f"chooseStrategy!!!{self.id}")
        question = question
        description = f"##任务：文本选取\n#这个是你需要去解决的问题：{question},\n 这些是你搜索出来的信息:\n"
        index = 0
        logger.info(f"selected!!!!{len(fractionList)}")
        
        if(len(fractionList)>1):
            for fraction in fractionList:
                if fraction.id not in usedList:
                    print(f"id mentioned{fraction.id}")
                    index+=1
                    description +=  f"/**\n【({index})】"+"标题:"+fraction.title+" || 内容: "+ fraction.text + "\n**/\n"
            description+=f"#要求：以【(?)】的格式输出，在这些问题当中最有可能包含与问题相关的知识的节点是哪一个"

            # logger.info(f"description!!!{description}" )
            output = await generate_result(description)
        else:
            if len(fractionList)==1:
                output = "【(1)】"
            else:
                output = "【(-1)】"
        logger.info(f"|||{output}|||Node search output!!!!!")
        gotResult, nodeIndex = extract_result_node_index(output)
        
        # return fractionList[nodeIndex]
        
        
        if not gotResult:
            return None
        # fractionListallNodes = fractionList
        if 0 <= nodeIndex < len(fractionList):
            selectedNode = fractionList[nodeIndex]
            self.finalFraction.append(selectedNode)
            return selectedNode
        else:
            logger.warning(f"Invalid nodeIndex: {nodeIndex}")
            return None
        
        
    async def query_question(self,questionInput, n = 1, top_k = 2,outputSelectionMode="tree_judge"):
        
        attempts = []
        tasks = []
        routeSummary = []
        for i in range(n):
            attempt = SearchAttempt(questionInput, self, self.startNode)
            attempts.append(attempt)
            tasks.append(attempt.attempt_search(top_k))
        
        for attem in attempts:
            routeSummary.append(attem.routeRecord)
        await asyncio.gather(*tasks)
        
    
        fractions = self.relatedFraction
        
        outputtitleList = []
        for fraction in fractions:
            outputtitleList.append(fraction.title)
            
        
        fractions = list(set(fractions))

        # mode = "true_false_judge"
        mode = outputSelectionMode
        
        if mode == "true_false_judge":
            logger.info("true_false_judge")
            check_fraction_tasks = [self.check_fraction_available(element) for element in fractions]
        elif mode == "tree_judge":
            logger.info("tree_judge")
            usedList = []
            tree_search_tasks = [self.chooseStrategy(self.question, fractions, usedList) for _ in range(10)]
            # resultFraction = await self.chooseStrategy(self.question, self.relatedFraction, usedList)
            
        else:
            print("mode fail")
            
            
        if mode == "true_false_judge":
            await asyncio.gather(*check_fraction_tasks)
        elif mode == "tree_judge":
            await asyncio.gather(*tree_search_tasks)
            
        # fractionList = []
        # for element in self.finalFraction:
        #     fractionList.append(element.title)
        # print("fractionList",fractionList)
        title_count = {}
        for element in self.finalFraction:
            title = element.title
            if title in title_count:
                title_count[title] += 1
            else:
                title_count[title] = 1
        # 打印统计结果
        print("Element Title Count:")
        for title, count in title_count.items():
            print(f"{title}: {count}")

        fractionList = [element.title for element in self.finalFraction]
        print("fractionList", fractionList)
        
        # outputtitleList = []
        prompt = f"##任务：回答问题\n#问题：{questionInput}\n#查询到的相关数据:"
        # 使用 set 去重
        unique_fractions = set(self.finalFraction)
        
        returnedInfoList = []
        
        
        for fraction in unique_fractions:
            # outputtitleList.append(fraction.title)
            prompt += "\n/**"+"\n#标题："+fraction.title+"\n#内容："+fraction.text+"\n**/"
            data = {
                "title":fraction.title,
                "content":fraction.text
            }
            returnedInfoList.append(data)
            
        result = await generate_result(prompt)
        logger.info(f"returnedInfoList{returnedInfoList}")
        return result, prompt, routeSummary, outputtitleList, title_count, returnedInfoList

class SearchAttempt:
    def __init__(self, text, query, starterNode:KnowledgeAgent, top_k = 1):
        self.startNode = starterNode
        self.id = str(uuid.uuid4())
        self.question = text
        self.history_path = []
        self.relatedFraction = []
        self.finaloutput = []
        self.routeRecord = []
        self.selectionRecord = []
        # self.routeRecord.append(starterNode.id)
        self.query = query
        
    def add_history_path(self, agentID):
        self.history_path.append(agentID)
    
    async def attempt_search(self, top_k):
        level = -1
        previousInfo = "\n#之前按顺序选取过的结点有：【根节点】"
        result = await self.search_agent_nodes(currentNode = self.startNode, top_k = top_k, currentlevel = level, previousInfo = previousInfo)
        
    async def search_agent_nodes(self, currentNode, top_k=1, currentlevel = -1, previousInfo="\n#之前按顺序选取过的结点有：【根节点】"):
        logger.info(f" attempt, id:{self.id}，{currentNode.id}")
        currentlevel+=1
        previousTitle = currentNode.get_title()
        previousInfo += f"【{previousTitle}】"
        
        while len(self.routeRecord) <= currentlevel:
            self.routeRecord.append([])

        # 将 currentNode.id 添加到 self.routeRecord[currentlevel] 数组中
        self.routeRecord[currentlevel].append(currentNode.id)
        
        
        fractions, agents = currentNode.get_nodes()
        selectionIds = []
        for agent in agents:
            selectionIds.append(agent.id)
        record = {
            "selections": selectionIds,
            "current": currentNode.id
        }

        self.selectionRecord.append(record)

        if currentNode.isFractionNode():
            for element in fractions:
                self.finaloutput.append(element)
                self.query.add_relatedFraction(element)
            return

        usedList = []
        tasks = []
        loopNum = top_k
        if currentlevel<2:
            loopNum = 1
        for num in range(loopNum):
            logger.info(f"self_id######{currentNode.id}")
            logger.info("****************")
            logger.info(usedList)
            node1 = await currentNode.seasrchSelect_strategy(self, usedList=usedList, previousInfo = previousInfo)

            logger.info(usedList)
            logger.info("#########****")

            if node1 is not None:
                usedList.append(node1.id)
                task = asyncio.create_task(self.search_agent_nodes(node1, top_k=top_k, currentlevel = currentlevel))
                tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks)
        else:
            logger.info("hit dead end$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.info(currentNode.get_title())
            logger.info(currentNode.get_id())
            logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

def extract_result_node_index(string):
    if not isinstance(string, (str, bytes)):
        return False, -1
    nodeIndex = 0
    if string:
        nodeIndex = 0
        match = re.search(r'\((\d+)\)', string)
        if match:
            logger.info(f"match!!!!{match.group(1)}")
            nodeIndex = int(match.group(1)) - 1
        else:
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
csv_file_path = "csv_database/health_database_final.csv"
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
output_file = 'knowledge_tree.json'
write_tree_to_json(startNode, output_file)


@app.post("/query")
async def query_question(request: Request):
    data = await request.json()
    question = data.get("question")
    attempt_number = data.get("attempt_number")
    top_k = data.get("top_k")
    outputSelectionMode = data.get("outputSelectionMode")
    query = Query(question, startNode)
    result, prompt, routeSummary,outputtitleList, title_count, returnedInfoList = await query.query_question(question, n = attempt_number, top_k = top_k, outputSelectionMode = outputSelectionMode)
    print("title_count!!!",title_count)
    return {"message": "Query processed successfully", "result": result, "prompt":prompt, "routeSummary":routeSummary, "outputtitleList":outputtitleList, "title_count":title_count, "returnedInfoList":returnedInfoList}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5070)
