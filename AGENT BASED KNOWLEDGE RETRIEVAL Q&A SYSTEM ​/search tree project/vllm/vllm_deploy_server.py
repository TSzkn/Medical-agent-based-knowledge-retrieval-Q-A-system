

import os
import re
 #修改需要的卡，可以占用的卡
os.environ["CUDA_VISIBLE_DEVICES"] = "2"
import argparse
import json
from typing import AsyncGenerator
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
import uvicorn

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('LLM.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('uvicorn')
 
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm import SamplingParams
from vllm.utils import random_uuid


TIMEOUT_KEEP_ALIVE = 5  # seconds
TIMEOUT_TO_PEVENT_DEADLOCK = 1 # seconds
app = FastAPI()

@app.post("/data")
async def generate(request: Request) -> Response:
    """
    Generate Completion for the request.
    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the genreration.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See 'SamplingParams' for details).
    """
 
    try:
        request_dict = await request.json()
        # contexts = request_dict.pop("contexts")
        # contexts = request_dict.get("data", {}).get("context")
        contexts = request_dict.pop("input")
        history = request_dict.pop("history",[])
        
        # no prompt adjustment
        prompt = contexts
        # salt_uuid = request_dict.pop("salt_uuid", "null")
        salt_uuid="null"
        # logger.info("prompt!!!")
        logger.info("input_prompt:",prompt)
        stream = request_dict.pop("stream", False) 
        # sampling_params = SamplingParams(**request_dict)
        # sampling_params = SamplingParams(n=1, temperature=0.95, top_p=0.65, top_k=20, max_tokens=128)
        # sampling_params = SamplingParams(best_of=1, temperature=1e-6, top_p=1, top_k=-1, max_tokens=256, ignore_eos=False)
        sampling_params = SamplingParams(n=1, best_of=1, top_p=0.8, temperature=0.8, max_tokens=4096)
        # sampling_params = SamplingParams(n=1, temperature=0, best_of=5, top_p=1.0, top_k=-1, use_beam_search=True, max_tokens=128)
 
        request_uuid = random_uuid()
        # logger.info("prompt!!!",prompt)
        results_generator = engine.generate(prompt, sampling_params, request_uuid)
        # logger.info("results_generator: %s",results_generator)
        # Streaming case
        async def stream_results() -> AsyncGenerator[bytes, None]:
            async for request_output in results_generator:
                prompt = request_output.prompt
                text_outputs = [
                    prompt + output.text for output in request_output.outputs
                ]
                ret = {"text": text_outputs}
                yield (json.dumps(ret) + "\0").encode("utf-8")
        async def abort_request() -> None:
            await engine.abort(request_id)
 
        if stream:
            background_tasks = BackgroundTasks()
            # Abort the request if the client disconnects.
            background_tasks.add_task(abort_request)
            return StreamingResponse(stream_results(), background=background_tasks)
 
        # Non-streaming case
        final_output = None
        async for request_output in results_generator:
            if await request.is_disconnected():
                # Abort the request if the client disconnect.
                await engine.abort(request_id)
                return Response(status_code=499)
            final_output = request_output
        assert final_output is not None
        text_outputs = [output.text for output in final_output.outputs]
        # logger.info("text_outputs:",text_outputs[0])

        # ret = {"data": {"text": text_outputs}, "code": 5200, "message": "调试成功", "salt_uuid": salt_uuid}
        ret = {"response": text_outputs[0], "model_location": "default location", "description": "default description"}
    except Exception as e:
        ret = {"data": {"text": ""}, "code": 5201, "message": f"调用失败\n错误信息: {e}, ", "salt_uuid": salt_uuid}
    return JSONResponse(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5095)
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()
 
    engine_args = AsyncEngineArgs.from_cli_args(args)
    engine = AsyncLLMEngine.from_engine_args(engine_args)
 
    uvicorn.run(app,
                host=args.host,
                port=args.port,
                log_level="info",
                timeout_keep_alive=TIMEOUT_KEEP_ALIVE)

# python vllm_deploy_vserver.py --model "/root/chatglm3-6b-vllm-search-agent" --tensor-parallel-size 1 --gpu-memory-utilization 0.5 --trust-remote-code --dtype half