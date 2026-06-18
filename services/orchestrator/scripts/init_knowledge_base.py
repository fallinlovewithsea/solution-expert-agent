"""初始化知识库：从飞书文件夹拉取全部文档并构建物料库"""
import sys
sys.path.insert(0, "/app")

from app.material_libraries.loader import MaterialLibraryLoader

FOLDER_TOKEN = "EmcZfzpSul8rCcdhXvhcKpgWn7g"

if __name__ == "__main__":
    loader = MaterialLibraryLoader()
    print(f"开始从飞书文件夹拉取文档...")
    count = loader.load_all_from_feishu(FOLDER_TOKEN)
    print(f"知识库初始化完成，共处理 {count} 份文档")