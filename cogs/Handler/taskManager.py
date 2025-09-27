import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import sqlite3
import asyncio
from datetime import datetime
from typing import Optional

class TaskManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        
    def init_db(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                isDone INTEGER DEFAULT 0,
                guild_id INTEGER NOT NULL
            )
        ''')
        
        # Create settings table for task channels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_settings (
                guild_id INTEGER PRIMARY KEY,
                task_channel_id INTEGER NOT NULL,
                embed_message_id INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

    @cooldown(1, 5, BucketType.user)
    @commands.command(name='set_task_channel')
    @commands.has_permissions(administrator=True)
    async def set_task_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the default channel for tasks"""
        if channel is None:
            channel = ctx.channel
            
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # Insert or update the task channel for this guild
        cursor.execute('''
            INSERT OR REPLACE INTO task_settings (guild_id, task_channel_id)
            VALUES (?, ?)
        ''', (ctx.guild.id, channel.id))
        
        conn.commit()
        conn.close()
        
        # Send initial embed message
        embed = self.create_task_embed(ctx.guild.id, page=1)
        message = await channel.send(embed=embed, view=TaskView(self, ctx.guild.id))
        
        # Update the embed message ID
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE task_settings 
            SET embed_message_id = ? 
            WHERE guild_id = ?
        ''', (message.id, ctx.guild.id))
        conn.commit()
        conn.close()
        
        await ctx.send(f"Task channel set to {channel.mention}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages in the task channel"""
        if message.author.bot:
            return
            
        # Check if message is in a task channel
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task_channel_id, embed_message_id 
            FROM task_settings 
            WHERE guild_id = ?
        ''', (message.guild.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and message.channel.id == result[0]:
            task_channel_id, embed_message_id = result
            
            # Save task to database
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task, author_id, author_name, guild_id)
                VALUES (?, ?, ?, ?)
            ''', (message.content, message.author.id, message.author.display_name, message.guild.id))
            conn.commit()
            conn.close()
            
            # Delete the user's message
            try:
                await message.delete()
            except discord.NotFound:
                pass
            
            # Update the embed
            await self.update_task_embed(message.guild.id, message.channel, embed_message_id)

    def get_tasks(self, guild_id: int, page: int = 1, per_page: int = 10):
        """Get tasks from database with pagination"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        
        cursor.execute('''
            SELECT id, task, author_name, date_created
            FROM tasks 
            WHERE guild_id = ? AND isDone = 0
            ORDER BY date_created ASC
            LIMIT ? OFFSET ?
        ''', (guild_id, per_page, offset))
        
        tasks = cursor.fetchall()
        
        # Get total count for pagination
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE guild_id = ? AND isDone = 0
        ''', (guild_id,))
        total_tasks = cursor.fetchone()[0]
        
        conn.close()
        
        return tasks, total_tasks

    def create_task_embed(self, guild_id: int, page: int = 1):
        """Create the task list embed"""
        tasks, total_tasks = self.get_tasks(guild_id, page)
        
        embed = discord.Embed(
            title="📋 Task List",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        if not tasks:
            embed.description = "No tasks available!"
            embed.set_footer(text=f"Page {page}")
            return embed
        
        task_list = ""
        per_page = 10
        start_queue = (page - 1) * per_page + 1
        
        for i, (task_id, task, author, date_created) in enumerate(tasks):
            queue_num = start_queue + i
            # Parse the date and format it
            date_obj = datetime.fromisoformat(date_created.replace('Z', '+00:00') if 'Z' in date_created else date_created)
            formatted_date = date_obj.strftime("%m/%d %H:%M")
            
            task_list += f"`{queue_num}.` **{task}** - {author} `({formatted_date})`\n"
        
        embed.description = task_list
        
        total_pages = (total_tasks + per_page - 1) // per_page
        embed.set_footer(text=f"Page {page}/{total_pages} • Total tasks: {total_tasks}")
        
        return embed

    async def update_task_embed(self, guild_id: int, channel: discord.TextChannel, embed_message_id: int):
        """Update the existing task embed"""
        try:
            message = await channel.fetch_message(embed_message_id)
            embed = self.create_task_embed(guild_id, page=1)
            view = TaskView(self, guild_id, page=1)
            await message.edit(embed=embed, view=view)
        except discord.NotFound:
            # If message not found, create a new one
            embed = self.create_task_embed(guild_id, page=1)
            message = await channel.send(embed=embed, view=TaskView(self, guild_id))
            
            # Update the embed message ID
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE task_settings 
                SET embed_message_id = ? 
                WHERE guild_id = ?
            ''', (message.id, guild_id))
            conn.commit()
            conn.close()

    def complete_task(self, guild_id: int, queue_number: int, page: int = 1):
        """Mark a task as completed (soft delete)"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # Get the actual task ID based on queue number and page
        per_page = 10
        offset = (page - 1) * per_page + (queue_number - 1)
        
        cursor.execute('''
            SELECT id FROM tasks 
            WHERE guild_id = ? AND isDone = 0
            ORDER BY date_created ASC
            LIMIT 1 OFFSET ?
        ''', (guild_id, offset))
        
        result = cursor.fetchone()
        if result:
            task_id = result[0]
            cursor.execute('''
                UPDATE tasks 
                SET isDone = 1 
                WHERE id = ?
            ''', (task_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False

class TaskView(discord.ui.View):
    def __init__(self, task_manager, guild_id: int, page: int = 1):
        super().__init__(timeout=None)
        self.task_manager = task_manager
        self.guild_id = guild_id
        self.page = page
        self.setup_buttons()
    
    def setup_buttons(self):
        """Setup navigation and task completion buttons"""
        self.clear_items()
        
        # Get total tasks for pagination
        _, total_tasks = self.task_manager.get_tasks(self.guild_id, self.page)
        per_page = 10
        total_pages = (total_tasks + per_page - 1) // per_page if total_tasks > 0 else 1
        
        # Navigation buttons
        if total_pages > 1:
            # First page button
            if self.page > 1:
                first_btn = discord.ui.Button(emoji="⏪", style=discord.ButtonStyle.secondary)
                first_btn.callback = self.first_page
                self.add_item(first_btn)
                
                prev_btn = discord.ui.Button(emoji="◀️", style=discord.ButtonStyle.secondary)
                prev_btn.callback = self.prev_page
                self.add_item(prev_btn)
            
            # Next/Last page buttons
            if self.page < total_pages:
                next_btn = discord.ui.Button(emoji="▶️", style=discord.ButtonStyle.secondary)
                next_btn.callback = self.next_page
                self.add_item(next_btn)
                
                last_btn = discord.ui.Button(emoji="⏩", style=discord.ButtonStyle.secondary)
                last_btn.callback = self.last_page
                self.add_item(last_btn)
        
        # Task completion buttons (1-10 or dynamic based on page)
        tasks, _ = self.task_manager.get_tasks(self.guild_id, self.page)
        for i in range(min(len(tasks), 10)):
            btn = discord.ui.Button(
                label=str(i + 1),
                style=discord.ButtonStyle.success,
                row=2 + i // 5  # Distribute across rows
            )
            btn.callback = self.create_complete_callback(i + 1)
            self.add_item(btn)
    
    def create_complete_callback(self, task_num):
        async def complete_callback(interaction):
            success = self.task_manager.complete_task(self.guild_id, task_num, self.page)
            if success:
                # Update the embed
                embed = self.task_manager.create_task_embed(self.guild_id, self.page)
                self.setup_buttons()  # Refresh buttons
                await interaction.response.edit_message(embed=embed, view=self)
                
                # Send ephemeral confirmation
                await interaction.followup.send(f"Task #{task_num} completed!", ephemeral=True)
            else:
                await interaction.response.send_message("Task not found!", ephemeral=True)
        return complete_callback
    
    async def first_page(self, interaction):
        self.page = 1
        embed = self.task_manager.create_task_embed(self.guild_id, self.page)
        self.setup_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def prev_page(self, interaction):
        if self.page > 1:
            self.page -= 1
            embed = self.task_manager.create_task_embed(self.guild_id, self.page)
            self.setup_buttons()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction):
        _, total_tasks = self.task_manager.get_tasks(self.guild_id, self.page)
        total_pages = (total_tasks + 9) // 10  # 10 tasks per page
        if self.page < total_pages:
            self.page += 1
            embed = self.task_manager.create_task_embed(self.guild_id, self.page)
            self.setup_buttons()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def last_page(self, interaction):
        _, total_tasks = self.task_manager.get_tasks(self.guild_id, self.page)
        total_pages = (total_tasks + 9) // 10
        self.page = max(total_pages, 1)
        embed = self.task_manager.create_task_embed(self.guild_id, self.page)
        self.setup_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(TaskManager(bot))