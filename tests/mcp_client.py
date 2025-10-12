#!/usr/bin/env python3
"""
Simple MCP Client utility for testing Web Explorer MCP server.

This utility provides a command-line interface for interacting with the
Web Explorer MCP server for end-to-end testing purposes.
"""

from typing import Any

from fastmcp import Client
from loguru import logger


class MCPClient:
    """Simple MCP client for end-to-end testing."""

    def __init__(self, server_source: Any):
        """
        Initialize the MCP client.

        Parameters
        ----------
        server_source : Any
            Server source - can be FastMCP instance, file path, or URL
        """
        self.client = Client(server_source)
        self._connected = False

    async def connect(self) -> bool:
        """
        Connect to the server.

        Returns
        -------
        bool
            True if connected successfully
        """
        try:
            await self.client.__aenter__()
            self._connected = True
            logger.info("Connected to MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the server."""
        if self._connected:
            try:
                await self.client.__aexit__(None, None, None)
                self._connected = False
                logger.info("Disconnected from MCP server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

    async def ping(self) -> bool:
        """
        Ping the server to check connectivity.

        Returns
        -------
        bool
            True if server responded to ping
        """
        try:
            await self.client.ping()
            logger.info("Server ping successful")
            return True
        except Exception as e:
            logger.error(f"Server ping failed: {e}")
            return False

    async def list_tools(self) -> list[dict]:
        """
        List available tools on the server.

        Returns
        -------
        list[dict]
            List of available tools with their metadata
        """
        try:
            tools = await self.client.list_tools()
            logger.info(f"Retrieved {len(tools)} tools")
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
                for tool in tools
            ]
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """
        Call a tool on the server.

        Parameters
        ----------
        name : str
            Tool name to call
        arguments : dict
            Arguments to pass to the tool

        Returns
        -------
        dict
            Tool execution result
        """
        try:
            result = await self.client.call_tool(name, arguments)
            logger.info(f"Tool '{name}' executed successfully")
            return {"success": True, "data": result.data, "error": None}
        except Exception as e:
            logger.error(f"Tool '{name}' execution failed: {e}")
            return {"success": False, "data": None, "error": str(e)}

    async def list_resources(self) -> list[dict]:
        """
        List available resources on the server.

        Returns
        -------
        list[dict]
            List of available resources
        """
        try:
            resources = await self.client.list_resources()
            logger.info(f"Retrieved {len(resources)} resources")
            return [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                }
                for resource in resources
            ]
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []

    async def list_prompts(self) -> list[dict]:
        """
        List available prompts on the server.

        Returns
        -------
        list[dict]
            List of available prompts
        """
        try:
            prompts = await self.client.list_prompts()
            logger.info(f"Retrieved {len(prompts)} prompts")
            return [
                {
                    "name": prompt.name,
                    "description": prompt.description,
                }
                for prompt in prompts
            ]
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            return []
