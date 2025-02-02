from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import GroupNormalMessageReceived, PersonNormalMessageReceived
from pkg.platform.types import MessageChain, File, Plain
import tempfile
import os
import time
import asyncio

@register(name="ChatLogger", 
         description="长消息转聊天记录文件", 
         version="1.1",
         author="YourName")
class ChatLoggerPlugin(BasePlugin):
    
    def __init__(self, host: APIHost):
        """初始化配置参数"""
        self.config = {
            'threshold': 200,      # 触发转换的字符阈值
            'file_prefix': '[记录]', # 文件前缀
            'retention': 30,       # 文件保留时间（秒）
            'max_size': 5000       # 最大支持处理字符数
        }
        
        # 创建临时目录
        self.temp_dir = os.path.join(tempfile.gettempdir(), "chat_logs")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def initialize(self):
        """异步初始化"""
        self.ap.logger.info(f"ChatLogger 加载成功 | 阈值:{self.config['threshold']}字符")

    @handler(GroupNormalMessageReceived, PersonNormalMessageReceived)
    async def handle_message(self, ctx: EventContext):
        """处理消息接收事件"""
        try:
            # 获取消息内容
            message = ctx.event.text_message.strip()
            
            # 长度检查
            if not self._should_convert(message):
                return
                
            # 生成聊天记录文件
            file_path = await self._generate_log_file(ctx, message)
            
            # 构造回复消息
            reply_msg = MessageChain([
                Plain("您发送的消息过长，已转为文件：\n"),
                File(file_path)
            ])
            
            # 发送并阻止默认回复
            ctx.prevent_default()
            await ctx.reply(reply_msg)
            
            # 安排清理任务
            asyncio.create_task(self._cleanup_file(file_path))
            
        except Exception as e:
            self.ap.logger.error(f"处理消息异常: {str(e)}", exc_info=True)
            await ctx.reply(MessageChain([Plain("消息处理失败，请稍后重试")]))

    def _should_convert(self, message: str) -> bool:
        """判断是否需要转换"""
        return len(message) >= self.config['threshold'] and len(message) <= self.config['max_size']

    async def _generate_log_file(self, ctx: EventContext, content: str) -> str:
        """生成日志文件"""
        try:
            # 构造文件名
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"{self.config['file_prefix']}{timestamp}.txt"
            file_path = os.path.join(self.temp_dir, filename)
            
            # 写入文件内容
            with open(file_path, 'w', encoding='utf-8') as f:
                # 基础信息
                f.write(f"=== 聊天记录 ===\n")
                f.write(f"生成时间: {time.ctime()}\n")
                
                # 上下文信息
                if isinstance(ctx.event, GroupNormalMessageReceived):
                    f.write(f"群组ID: {ctx.event.group_id}\n")
                    f.write(f"发送者ID: {ctx.event.sender_id}\n")
                else:
                    f.write(f"用户ID: {ctx.event.sender_id}\n")
                
                # 消息内容
                f.write("\n消息内容：\n")
                f.write(content)
            
            return file_path
            
        except IOError as e:
            self.ap.logger.error(f"文件写入失败: {str(e)}")
            raise RuntimeError("文件创建失败")

    async def _cleanup_file(self, file_path: str):
        """异步清理文件"""
        await asyncio.sleep(self.config['retention'])
        try:
            os.remove(file_path)
            self.ap.logger.debug(f"已清理文件: {os.path.basename(file_path)}")
        except Exception as e:
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import GroupNormalMessageReceived, PersonNormalMessageReceived
from pkg.platform.types import MessageChain, File, Plain
import tempfile
import os
import time
import asyncio

@register(name="ChatLogger", 
         description="长消息转聊天记录文件", 
         version="1.1",
         author="YourName")
class ChatLoggerPlugin(BasePlugin):
    
    def __init__(self, host: APIHost):
        """初始化配置参数"""
        self.config = {
            'threshold': 200,      # 触发转换的字符阈值
            'file_prefix': '[记录]', # 文件前缀
            'retention': 30,       # 文件保留时间（秒）
            'max_size': 5000       # 最大支持处理字符数
        }
        
        # 创建临时目录
        self.temp_dir = os.path.join(tempfile.gettempdir(), "chat_logs")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def initialize(self):
        """异步初始化"""
        self.ap.logger.info(f"ChatLogger 加载成功 | 阈值:{self.config['threshold']}字符")

    @handler(GroupNormalMessageReceived, PersonNormalMessageReceived)
    async def handle_message(self, ctx: EventContext):
        """处理消息接收事件"""
        try:
            # 获取消息内容
            message = ctx.event.text_message.strip()
            
            # 长度检查
            if not self._should_convert(message):
                return
                
            # 生成聊天记录文件
            file_path = await self._generate_log_file(ctx, message)
            
            # 构造回复消息
            reply_msg = MessageChain([
                Plain("您发送的消息过长，已转为文件：\n"),
                File(file_path)
            ])
            
            # 发送并阻止默认回复
            ctx.prevent_default()
            await ctx.reply(reply_msg)
            
            # 安排清理任务
            asyncio.create_task(self._cleanup_file(file_path))
            
        except Exception as e:
            self.ap.logger.error(f"处理消息异常: {str(e)}", exc_info=True)
            await ctx.reply(MessageChain([Plain("消息处理失败，请稍后重试")]))

    def _should_convert(self, message: str) -> bool:
        """判断是否需要转换"""
        return len(message) >= self.config['threshold'] and len(message) <= self.config['max_size']

    async def _generate_log_file(self, ctx: EventContext, content: str) -> str:
        """生成日志文件"""
        try:
            # 构造文件名
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"{self.config['file_prefix']}{timestamp}.txt"
            file_path = os.path.join(self.temp_dir, filename)
            
            # 写入文件内容
            with open(file_path, 'w', encoding='utf-8') as f:
                # 基础信息
                f.write(f"=== 聊天记录 ===\n")
                f.write(f"生成时间: {time.ctime()}\n")
                
                # 上下文信息
                if isinstance(ctx.event, GroupNormalMessageReceived):
                    f.write(f"群组ID: {ctx.event.group_id}\n")
                    f.write(f"发送者ID: {ctx.event.sender_id}\n")
                else:
                    f.write(f"用户ID: {ctx.event.sender_id}\n")
                
                # 消息内容
                f.write("\n消息内容：\n")
                f.write(content)
            
            return file_path
            
        except IOError as e:
            self.ap.logger.error(f"文件写入失败: {str(e)}")
            raise RuntimeError("文件创建失败")

    async def _cleanup_file(self, file_path: str):
        """异步清理文件"""
        await asyncio.sleep(self.config['retention'])
        try:
            os.remove(file_path)
            self.ap.logger.debug(f"已清理文件: {os.path.basename(file_path)}")
        except Exception as e:
            self.ap.logger.warning(f"文件清理失败: {str(e)}")

    def __del__(self):
        """插件卸载时清理所有临时文件"""
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                os.remove(file_path)
            except:
                pass
        self.ap.logger.info("ChatLogger 已卸载")
