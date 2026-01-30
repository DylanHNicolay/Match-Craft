import discord
from discord import app_commands
from discord.ext import commands
from utils.db import db
from utils.embedView import EmbedView

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def is_admin(self, member: discord.Member) -> bool:
        """Check if a member has an admin role."""
        try:
            admin_roles_records = await db.execute("SELECT role_id FROM administrative_roles")
            if not admin_roles_records:
                return False

            admin_role_ids = {record['role_id'] for record in admin_roles_records}
            member_role_ids = {role.id for role in member.roles}

            return not admin_role_ids.isdisjoint(member_role_ids)
        except Exception as e:
            print(f"An error occurred in is_admin check: {e}")
            return False

    admin = app_commands.Group(name="admin", description="Admin commands")

    @admin.command(name="define", description="Define an admin role.")
    async def define(self, interaction: discord.Interaction, role: discord.Role):
        """Define an admin role."""
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Only the server owner can use this command.", ephemeral=True)
            return
        
        try:
            # Check if the role already exists
            await db.connect()
            existing_role = await db.execute("SELECT * FROM administrative_roles WHERE role_id = $1", role.id)
            if existing_role:
                await interaction.response.send_message(f"Role {role.mention} is already an admin role.")
                return
            await interaction.response.send_message(f"Role {role.mention} has been added as an admin role.")
            await db.execute("INSERT INTO administrative_roles (role_id) VALUES ($1);", role.id)
            await db.close()
            await interaction.response.send_message(f"Role {role.mention} has been added as an admin role.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    #Remove the specified role from the pug admin whitelist
    @app_commands.command()
    async def removeadminrole(self, interaction: discord.Interaction, role: discord.Role):
        if(interaction.user.id == interaction.guild.owner_id):
            outMessage=role.name + " no longer has pug admin perms"
            try:
                await db.connect()
                await db.execute("DELETE FROM administrative_roles WHERE role_id = $1;",role.id)
                await db.close()
            except: 
                await interaction.response.send_message(view=EmbedView(myText="error removing {id} from the database".format(id=role.id)))
            await interaction.response.send_message(view=EmbedView(myText=outMessage))
        else:
            await interaction.response.send_message(view=EmbedView(myText="This command is reserved for administrators"))

    #display a message containing all the whitelisted roles for pug administration
    # TODO: Remake getAdminList logic here
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
