from http import HTTPStatus
from dashscope import ImageSynthesis
from app.config import settings


def generate_image_tool(product_description: str, style: str = "电商摄影") -> str:
    """使用通义万相生成产品图片。

    Args:
        product_description: 产品描述和期望的视觉效果
        style: 图片风格（电商摄影、极简、创意、3D渲染等）

    Returns:
        生成图片的 URL
    """
    prompt = f"{style}风格，{product_description}，高质量，商业摄影级画质"

    response = ImageSynthesis.call(
        api_key=settings.dashscope_api_key,
        model=settings.image_model,
        input={"prompt": prompt},
        parameters={
            "size": settings.image_size,
            "n": 1,
        },
    )

    if response.status_code == HTTPStatus.OK:
        return response.output.results[0].url
    else:
        raise RuntimeError(
            f"图片生成失败: status={response.status_code}, "
            f"code={response.code}, message={response.message}"
        )
