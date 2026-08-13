"""集中读取环境变量。名称需与 Bot Framework 约定一致。"""
import os

from dotenv import load_dotenv

_DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_DOTENV_PATH)


class DefaultConfig:
    """Bot 运行配置。属性名 APP_ID/APP_PASSWORD/APP_TYPE/APP_TENANTID 是
    ConfigurationBotFrameworkAuthentication 识别的标准键。"""

    PORT = int(os.environ.get("PORT", 3978))

    # --- Teams / Bot Framework ---
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")

    # --- Azure OpenAI (brain) ---
    AOAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    AOAI_MODEL = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4.1")
    AOAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01")
    AOAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")

    # --- Azure AI Foundry (brain_maf) ---
    FOUNDRY_PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
    FOUNDRY_TENANT_ID = os.environ.get("FOUNDRY_TENANT_ID", "")
    FOUNDRY_CLIENT_ID = os.environ.get("FOUNDRY_CLIENT_ID", "")
    FOUNDRY_CLIENT_SECRET = os.environ.get("FOUNDRY_CLIENT_SECRET", "")
