
import asyncio
import httpx

async def call_query_api(question: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post("http://0.0.0.0:5070/query", json={"question": question, "attempt_number":5, "top_k":2, "outputSelectionMode":"true_false_judge"})
            # response = await client.post("http://0.0.0.0:5070/query", json={"question": question, "attempt_number":5, "top_k":2, "outputSelectionMode":"tree_judge"})
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                prompt = data.get("prompt")
                outputtitleList = data.get("outputtitleList")
                routeSummary = data.get("routeSummary")
                title_count = data.get("title_count")
                returnedInfoList = data.get("returnedInfoList")
                print("-----------result---------------")
                print(result)
                print("-----------prompt---------------")
                print(prompt)
                print("-----------routeSummary---------------")
                print(routeSummary)
                print("-----------outputtitleList---------------")
                print(outputtitleList)
                print("-----------title_count---------------")
                print(title_count)
                print("-----------returnedInfoList---------------")
                print(returnedInfoList)
                
                print("Query processed successfully")
            else:
                print(f"Error: {response.status_code}")
    except httpx.RequestError as e:
        print(f"An error occurred while requesting: {str(e)}")
# question = "国考的新增指标有哪些？"
# question = "神经毒素是如何导致蜱瘫痪的？解释一下"
# question = "特需医疗服务占比是啥？"
# question = "什么导致了稍延迟的I 型过敏反应？"
# question = "蜱可传播哪些病原体导致感染性疾病？"
question = "我应该如何调整我的生活习惯来更好地控制发作性睡病呢？"
asyncio.run(call_query_api(question))

