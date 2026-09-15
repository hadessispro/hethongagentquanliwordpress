import os
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Header, HTTPException, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mcp.server.mcpserver import MCPServer
from mcp.server.sse import TransportSecuritySettings

from mcp_server.config import settings
import mcp_server.workspace_tools as wt
import mcp_server.ponytail_tools as pt

# 1. Initialize official MCPServer
mcp = MCPServer('LocalWorkspacePonytailMCP')

# Register MCP Tools
@mcp.tool(name='list_directory', description='List files and folders within the workspace directory.')
def mcp_list_directory(path: str = '.', recursive: bool = False, max_depth: int = 2) -> Dict[str, Any]:
    return wt.list_directory(path, recursive, max_depth)

@mcp.tool(name='read_file', description='Read contents of a text file within the workspace.')
def mcp_read_file(path: str, start_line: int = 1, end_line: int = -1) -> Dict[str, Any]:
    return wt.read_file(path, start_line, end_line)

@mcp.tool(name='write_file', description='Create or overwrite a file in the workspace.')
def mcp_write_file(path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
    return wt.write_file(path, content, overwrite)

@mcp.tool(name='edit_file', description='Replace target snippet with replacement in a file.')
def mcp_edit_file(path: str, target_snippet: str, replacement: str) -> Dict[str, Any]:
    return wt.edit_file(path, target_snippet, replacement)

@mcp.tool(name='delete_file', description='Delete a file or empty directory in the workspace.')
def mcp_delete_file(path: str) -> Dict[str, Any]:
    return wt.delete_file(path)

@mcp.tool(name='search_files', description='Search file names or file contents in workspace for query string.')
def mcp_search_files(query: str, path: str = '.', case_sensitive: bool = False, extension: str = '') -> Dict[str, Any]:
    return wt.search_files(query, path, case_sensitive, extension)

@mcp.tool(name='execute_command', description='Execute a terminal command (PowerShell) in workspace directory.')
def mcp_execute_command(command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    return wt.execute_command(command, timeout)

@mcp.tool(name='get_workspace_info', description='Get workspace path, disk space, and environment info.')
def mcp_get_workspace_info() -> Dict[str, Any]:
    return wt.get_workspace_info()

@mcp.tool(name='switch_workspace', description='Switch active workspace directory to a new folder on the computer.')
def mcp_switch_workspace(new_path: str) -> Dict[str, Any]:
    return wt.switch_workspace(new_path)

@mcp.tool(name='list_available_drives', description='List available drives (C:/, D:/...) and user folders on Windows.')
def mcp_list_available_drives() -> Dict[str, Any]:
    return wt.list_available_drives()

@mcp.tool(name='ponytail_instructions', description='Return Ponytail lazy-senior-dev ruleset (mode: lite, full, or ultra).')
def mcp_ponytail_instructions(mode: Optional[str] = None) -> Dict[str, str]:
    return pt.get_ponytail_instructions(mode)

@mcp.tool(name='ponytail_audit', description='Audit code files in workspace for bloat and over-engineering.')
def mcp_ponytail_audit(path: str = '.') -> Dict[str, Any]:
    return pt.audit_workspace(path)

# Register MCP Prompts
@mcp.prompt(name='ponytail', description='Activate Ponytail Lazy Senior Developer persona.')
def mcp_prompt_ponytail(mode: Optional[str] = None) -> Dict[str, Any]:
    instr = pt.get_ponytail_instructions(mode)
    return {
        'messages': [
            {'role': 'user', 'content': {'type': 'text', 'text': instr['instructions']}}
        ]
    }

# 2. Setup Transports with DNS rebinding protection disabled for ngrok compatibility
transport_sec = TransportSecuritySettings(enable_dns_rebinding_protection=False)
sse_starlette = mcp.sse_app(transport_security=transport_sec)
http_starlette = mcp.streamable_http_app(transport_security=transport_sec)

# 3. Create FastAPI app with Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize streamable HTTP task group
    async with http_starlette.router.lifespan_context(app):
        yield

app = FastAPI(
    title='Local Workspace MCP & REST Server for GPT',
    description='Provides local workspace filesystem access, PowerShell execution, and Ponytail rules for ChatGPT / Custom GPTs over ngrok.',
    version='1.0.0',
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Auth helper
def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias='X-API-Key'),
    authorization: Optional[str] = Header(None)
):
    if not settings.API_KEY:
        return True
    
    token = x_api_key
    if not token and authorization and authorization.startswith('Bearer '):
        token = authorization[7:].strip()
        
    if token != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or missing API Key')
    return True

# Pydantic models for REST endpoints
class WriteFileRequest(BaseModel):
    path: str = Field(..., description='Relative path to file in workspace')
    content: str = Field(..., description='File content to write')
    overwrite: bool = Field(True, description='Overwrite if file exists')

class EditFileRequest(BaseModel):
    path: str = Field(..., description='Relative path to file in workspace')
    target_snippet: str = Field(..., description='Exact snippet to replace')
    replacement: str = Field(..., description='Replacement content')

class DeleteFileRequest(BaseModel):
    path: str = Field(..., description='Relative path to file or directory')

class ExecuteCommandRequest(BaseModel):
    command: str = Field(..., description='PowerShell command to execute')
    timeout: Optional[int] = Field(None, description='Timeout in seconds')

# REST Endpoints for OpenAPI / Custom GPT Actions
@app.get('/health', tags=['General'], summary='Health check endpoint')
def health_check():
    return {'status': 'ok', 'server': 'Local MCP & REST Server for GPT'}

@app.get('/api/workspace/info', tags=['Workspace'], summary='Get workspace details')
def rest_workspace_info(auth: bool = Header(True, include_in_schema=False)):
    return wt.get_workspace_info()

@app.post('/api/workspace/switch', tags=['Workspace'], summary='Switch active workspace directory')
def rest_switch_workspace(new_path: str = Query(..., description='New folder path on the computer')):
    try:
        return wt.switch_workspace(new_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/workspace/drives', tags=['Workspace'], summary='List available drives and common folders')
def rest_list_drives():
    return wt.list_available_drives()

@app.get('/api/files/list', tags=['Filesystem'], summary='List files and directories')
def rest_list_directory(
    path: str = Query('.', description='Relative path in workspace'),
    recursive: bool = Query(False, description='Recursively scan directories'),
    max_depth: int = Query(2, description='Max depth for recursion')
):
    try:
        return wt.list_directory(path, recursive, max_depth)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/files/read', tags=['Filesystem'], summary='Read a file')
def rest_read_file(
    path: str = Query(..., description='Relative path to file'),
    start_line: int = Query(1, description='1-indexed starting line'),
    end_line: int = Query(-1, description='Ending line, or -1 for end of file')
):
    try:
        return wt.read_file(path, start_line, end_line)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/api/files/write', tags=['Filesystem'], summary='Create or overwrite a file')
def rest_write_file(req: WriteFileRequest):
    try:
        return wt.write_file(req.path, req.content, req.overwrite)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/api/files/edit', tags=['Filesystem'], summary='Replace snippet in a file')
def rest_edit_file(req: EditFileRequest):
    try:
        return wt.edit_file(req.path, req.target_snippet, req.replacement)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete('/api/files/delete', tags=['Filesystem'], summary='Delete file or empty directory')
def rest_delete_file(path: str = Query(..., description='Relative path to file or directory')):
    try:
        return wt.delete_file(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/files/search', tags=['Filesystem'], summary='Search files by query string')
def rest_search_files(
    query: str = Query(..., description='Search query'),
    path: str = Query('.', description='Directory to search within'),
    case_sensitive: bool = Query(False, description='Case sensitive search'),
    extension: str = Query('', description='Filter by extension, e.g. .py')
):
    try:
        return wt.search_files(query, path, case_sensitive, extension)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/api/terminal/execute', tags=['Terminal'], summary='Execute PowerShell command')
def rest_execute_command(req: ExecuteCommandRequest):
    try:
        return wt.execute_command(req.command, req.timeout)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/ponytail/instructions', tags=['Ponytail'], summary='Get Ponytail lazy senior dev instructions')
def rest_ponytail_instructions(mode: Optional[str] = Query(None, description='lite, full, or ultra')):
    return pt.get_ponytail_instructions(mode)

@app.get('/api/ponytail/audit', tags=['Ponytail'], summary='Audit workspace for code bloat')
def rest_ponytail_audit(path: str = Query('.', description='Relative path to audit')):
    try:
        return pt.audit_workspace(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Attach MCP routes
app.routes.extend(sse_starlette.routes)
app.routes.extend(http_starlette.routes)
