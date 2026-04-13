from fastmcp import FastMCP
# 把 mcp 实例提前导出，方便内部模块直接调用
from app.tools.copywriting import generate_copywriting_tool
from app.tools.image import generate_image_tool


def create_mcp_server() -> FastMCP:
    mcp = FastMCP(
        name="ecommerce-agent",
        instructions="电商文案生成与图片生成工具集",
    )

    @mcp.tool()
    def generate_copywriting(product_info: str, style: str = "专业", platform: str = "通用") -> str:
        """生成电商产品文案。

        Args:
            product_info: 产品信息，包括名称、特点、目标受众等
            style: 文案风格（专业、活泼、文艺、幽默等）
            platform: 目标平台（淘宝、小红书、抖音、京东、通用）

        Returns:
            生成的电商文案文本
        """
        return generate_copywriting_tool(product_info, style, platform)

    @mcp.tool()
    def generate_image(product_description: str, style: str = "电商摄影") -> str:
        """使用通义万相 AI 生成产品图片。

        Args:
            product_description: 产品描述和期望的视觉效果
            style: 图片风格（电商摄影、极简、创意、3D渲染等）

        Returns:
            生成图片的 URL 地址
        """
        return generate_image_tool(product_description, style)

    return mcp


# 全局单例
mcp = create_mcp_server()
