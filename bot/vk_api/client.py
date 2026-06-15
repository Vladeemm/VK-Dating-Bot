"""VK API клиент."""

import os
from dotenv import load_dotenv
import vk_api

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_VK_TOKEN = os.getenv('MY_VK_TOKEN')

vk_group_session = vk_api.VkApi(token=BOT_TOKEN)
vk_group_api = vk_group_session.get_api()

vk_user_session = vk_api.VkApi(token=MY_VK_TOKEN)
vk_user_api = vk_user_session.get_api()

# Alias for legacy use in vk_api modules.
vk = vk_user_api
vk_group = vk_group_api
