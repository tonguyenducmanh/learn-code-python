import json
import requests
from typing import Any, List, Optional

from agno.tools import Toolkit
from agno.utils.log import log_debug


class BirthdayTools(Toolkit):
    """
    BirthdayTools là một toolkit để gọi workflow Dify cho sinh nhật.
    Args:
        api_key (str): API Key của Dify.
        base_url (str): URL endpoint (mặc định là https://api.dify.ai/v1/workflows/run).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.dify.ai/v1/workflows/run",
        **kwargs,
    ):
        self.api_key = api_key
        self.base_url = base_url

        tools: List[Any] = [self.call_birthday_workflow]

        super().__init__(name="birthday", tools=tools, **kwargs)

    def call_birthday_workflow(self, time: str = "today", user: str = "abc-123") -> str:
        """
        Gọi workflow Dify để xử lý logic birthday.
        Args:
            time (str): Giá trị cho trường "time" trong inputs, chỉ có thể là today hoặc tomorrow
            user (str): ID người dùng. chỉ có thể là abc-123
        Returns:
            str: Kết quả trả về từ API (JSON).
        """
        log_debug(f"Gọi Dify Workflow với time={time}, user={user}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": {
                "time": time
            },
            "response_mode": "streaming",  # Nếu muốn thay đổi có thể chỉnh ở đây
            "user": user
        }

        response = requests.post(self.base_url, headers=headers, json=payload, stream=True)

        # Đọc stream và trả về dạng chuỗi gộp
        result = ""
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                result += decoded + "\n"

        return result
