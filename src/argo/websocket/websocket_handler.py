# argo/websocket/websocket_handler.py

from fastapi import FastAPI, Path, Query
from starlette.websockets import WebSocket, WebSocketDisconnect
import json

from argo.kernel.schema import WebSocketMessage, MessageType
from argo.command.commands import CommandContext
from argo.configs import logger

def setup_websocket(app: FastAPI, runtime_state):
    @app.websocket("/ws/{uid}")
    async def websocket_endpoint(
            websocket: WebSocket,
            uid: str = Path(..., description="User ID"),
            token: str = Query(None, description="Authentication token")
    ):
        if token:
            #TODO:Add auth
            pass

        if uid in runtime_state.ws_manager.active_connections:
            await websocket.close(code=1008, reason="User ID already connected")
            return


        await runtime_state.ws_manager.connect(uid, websocket)
        context = CommandContext(uid, websocket, runtime_state)

        try:
            welcome_msg = WebSocketMessage(
                type=MessageType.SYSTEM,
                content=f"Welcome {uid}! Type /help for available commands or send JSON message to chat."
            )
            await websocket.send_json(welcome_msg.model_dump())

            while True:
                try:
                    data = await websocket.receive_text()
                    data = data.strip()

                    try:
                        message = WebSocketMessage.model_validate_json(data)
                        if message.type == MessageType.COMMAND:
                            parts = message.content.split()
                            if parts:
                                command = parts[0]
                                args = parts[1:]
                                await runtime_state.command_manager.execute(command, args, context)

                        elif message.type == MessageType.CHAT:
                            async def handle_chat_message(message: WebSocketMessage):
                                if message.agent_id:
                                    agent = await runtime_state.character_manager.get_agent(message.agent_id)
                                    if agent:
                                        try:
                                            if message.stream:
                                                async for chunk in  agent.achat(message.content, context):
                                                    stream_msg = WebSocketMessage(
                                                        type=MessageType.CHAT_STREAM,
                                                        content=chunk,
                                                        agent_id=message.agent_id,
                                                        is_final=False
                                                    )
                                                    await runtime_state.ws_manager.send_to_user(
                                                        uid,
                                                        stream_msg.model_dump()
                                                    )



                                                final_msg = WebSocketMessage(
                                                    type=MessageType.CHAT_STREAM,
                                                    content="",
                                                    agent_id=message.agent_id,
                                                    is_final=True
                                                )
                                                await runtime_state.ws_manager.send_to_user(
                                                    uid,
                                                    final_msg.model_dump()
                                                )
                                            else:
                                                response = await agent.chat(message.content, context)
                                                response_msg = WebSocketMessage(
                                                    type=MessageType.CHAT,
                                                    content=response,
                                                    agent_id=message.agent_id
                                                )
                                                await runtime_state.ws_manager.send_to_user(
                                                    uid,
                                                    response_msg.model_dump()
                                                )
                                        except Exception as e:
                                            error_msg = WebSocketMessage(
                                                type=MessageType.SYSTEM,
                                                content=f"Error processing chat: {str(e)}"
                                            )
                                            await websocket.send_json(error_msg.model_dump())
                                            logger.error(f"Error processing chat for {uid}: {e}")
                                    else:
                                        error_msg = WebSocketMessage(
                                            type=MessageType.CHAT,
                                            content=f"Agent {message.agent_id} not found"
                                        )
                                        logger.error(f"Agent not found for {uid}")
                                        await websocket.send_json(error_msg.model_dump())
                            await handle_chat_message(message)
                        else:
                            error_msg = WebSocketMessage(
                                type=MessageType.SYSTEM,
                                content="Please specify an agent_id for chat"
                            )
                            await websocket.send_json(error_msg.dict())

                    except ValueError:
                        if data.startswith('/'):
                            parts = data[1:].split()
                            if parts:
                                command = parts[0]
                                args = parts[1:]
                                await runtime_state.command_manager.execute(command, args, context)
                        else:
                            error_msg = WebSocketMessage(
                                type=MessageType.SYSTEM,
                                content="Invalid message format. Use JSON format or /command args"
                            )
                            await websocket.send_json(error_msg.model_dump())

                except json.JSONDecodeError:
                    error_msg = WebSocketMessage(
                        type=MessageType.SYSTEM,
                        content="Invalid JSON format"
                    )
                    await websocket.send_json(error_msg.model_dump())

        except WebSocketDisconnect:
            runtime_state.ws_manager.disconnect(uid)
            disconnect_msg = WebSocketMessage(
                type=MessageType.SYSTEM,
                content=f"User {uid} disconnected"
            )
            await runtime_state.ws_manager.broadcast(disconnect_msg.model_dump())
            logger.info(f"websocket disconnected for {uid}")
        except Exception as e:
            logger.error(f"WebSocket error for user {uid}: {e}")
            error_msg = WebSocketMessage(
                type=MessageType.SYSTEM,
                content=f"Error: {str(e)}"
            )
            await websocket.send_json(error_msg.model_dump())
        finally:
            runtime_state.ws_manager.disconnect(uid)
            logger.info(f"finally websocket disconnected for {uid}")

