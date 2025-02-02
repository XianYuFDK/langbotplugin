from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.platform.types import MessageChain, File
import time
import tempfile
import os
import asyncio

@register(name="LangBotChatLogger", description="长消息转聊天记录文件", version="0.3", author="YourName")
class LangBotChatLogger(BasePlugin):

    def __init__(self, host: APIHost):
        # 配置参数
        self.config = {
            'threshold': 200,  # 触发转换的字符数
            'file_prefix': '[聊天记录]',
            'keep_temp': False  # 是否保留临时文件（调试用）
        }
        
        # 初始化临时目录
        self.temp_dir = tempfile.gettempdir()
        os.makedirs(os.path.join(self.temp_dir, "langbot_files"), exist_ok=True)

    async def _create_chat_file(self, message: str, ctx: EventContext) -> str:
        """创建聊天记录文件"""
        try:
            # 生成文件名
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"{self.config['file_prefix']}{timestamp}.txt"
            filepath = os.path.join(self.temp_dir, "langbot_files", filename)
            
            # 写入内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=== 聊天记录 ===\n")
                f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # 根据事件类型添加上下文信息
                if isinstance(ctx.event, GroupNormalMessageReceived):
                    f.write(f"群组: {ctx.event.group_id}\n")
                    f.write(f"发送者: {ctx.event.sender_id}\n")
                elif isinstance(ctx.event, PersonNormalMessageReceived):
                    f.write(f"接收者: {ctx.event.sender_id}\n")
                
                f.write("\n消息内容:\n")
                f.write(message)
            
            return filepath
        except Exception as e:
            self.ap.logger.error(f"文件创建失败: {str(e)}")
            return None

    @handler(PersonNormalMessageReceived, GroupNormalMessageReceived)
    async def handle_message(self, ctx: EventContext):
        """处理消息接收事件"""
        try:
            # 获取消息内容
            message = ctx.event.text_message.strip()
            
            # 长度检查
            if len(message) < self.config['threshold']:
                return

            # 创建聊天文件
            filepath = await self._create_chat_file(message, ctx)
            if not filepath:
                return

            # 构造消息链
            file_msg = MessageChain([
                Plain("以下消息已转为聊天记录文件：\n"),
                File(filepath)
            ])

            # 替换原回复
            ctx.prevent_default()  # 阻止默认回复
            await ctx.reply(file_msg)  # 发送文件消息

            # 清理临时文件
            if not self.config['keep_temp']:
                asyncio.create_task(self._cleanup_file(filepath))
                
        except Exception as e:
            self.ap.logger.error(f"消息处理异常: {str(e)}")

    async def _cleanup_file(self, filepath: str, delay: int = 30):
        """延迟清理文件"""
        await asyncio.sleep(delay)
        try:
            os.remove(filepath)
            self.ap.logger.debug(f"已清理临时文件: {filepath}")
        except Exception as e:
            self.ap.logger.warning(f"文件清理失败: {str(e)}")

    # 其他辅助方法...
