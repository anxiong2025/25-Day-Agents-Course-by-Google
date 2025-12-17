"""
Human-in-the-Loop Server - 生产级 API 服务

提供完整的 REST API:
- POST /tasks          - 创建新任务
- GET  /tasks          - 获取任务列表
- GET  /tasks/{id}     - 获取任务详情
- POST /tasks/{id}/approve - 批准任务
- POST /tasks/{id}/reject  - 拒绝任务
- GET  /tasks/pending  - 获取待审批任务

同时提供 A2A 协议支持。

运行方式:
    python -m langgraph_agent.server
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(project_root, ".env"))

from langgraph_agent.hitl_agent import (
    run_hitl_agent,
    resume_after_approval,
    create_hitl_graph,
)
from langgraph_agent.checkpointer import (
    get_task_store,
    get_checkpointer,
    TaskMetadata,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# Pydantic Models
# ============================================================

class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    message: str = Field(..., description="用户输入的消息")
    metadata: Optional[dict] = Field(default=None, description="额外元数据")


class TaskCreateResponse(BaseModel):
    """创建任务响应"""
    task_id: str
    thread_id: str
    status: str
    requires_approval: bool
    risk_level: Optional[str] = None
    action_description: Optional[str] = None
    message: str


class ApprovalRequest(BaseModel):
    """审批请求"""
    approved: bool = Field(..., description="是否批准")
    comment: Optional[str] = Field(default="", description="审批意见")
    approver: Optional[str] = Field(default="system", description="审批人")


class ApprovalResponse(BaseModel):
    """审批响应"""
    task_id: str
    status: str
    result: Optional[str] = None
    message: str


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    thread_id: str
    status: str
    created_at: str
    updated_at: str
    current_node: Optional[str] = None
    pending_action: Optional[str] = None
    user_input: Optional[str] = None
    error_message: Optional[str] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: list[TaskInfo]
    total: int


class TaskDetailResponse(BaseModel):
    """任务详情响应"""
    task: TaskInfo
    state: Optional[dict] = None


# ============================================================
# 超时检查后台任务
# ============================================================

# 审批超时时间（秒）
APPROVAL_TIMEOUT_SECONDS = int(os.getenv("APPROVAL_TIMEOUT_SECONDS", "300"))  # 默认 5 分钟

async def check_approval_timeouts():
    """
    后台任务：检查审批超时

    每隔一段时间检查等待审批的任务，超时的自动拒绝
    """
    while True:
        try:
            task_store = get_task_store()
            pending_tasks = task_store.get_pending_approvals()

            for task in pending_tasks:
                # 检查是否超时
                created_at = datetime.fromisoformat(task.created_at)
                timeout_at = created_at + timedelta(seconds=APPROVAL_TIMEOUT_SECONDS)

                if datetime.utcnow() > timeout_at:
                    logger.warning(f"Task {task.task_id} approval timeout, auto-rejecting")

                    # 自动拒绝
                    try:
                        resume_after_approval(
                            task_id=task.task_id,
                            thread_id=task.thread_id,
                            approved=False,
                            comment="审批超时，自动拒绝",
                            approver="system_timeout",
                        )
                        task_store.update_task(task.task_id, status="timeout")
                    except Exception as e:
                        logger.error(f"Failed to auto-reject task {task.task_id}: {e}")

        except Exception as e:
            logger.error(f"Error in timeout check: {e}")

        # 每 30 秒检查一次
        await asyncio.sleep(30)


# ============================================================
# FastAPI App
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting HITL Server...")
    logger.info(f"Approval timeout: {APPROVAL_TIMEOUT_SECONDS} seconds")

    # 启动超时检查后台任务
    timeout_task = asyncio.create_task(check_approval_timeouts())

    yield

    # 关闭时
    logger.info("Shutting down HITL Server...")
    timeout_task.cancel()
    try:
        await timeout_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Human-in-the-Loop Agent API",
    description="生产级 Human-in-the-Loop Agent 服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（Web UI）
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ============================================================
# Web UI 入口
# ============================================================

@app.get("/ui", tags=["Web UI"])
async def web_ui():
    """Web UI 入口页面"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Web UI not found")


# ============================================================
# API 端点
# ============================================================

@app.post("/tasks", response_model=TaskCreateResponse, tags=["Tasks"])
async def create_task(request: TaskCreateRequest, background_tasks: BackgroundTasks):
    """
    创建新任务

    流程:
    1. 分析用户请求
    2. 评估风险等级
    3. 如果需要审批，返回等待审批状态
    4. 如果不需要审批，直接执行并返回结果
    """
    try:
        logger.info(f"Creating task for: {request.message[:50]}...")

        # 运行 Agent
        result = run_hitl_agent(request.message)

        task_id = result["task_id"]
        thread_id = result["thread_id"]
        status = result["status"]
        agent_result = result.get("result", {})

        # 提取关键信息
        requires_approval = agent_result.get("requires_approval", False)
        risk_level = agent_result.get("risk_level", "")
        action_plan = agent_result.get("action_plan", {})
        action_description = action_plan.get("description", "")
        final_answer = agent_result.get("final_answer", "")

        # 根据状态返回不同消息
        if status == "waiting_approval":
            message = f"任务需要审批。风险等级: {risk_level}，操作: {action_description}"
        elif status == "completed":
            message = final_answer or "任务已完成"
        else:
            message = f"任务状态: {status}"

        return TaskCreateResponse(
            task_id=task_id,
            thread_id=thread_id,
            status=status,
            requires_approval=requires_approval,
            risk_level=risk_level,
            action_description=action_description,
            message=message,
        )

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def list_tasks(status: Optional[str] = None, limit: int = 50):
    """
    获取任务列表

    可选参数:
    - status: 按状态筛选 (pending, waiting_approval, approved, rejected, completed, failed)
    - limit: 返回数量限制
    """
    try:
        task_store = get_task_store()

        if status:
            tasks = task_store.get_tasks_by_status(status)
        else:
            # 获取所有任务（通过获取各状态的任务合并）
            all_tasks = []
            for s in ["pending", "waiting_approval", "approved", "rejected", "completed", "failed", "timeout"]:
                all_tasks.extend(task_store.get_tasks_by_status(s))
            # 按创建时间排序
            tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)

        # 限制数量
        tasks = tasks[:limit]

        return TaskListResponse(
            tasks=[
                TaskInfo(
                    task_id=t.task_id,
                    thread_id=t.thread_id,
                    status=t.status,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                    current_node=t.current_node,
                    pending_action=t.pending_action,
                    user_input=t.user_input,
                    error_message=t.error_message,
                )
                for t in tasks
            ],
            total=len(tasks),
        )

    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/pending", response_model=TaskListResponse, tags=["Tasks"])
async def get_pending_approvals():
    """获取所有待审批的任务"""
    try:
        task_store = get_task_store()
        tasks = task_store.get_pending_approvals()

        return TaskListResponse(
            tasks=[
                TaskInfo(
                    task_id=t.task_id,
                    thread_id=t.thread_id,
                    status=t.status,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                    current_node=t.current_node,
                    pending_action=t.pending_action,
                    user_input=t.user_input,
                    error_message=t.error_message,
                )
                for t in tasks
            ],
            total=len(tasks),
        )

    except Exception as e:
        logger.error(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}", response_model=TaskDetailResponse, tags=["Tasks"])
async def get_task(task_id: str):
    """获取任务详情"""
    try:
        task_store = get_task_store()
        task = task_store.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        # 获取图状态（如果有）
        state = None
        try:
            checkpointer = get_checkpointer()
            config = {"configurable": {"thread_id": task.thread_id}}
            graph = create_hitl_graph(checkpointer)
            state_snapshot = graph.get_state(config)
            if state_snapshot:
                state = dict(state_snapshot.values) if state_snapshot.values else None
        except Exception as e:
            logger.warning(f"Failed to get state for task {task_id}: {e}")

        return TaskDetailResponse(
            task=TaskInfo(
                task_id=task.task_id,
                thread_id=task.thread_id,
                status=task.status,
                created_at=task.created_at,
                updated_at=task.updated_at,
                current_node=task.current_node,
                pending_action=task.pending_action,
                user_input=task.user_input,
                error_message=task.error_message,
            ),
            state=state,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/{task_id}/approve", response_model=ApprovalResponse, tags=["Approval"])
async def approve_task(task_id: str, request: ApprovalRequest):
    """
    审批任务（批准）

    批准后，任务将继续执行
    """
    if not request.approved:
        raise HTTPException(
            status_code=400,
            detail="Use /tasks/{task_id}/reject for rejection"
        )

    return await _process_approval(task_id, True, request.comment, request.approver)


@app.post("/tasks/{task_id}/reject", response_model=ApprovalResponse, tags=["Approval"])
async def reject_task(task_id: str, request: ApprovalRequest):
    """
    审批任务（拒绝）

    拒绝后，任务将终止并返回拒绝原因
    """
    return await _process_approval(task_id, False, request.comment, request.approver)


async def _process_approval(
    task_id: str,
    approved: bool,
    comment: str,
    approver: str,
) -> ApprovalResponse:
    """处理审批"""
    try:
        task_store = get_task_store()
        task = task_store.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if task.status != "waiting_approval":
            raise HTTPException(
                status_code=400,
                detail=f"Task is not waiting for approval. Current status: {task.status}"
            )

        logger.info(f"Processing approval for task {task_id}: approved={approved}")

        # 恢复执行
        result = resume_after_approval(
            task_id=task_id,
            thread_id=task.thread_id,
            approved=approved,
            comment=comment or "",
            approver=approver or "system",
        )

        # 获取最终结果
        agent_result = result.get("result", {})
        final_answer = agent_result.get("final_answer", "")

        action = "批准" if approved else "拒绝"
        return ApprovalResponse(
            task_id=task_id,
            status=result["status"],
            result=final_answer,
            message=f"任务已{action}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process approval for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 健康检查
# ============================================================

@app.get("/health", tags=["System"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "approval_timeout_seconds": APPROVAL_TIMEOUT_SECONDS,
    }


@app.get("/", tags=["System"])
async def root():
    """API 根路径"""
    return {
        "name": "Human-in-the-Loop Agent API",
        "version": "1.0.0",
        "web_ui": "/ui",
        "docs": "/docs",
        "endpoints": {
            "create_task": "POST /tasks",
            "list_tasks": "GET /tasks",
            "pending_approvals": "GET /tasks/pending",
            "get_task": "GET /tasks/{task_id}",
            "approve": "POST /tasks/{task_id}/approve",
            "reject": "POST /tasks/{task_id}/reject",
        }
    }


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Day 16: Human-in-the-Loop Agent Server")
    print("=" * 60)
    print()
    print("访问地址:")
    print("  Web UI:   http://localhost:8016/ui   <- 推荐")
    print("  API Docs: http://localhost:8016/docs")
    print()
    print("API 端点:")
    print("  POST /tasks           - 创建新任务")
    print("  GET  /tasks           - 获取任务列表")
    print("  GET  /tasks/pending   - 获取待审批任务")
    print("  POST /tasks/{id}/approve - 批准任务")
    print("  POST /tasks/{id}/reject  - 拒绝任务")
    print()
    print(f"审批超时: {APPROVAL_TIMEOUT_SECONDS} 秒")
    print("=" * 60)
    print()

    uvicorn.run(app, host="localhost", port=8016)
